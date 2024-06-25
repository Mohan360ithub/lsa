# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe,json,datetime,calendar

def execute(filters=None):
    columns, data = [], []
     
    columns=[
        
        {"label": "EID", "fieldname": "eid", "fieldtype": "Link", "options": "Employee", "width": 100, },
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 175, },
        {"label": "Monthly Salary", "fieldname": "monthly_salary", "fieldtype": "Currency", "width": 100, },
        
        {"label": "PT Deduction", "fieldname": "pt_deduction", "fieldtype": "Currency", "width": 100, },
        {"label": "Other Deductions", "fieldname": "other_deductions", "fieldtype": "Currency", "width": 100, "default":0.00},
        
        {"label": "Leave Without Pay", "fieldname": "lwp", "fieldtype": "Int", "width": 100, },
        {"label": "Net Payable Salary", "fieldname": "net_payable_salary", "fieldtype": "Currency", "width": 100, },
        
        {"label": "Bank Name", "fieldname": "bank_name", "fieldtype": "Data", "width": 150, },
        {"label": "Acc. No.", "fieldname": "acc_no", "fieldtype": "Data", "width": 150, },
        {"label": "IFSC", "fieldname": "ifsc", "fieldtype": "Data", "width": 120, },
        
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 90, },
        
    ]
     
    data = employee_data(filters)
    
    html_card = """

    <script>
        document.addEventListener('click', function(event) {
            // Check if the clicked element is a cell
            var clickedCell = event.target.closest('.dt-cell__content');
            if (clickedCell) {
                // Remove highlight from previously highlighted cells
                var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
                previouslyHighlightedCells.forEach(function(cell) {
                    cell.classList.remove('highlighted-cell');
                    cell.style.backgroundColor = ''; // Remove background color
                    cell.style.border = ''; // Remove border
                    cell.style.fontWeight = '';
                });
                
                // Highlight the clicked row's cells
                var clickedRow = event.target.closest('.dt-row');
                var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
                cellsInClickedRow.forEach(function(cell) {
                    cell.classList.add('highlighted-cell');
                    cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
                    cell.style.border = '2px solid #90c9e3'; // Border color
                    cell.style.fontWeight = 'bold';
                });
            }
        });
        
    </script>
    """

    return columns, data, html_card

	 
def employee_data(filters):
    fy = filters.get("fy")
    mon = filters.get("month")
    first_date, last_date = get_first_and_last_date_of_month(fy, mon)
    print(first_date, last_date)
    
    absent_list = frappe.get_all("Attendance",
                                 filters={"status": "Absent","docstatus":1, "attendance_date": ("between", [first_date, last_date])},
                                 fields=["name", "employee_name"])
    print(absent_list)

    if absent_list:
        absent_msg = f"First resolve the Absent mark for {mon} of {fy}"
        
        for ab in absent_list:
            absent_msg += f"<br><a href='http://lsa.local:8012/app/attendance/{ab.name}'>{ab.name}</a> for {ab.employee_name}"
        
        frappe.msgprint(absent_msg)

    emp_filter = {"status":"Active"}
    if filters.get("employee"):
        emp_filter["name"] = filters.get("employee")
    
    emp_list = frappe.get_all("Employee",
                              filters=emp_filter,
                              fields=["name", "employee_name", "ctc", "bank_name", "bank_ac_no", "ifsc_code"])

    leave_application_list = frappe.get_all("Leave Application",
                                            filters={
                                                "leave_type": "Leave Without Pay",
                                                "status": "Approved",
                                                "docstatus": 1,
                                                "from_date": ("<=", last_date),
                                                "to_date": (">=", first_date)
                                            },
                                            fields=["name", "employee", "total_leave_days", "from_date", "to_date"])

    leave_emp_map = {}
    for leave in leave_application_list:
        if leave.employee not in leave_emp_map:
            leave_for_month=leave_days_for_current_month(leave,first_date,last_date)
            leave_emp_map[leave.employee] = leave_for_month
        else:
            leave_for_month=leave_days_for_current_month(leave,first_date,last_date)
            leave_emp_map[leave.employee] += leave_for_month

    data = []


    for emp in emp_list:
        data_row = {
            "eid": emp.name,
            "employee_name": emp.employee_name,
            "bank_name": emp.bank_name,
            "acc_no": emp.bank_ac_no,
            "ifsc": emp.ifsc_code,
        }
          
        monthly_salary = emp.ctc / 12
        net_payable_salary = emp.ctc / 12
        pt_deduction = 0.00
        other_deductions = 0.00
        lwp = 0

        if monthly_salary >= 25000:
            pt_deduction = 200

        if emp.name in leave_emp_map:
            lwp = leave_emp_map[emp.name]
        net_payable_salary = (net_payable_salary / 30) * (30 - lwp) - (pt_deduction + other_deductions)

        data_row["monthly_salary"] = monthly_salary
        data_row["pt_deduction"] = pt_deduction
        data_row["other_deductions"] = other_deductions
        data_row["lwp"] = lwp
        data_row["net_payable_salary"] = net_payable_salary

        data.append(data_row)

    return data


def get_first_and_last_date_of_month(fy, mon):
    # Split the financial year into start and end years
    start_year, end_year = map(int, fy.split('-'))

    # Map month names to month numbers
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Get the month number
    month_number = months[mon]

    # Determine the actual year for the given month in the FY
    if month_number >= 4:  # April to December
        year = start_year
    else:  # January to March
        year = end_year

    # Get the first date of the month
    first_date = datetime.date(year, month_number, 1)

    # Get the last date of the month
    last_date = datetime.date(year, month_number, calendar.monthrange(year, month_number)[1])

    return first_date, last_date


def leave_days_for_current_month(leave_application,first_date,last_date):
    from_date = leave_application.get("from_date")
    to_date = leave_application.get("to_date")
    
    # Calculate the number of leave days in the current month
    leave_days_current_month = (min(to_date, last_date) - max(from_date, first_date)).days + 1
    if leave_days_current_month < 0:
        leave_days_current_month = 0
    return leave_days_current_month
