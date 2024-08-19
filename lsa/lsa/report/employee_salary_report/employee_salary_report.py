# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe,json,datetime,calendar
from datetime import timedelta,date
from lsa.custom_employee import get_employee_leave_data

def execute(filters=None):
    columns, data = [], []
     
    columns=[
        
        {"label": "Emp ID", "fieldname": "eid", "fieldtype": "Link", "options": "Employee", "width": 100, },
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 175, },


        {"label": "Net Payable Salary", "fieldname": "net_payable_salary", "fieldtype": "Currency", "width": 100, },
        
        {"label": "Bank Name", "fieldname": "bank_name", "fieldtype": "Data", "width": 150, },
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 90, },
        {"label": "Acc. No.", "fieldname": "acc_no", "fieldtype": "Data", "width": 150, },
        {"label": "IFSC", "fieldname": "ifsc", "fieldtype": "Data", "width": 120, },


        {"label": "Monthly Gross Salary", "fieldname": "monthly_salary", "fieldtype": "Currency", "width": 100, },
        
        {"label": "PT Deduction", "fieldname": "pt_deduction", "fieldtype": "Currency", "width": 100, },
        {"label": "Other Deductions", "fieldname": "other_deductions", "fieldtype": "Currency", "width": 100, "default":0.00},
        
        {"label": "Leave Without Pay", "fieldname": "lwp", "fieldtype": "Float", "width": 100, },


        {"label": "Absents", "fieldname": "absent_marked_days", "fieldtype": "Float", "width": 100, },
        {"label": "Absents Needs To Be Resolved", "fieldname": "absent_need_to_be_resolve", "fieldtype": "Data", "width": 300, },

        {"label": "Pending Leave Applications(Count)", "fieldname": "leave_applications_need_to_be_resolve_count", "fieldtype": "Int", "width": 100, },
        {"label": "Pending Leave Applications", "fieldname": "leave_applications_need_to_be_resolve", "fieldtype": "Data", "width": 300, },
        
        {"label": "Unmarked Days Count (Empty)", "fieldname": "not_marked_days", "fieldtype": "Float", "width": 100, },
        {"label": "Unmarked Days Dates (Empty)", "fieldname": "attendance_not_marked", "fieldtype": "Data", "width": 300, },
        


                # {"label": "Balance Leave Without Pay", "fieldname": "leave_without_pay", "fieldtype": "Float", "width": 100, },
        {"label": "CompOff Lv Bal", "fieldname": "compensatory_off", "fieldtype": "Float", "width": 100, },
        {"label": "Priv Lv Bal", "fieldname": "privilege_leave", "fieldtype": "Float", "width": 100, },
        {"label": "Sick Lv Bal", "fieldname": "sick_leave", "fieldtype": "Float", "width": 100, },
        {"label": "Spcl Lv Bal", "fieldname": "special_leave", "fieldtype": "Float", "width": 100, },

        {"label": "Consumed Leave Summary", "fieldname": "leave_summary", "fieldtype": "Data", "width": 300, },


        
    ]
     
    data,absent_data = employee_data(filters)
    html_card=str(absent_data)
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
    absent_data=None
    first_date, last_date = get_first_and_last_date_of_month(fy, mon)
    # print(first_date, last_date)
    mon_num=first_date.month
    year_num=first_date.year
    from_leave_date = datetime.datetime(year_num, 1, 1)
    absent_list = frappe.get_all("Attendance",
                                 filters={"status": "Absent","docstatus":1, "attendance_date": ("between", [first_date, last_date])},
                                 fields=["name", "employee_name"])

                        
    # print(absent_list)
    ab_emp = {}
    if absent_list:
        absent_msg = f"First resolve the Absent mark for {mon} of {fy}"
        
        for ab in absent_list:
            absent_msg += f"<br><a href='https://online.lsaoffice.com/app/attendance/{ab.name}'>{ab.name}</a> for {ab.employee_name}"
            if ab.employee_name not in ab_emp:
                ab_emp[ab.employee_name] = []
            ab_emp[ab.employee_name].append(ab.name)

        # frappe.msgprint(absent_msg)
        # return []
    # print("ab_emp",ab_emp)
    
    holiday_dicts = frappe.get_all("Holiday",filters={"holiday_date":("between",[first_date, last_date])},fields=("holiday_date",))
    holiday_dates = [str(holiday["holiday_date"])[-2:] for holiday in holiday_dicts]
    # print("holiday_dates",holiday_dates)

    working_dates = set()
    current_date = first_date
    while current_date <= last_date:
        current_day=str(current_date)[-2:]
        if current_day not in holiday_dates:
            working_dates.add(current_day)
        current_date += timedelta(days=1)
    # print("working_dates",working_dates)
    # absent_data=[working_dates]
    attendance_list = frappe.get_all("Attendance",
                                 filters={"docstatus":1, "attendance_date": ("between", [first_date, last_date])},
                                 fields=["name","attendance_date", "employee_name"])
    attendance_map = {}
    for attendance in attendance_list:
        if attendance["employee_name"] not in attendance_map:
            attendance_map[attendance["employee_name"]]={str(attendance["attendance_date"])[-2:]}
        else:
            attendance_map[attendance["employee_name"]].add(str(attendance["attendance_date"])[-2:])
    
    # print("attendance_map",attendance_map)
    # absent_data+=[attendance_map]
    emp_filter = {"status":"Active"}
    if filters.get("employee"):
        emp_filter["name"] = filters.get("employee")
    
    emp_list = frappe.get_all("Employee",
                              filters=emp_filter,
                              fields=["name", "employee_name", "ctc", "bank_name", "bank_ac_no", "ifsc_code",
                                        "company","designation","department"])

    leave_application_list = frappe.get_all("Leave Application",
                                            filters={
                                                # "leave_type": "Leave Without Pay",
                                                "status": "Approved",
                                                "docstatus": 1,
                                                "from_date": ("<=", last_date),
                                                "to_date": (">=", first_date)
                                            },
                                            fields=["name","leave_type", "employee", "total_leave_days", "from_date", "to_date","half_day"])
    
   
    leave_emp_map = {}
    emp_leave_summary={}
    for leave in leave_application_list:
        if leave.leave_type =="Leave Without Pay":
            if leave.employee not in leave_emp_map:
                # leave_for_month=leave_days_for_current_month(leave,first_date,last_date)
                # leave_emp_map[leave.employee] = leave_for_month
                leave_emp_map[leave.employee] = leave.total_leave_days
            else:
                # leave_for_month=leave_days_for_current_month(leave,first_date,last_date)
                # leave_emp_map[leave.employee] += leave_for_month
                leave_emp_map[leave.employee] += leave.total_leave_days

        leave_date_range=[" to ".join(set([str(leave.from_date.strftime("%d-%m-%Y")),str(leave.to_date.strftime("%d-%m-%Y"))]))]
        if leave.employee not in emp_leave_summary:
            emp_leave_summary[leave.employee] = {leave.leave_type :[leave.total_leave_days,leave_date_range]}
        else:
            if leave.leave_type not in emp_leave_summary[leave.employee]:
                emp_leave_summary[leave.employee][leave.leave_type] = [leave.total_leave_days,leave_date_range]
            else:
                emp_leave_summary[leave.employee][leave.leave_type][0] += leave.total_leave_days
                emp_leave_summary[leave.employee][leave.leave_type][1] +=leave_date_range
    absent_data=leave_emp_map
    pending_leave_application_list = frappe.get_all("Leave Application",
                                            filters={
                                                "docstatus": 0,
                                                "from_date": ("<=", last_date),
                                                "to_date": (">=", first_date)
                                            },
                                            fields=["name","employee",])
    pending_leave_application_dict={}
    for pe_la in pending_leave_application_list:
        if pe_la.employee not in pending_leave_application_dict:
            pending_leave_application_dict[pe_la.employee] = []
        pending_leave_application_dict[pe_la.employee] += [pe_la.name]


    # print(emp_leave_summary)
    data = []
    leave_data=get_employee_leave_data(emp_list,last_date,from_leave_date)
    emp_leave_bal={}
    for i in leave_data:
        if i.employee not in emp_leave_bal:
            emp_leave_bal[i.employee] = {i.leave_type:(i.leaves_allocated,i.leaves_taken)}
        else:
            emp_leave_bal[i.employee][i.leave_type]=(i.leaves_allocated,i.leaves_taken)
    # print("leave_emp_map",emp_leave_bal)

    for emp in emp_list:

        data_row = {
            "eid": emp.name,
            "employee_name": emp.employee_name,
            "bank_name": emp.bank_name,
            "acc_no": emp.bank_ac_no,
            "ifsc": emp.ifsc_code,
        }
        # print("data_row",data_row)
        not_marked_days=0
        absent_marked_days=0
        leave_types = ['Leave Without Pay', 'Compensatory Off',  'Privilege Leave', 'Sick Leave', 'Special Leave']
        for leave_type in leave_types:
            leavetypename="_".join([l.lower() for l in leave_type.split(' ')])
            # print(leavetypename)
            if emp.name in emp_leave_bal:
                if leave_type in emp_leave_bal[emp.name]:
                    data_row[leavetypename]=emp_leave_bal[emp.name][leave_type][0]-emp_leave_bal[emp.name][leave_type][1]
                else:
                    data_row[leavetypename]=0

            else:
                data_row[leavetypename]=0

        if emp.name in emp_leave_summary:
            summ_list=[f"{lv}({emp_leave_summary[emp.name][lv][0]})({', '.join(emp_leave_summary[emp.name][lv][1])})"for lv in emp_leave_summary[emp.name]]
            data_row["leave_summary"]=", \n".join(summ_list)


        

        if emp.employee_name not in attendance_map:
            continue

        should_skip_sal_calculation=False

        if emp.name in pending_leave_application_dict :
            data_row["monthly_salary"] = 0.00
            data_row["pt_deduction"] = 0.00
            data_row["other_deductions"] = 0.00
            data_row["lwp"] = 0
            data_row["net_payable_salary"] = 0
            data_row["leave_applications_need_to_be_resolve_count"]=len(pending_leave_application_dict[emp.name])
            data_row["leave_applications_need_to_be_resolve"]=", \n".join(pending_leave_application_dict[emp.name])
            # print("data_row_absent",data_row)
            should_skip_sal_calculation=True


        
        if emp.employee_name in ab_emp :
            data_row["monthly_salary"] = 0.00
            data_row["pt_deduction"] = 0.00
            data_row["other_deductions"] = 0.00
            data_row["lwp"] = 0
            data_row["net_payable_salary"] = 0
            data_row["absent_need_to_be_resolve"]=", \n".join(ab_emp[emp.employee_name])
            # print("data_row_absent",data_row)

            absent_marked_days=len(ab_emp[emp.employee_name])
            should_skip_sal_calculation=True


        if not working_dates.issubset(attendance_map[emp.employee_name]):
            data_row["monthly_salary"] = 0.00
            data_row["pt_deduction"] = 0.00
            data_row["other_deductions"] = 0.00
            data_row["lwp"] = 0
            data_row["net_payable_salary"] = 0
            not_marked_dates=working_dates-attendance_map[emp.employee_name]
            not_marked_dates_list=[i+"-"+str(mon_num)+"-"+str(year_num) for i in list(not_marked_dates)]
            data_row["attendance_not_marked"]=", \n".join(not_marked_dates_list)
            # print("data_row_no_marking",data_row)
            should_skip_sal_calculation=True
            not_marked_days=len(not_marked_dates)


        data_row["absent_marked_days"] = absent_marked_days
        data_row["not_marked_days"] = not_marked_days
        if should_skip_sal_calculation:
            data.append(data_row)
            continue

        monthly_salary = round(emp.ctc / 12)
        # net_payable_salary = round(emp.ctc / 12)
        pt_deduction = 0.00
        other_deductions = 0.00
        lwp = 0

        if monthly_salary >= 25000:
            pt_deduction = 200

        if emp.name in leave_emp_map:
            lwp = leave_emp_map[emp.name]

        # net_payable_salary = round((monthly_salary / 30) * (30 - lwp-absent_marked_days-not_marked_days) - (pt_deduction + other_deductions),0)
        net_payable_salary = round((monthly_salary / 30) * (30 - lwp) - (pt_deduction + other_deductions),0)


        data_row["monthly_salary"] = monthly_salary
        data_row["pt_deduction"] = pt_deduction
        data_row["other_deductions"] = other_deductions
        data_row["lwp"] = lwp
        
        data_row["net_payable_salary"] = net_payable_salary
        # print("data_row_complete",data_row)
        data.append(data_row)

    return data,absent_data


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
    first_date = date(year, month_number, 1)

    # Get the last date of the month
    last_date = date(year, month_number, calendar.monthrange(year, month_number)[1])

    return first_date, last_date


# def leave_days_for_current_month(leave_application,first_date,last_date):
#     from_date = leave_application.get("from_date")
#     to_date = leave_application.get("to_date")
    
#     # Calculate the number of leave days in the current month
#     leave_days_current_month = (min(to_date, last_date) - max(from_date, first_date)).days +1
    
#     if leave_application.half_day:
#         leave_days_current_month -=0.5

#     if leave_days_current_month < 0:
#         leave_days_current_month = 0
#     return leave_days_current_month


# def leave_days_for_current_month(leave_application, first_date, last_date):
#     from_date = leave_application.get("from_date")
#     to_date = leave_application.get("to_date")
    
#     # Ensure from_date and to_date are datetime objects
#     if isinstance(from_date, str):
#         from_date = datetime.strptime(from_date, '%Y-%m-%d')
#     if isinstance(to_date, str):
#         to_date = datetime.strptime(to_date, '%Y-%m-%d')
    
#     # Calculate the overlap period
#     overlap_start = max(from_date, first_date)
#     overlap_end = min(to_date, last_date)
    
#     if overlap_start > overlap_end:
#         leave_days_current_month = 0
#     else:
#         leave_days_current_month = (overlap_end - overlap_start).days + 1
    
#     if leave_application.get("half_day") and leave_days_current_month > 0:
#         leave_days_current_month -= 0.5

#     if leave_days_current_month < 0:
#         leave_days_current_month = 0
    
#     return leave_days_current_month






