# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta
from lsa.lsa.report.customer_revenue_report.customer_revenue_report import get_monthly_revenue

def execute(filters=None):
    columns, data = [], []

    columns = [
        {"label": _("CID"), "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Contact Person"), "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 200},
        {"label": _("Primary Mobile No"), "fieldname": "custom_primary_mobile_no", "fieldtype": "Data", "width": 120},
        {"label": _("Employee Monthly Effort Hours"), "fieldname": "employee_monthly_hour_spent", "fieldtype": "Float", "width": 120},
        {"label": _("Revenue Per Hour"), "fieldname": "revenue_per_hour", "fieldtype": "Currency", "width": 120},
        {"label": _("Employee Revenue Per Month"), "fieldname": "employee_revenue_per_month", "fieldtype": "Currency", "width": 120},
    ]

    data, html_card = get_data(filters)

    return columns, data, html_card

def get_data(filters):
    data = []
    html_card = ''

    if filters.get("month") and filters.get("fy") and filters.get("employee_id"):
        month = filters.get("month")
        fy = filters.get("fy")
        employee_id = filters.get("employee_id")
    else:
        return data

    start_date, end_date = get_month_dates_for_fiscal_year(month, fy)
    
    customer_query = """
        SELECT name, customer_name, custom_contact_person, custom_primary_mobile_no
        FROM `tabCustomer`
        WHERE disabled = 0
    """
    customer_list = frappe.db.sql(customer_query, as_dict=True)
    
    employee_actual_total_revenue_for_the_month = 0.00
    for customer in customer_list:
        resp_get_monthly_revenue = get_monthly_revenue(customer.name, start_date, end_date, employee_id)
        monthly_hour_spent = resp_get_monthly_revenue["monthly_hour_spent"]
        monthly_billing = resp_get_monthly_revenue["monthly_billing"]
        revenue_per_hour = resp_get_monthly_revenue["revenue_per_hour"]
        employee_monthly_hour_spent = resp_get_monthly_revenue["employee_monthly_hour_spent"]
        employee_revenue_per_month = revenue_per_hour * employee_monthly_hour_spent if revenue_per_hour and employee_monthly_hour_spent else None
        if monthly_billing:
            data.append({
                "customer_id": customer.name,
                "customer_name": customer.customer_name,
                "custom_contact_person": customer.custom_contact_person,
                "custom_primary_mobile_no": customer.custom_primary_mobile_no,
                "employee_monthly_hour_spent": employee_monthly_hour_spent,
                "revenue": monthly_billing,
                "revenue_per_hour": revenue_per_hour,
                "employee_revenue_per_month": employee_revenue_per_month,
            })
        employee_actual_total_revenue_for_the_month += employee_revenue_per_month if employee_revenue_per_month else 0.00
    
    employee_doc = frappe.get_doc("Employee", employee_id)
    
    timesheet_query = """
        SELECT name, total_working_hours
        FROM `tabTeam Timesheet`
        WHERE employee = %s
        AND date BETWEEN %s AND %s
        AND docstatus = 1
    """
    current_month_timesheet_list = frappe.db.sql(timesheet_query, (employee_id, start_date, end_date), as_dict=True)
    
    total_monthly_hours_logged_in_timesheet = sum([j.total_working_hours for j in current_month_timesheet_list])
    
    current_month_timesheet_list = [j.name for j in current_month_timesheet_list]
    
    if current_month_timesheet_list:
        timesheet_logged_billable_query = """
            SELECT SUM(time) / 60 AS total_logged_billable_hours
            FROM `tabCustom Timesheet Detail`
            WHERE parent IN (%s)
            AND billable = 'Yes'
        """ % (", ".join(["%s"] * len(current_month_timesheet_list)))
        timesheet_logged_billable_records = frappe.db.sql(timesheet_logged_billable_query, tuple(current_month_timesheet_list), as_dict=True)
        total_logged_billable_hours = round(timesheet_logged_billable_records[0].total_logged_billable_hours,2) if timesheet_logged_billable_records else 0
    else:
        total_logged_billable_hours = 0
    
    x_factor = round(employee_actual_total_revenue_for_the_month / employee_doc.custom_monthly_salary,2)
    if x_factor >= 4:
        x_factor_color = "green"
    elif 3 <= x_factor < 4:
        x_factor_color = "yellow"
    elif 2 <= x_factor < 3:
        x_factor_color = "red"
    else:
        x_factor_color = "black"
    html_card = f"""
    <div class="frappe-card">
        <div class="frappe-card-head">
            <h5><strong>Employee Summary</strong></h5>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body" id="executive-content">
            <table class="table table-bordered">
                <thead>
                    <tr><th style="border:1px solid #A9A9A9;width: 350px;">Employee:</th><th style="border:1px solid #A9A9A9;">{employee_doc.employee_name}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Month:</th><th style="border:1px solid #A9A9A9;">{month}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">FY:</th><th style="border:1px solid #A9A9A9;">{fy}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Salary:</th><th style="border:1px solid #A9A9A9;">{employee_doc.custom_monthly_salary}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Total Monthly Hours Logged in Timesheet:</th><th style="border:1px solid #A9A9A9;">{round(total_monthly_hours_logged_in_timesheet,2)}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Timesheet Logged Billable Hours:</th><th style="border:1px solid #A9A9A9;">{round(total_logged_billable_hours)}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Timesheet Logged Non Billable Hours:</th><th style="border:1px solid #A9A9A9;">{round(total_monthly_hours_logged_in_timesheet - total_logged_billable_hours,2)}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Expected Revenue:</th><th style="border:1px solid #A9A9A9;">{employee_doc.custom_monthly_salary * 5}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Actual Revenue:</th><th style="border:1px solid #A9A9A9;">{round(employee_actual_total_revenue_for_the_month,2)}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">X Factor:</th><th style="border:1px solid #A9A9A9;color: {x_factor_color};">{x_factor}</th></tr>
                </thead>
                <tbody>
                    <!-- Rows will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>
    <script>
    document.addEventListener('click', function(event) {{
        // Check if the clicked element is a cell
        var clickedCell = event.target.closest('.dt-cell__content');
        if (clickedCell) {{
            // Remove highlight from previously highlighted cells
            var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
            previouslyHighlightedCells.forEach(function(cell) {{
                cell.classList.remove('highlighted-cell');
                cell.style.backgroundColor = ''; // Remove background color
                cell.style.border = ''; // Remove border
                cell.style.fontWeight = '';
            }});
            
            // Highlight the clicked row's cells
            var clickedRow = event.target.closest('.dt-row');
            var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
            cellsInClickedRow.forEach(function(cell) {{
                cell.classList.add('highlighted-cell');
                cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
                cell.style.border = '2px solid #90c9e3'; // Border color
                cell.style.fontWeight = 'bold';
            }});
        }}
    }});
    </script>
    """
    
    return data, html_card

def get_month_dates_for_fiscal_year(month_name, fy):
    # Split the fiscal year into start and end years
    start_year, end_year = map(int, fy.split('-'))
    
    # Define the months in fiscal year order (April to March)
    fiscal_year_months = [
        "April", "May", "June", "July", "August", "September",
        "October", "November", "December", "January", "February", "March"
    ]
    
    # Determine if the month belongs to the starting year or the ending year
    if month_name in fiscal_year_months[:9]:  # April to December
        year = start_year
        month = fiscal_year_months.index(month_name) + 4  # April is month 4
    else:  # January to March
        year = end_year
        month = fiscal_year_months.index(month_name) - 8  # January is month 1
    
    # Get the first and last day of the month
    start_date = datetime(year, month, 1)
    if month == 12:  # December
        end_date = datetime(year, month, 31)
    else:
        next_month = datetime(year, month + 1, 1)
        end_date = next_month - timedelta(days=1)
    
    # Return the dates in the desired format
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


































# # Copyright (c) 2024, Mohan and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from datetime import datetime, timedelta
# from lsa.lsa.report.customer_revenue_report.customer_revenue_report import get_monthly_revenue

# def execute(filters=None):
#     columns, data = [], []

#     columns = [
#         {"label": _("CID"), "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
#         {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
#         {"label": _("Contact Person"), "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 100},
#         {"label": _("Primary Mobile No"), "fieldname": "custom_primary_mobile_no", "fieldtype": "Data", "width": 100},
#         {"label": _("Employee Monthly Effort Hours"), "fieldname": "employee_monthly_hour_spent", "fieldtype": "Float", "width": 120},
#         {"label": _("Revenue Per Hour"), "fieldname": "revenue_per_hour", "fieldtype": "Currency", "width": 120},
#         {"label": _("Employee Revenue Per Month"), "fieldname": "employee_revenue_per_month", "fieldtype": "Currency", "width": 120},
#     ]

#     data, html_card = get_data(filters)

#     return columns, data, html_card

# def get_data(filters):
#     data = []
#     html_card = ''

#     if filters.get("month") and filters.get("fy") and filters.get("employee_id"):
#         month = filters.get("month")
#         fy = filters.get("fy")
#         employee_id = filters.get("employee_id")
#     else:
#         return data

#     start_date, end_date = get_month_dates_for_fiscal_year(month, fy)
    
#     customer_list = frappe.get_all("Customer", filters={
#         "disabled": 0,
#     }, fields=["customer_name", "name", "custom_contact_person", "custom_primary_mobile_no"])
    
#     employee_actual_total_revenue_for_the_month = 0.00
#     for customer in customer_list:
#         resp_get_monthly_revenue = get_monthly_revenue(customer.name, start_date, end_date, employee_id)
#         monthly_hour_spent = resp_get_monthly_revenue["monthly_hour_spent"]
#         monthly_billing = resp_get_monthly_revenue["monthly_billing"]
#         revenue_per_hour = resp_get_monthly_revenue["revenue_per_hour"]
#         employee_monthly_hour_spent = resp_get_monthly_revenue["employee_monthly_hour_spent"]
#         employee_revenue_per_month = revenue_per_hour * employee_monthly_hour_spent if revenue_per_hour and employee_monthly_hour_spent else None
#         if monthly_billing:
#             data.append({
#                 "customer_id": customer.name,
#                 "customer_name": customer.customer_name,
#                 "custom_contact_person": customer.custom_contact_person,
#                 "custom_primary_mobile_no": customer.custom_primary_mobile_no,
#                 "employee_monthly_hour_spent": employee_monthly_hour_spent,
#                 "revenue": monthly_billing,
#                 "revenue_per_hour": revenue_per_hour,
#                 "employee_revenue_per_month": employee_revenue_per_month,
#             })
#         employee_actual_total_revenue_for_the_month += employee_revenue_per_month if employee_revenue_per_month else 0.00
    
#     employee_doc = frappe.get_doc("Employee", employee_id)
    
#     current_month_timesheet_list = frappe.get_all("Team Timesheet",
#         filters={
#             "employee": employee_id,
#             "date": ("between", [start_date, end_date]),
#             "docstatus": 1
#         },
#         fields=["name", "total_working_hours"]
#     )
    
#     total_monthly_hours_logged_in_timesheet = sum([j.total_working_hours for j in current_month_timesheet_list])
    
#     current_month_timesheet_list = [j.name for j in current_month_timesheet_list]
    
#     timesheet_logged_billable_records = frappe.get_all("Custom Timesheet Detail",
#         filters={
#             "parent": ("in", current_month_timesheet_list),
#             "billable": "Yes",
#         },
#         fields=["time", "parent"]
#     )
#     total_logged_billable_hours = round(sum(k.time for k in timesheet_logged_billable_records)/60,2)
    
#     html_card = f"""
#     <div class="frappe-card">
#         <div class="frappe-card-head">
#             <strong>Key-Value Pairs</strong>
#             <span class="caret"></span>
#         </div>
#         <div class="frappe-card-body" id="executive-content">
#             <table class="table table-bordered">
#                 <thead>
#                     <tr><th>Employee:</th><th>{employee_doc.employee_name}</th></tr>
#                     <tr><th>Month:</th><th>{month}</th></tr>
#                     <tr><th>FY:</th><th>{fy}</th></tr>
#                     <tr><th>Salary:</th><th>{employee_doc.custom_monthly_salary}</th></tr>
#                     <tr><th>Total Monthly Hours Logged in Timesheet:</th><th>{total_monthly_hours_logged_in_timesheet}</th></tr>
#                     <tr><th>Timesheet Logged Billable Hours:</th><th>{total_logged_billable_hours}</th></tr>
#                     <tr><th>Timesheet Logged Non Billable Hours:</th><th>{total_monthly_hours_logged_in_timesheet - total_logged_billable_hours}</th></tr>
#                     <tr><th>Expected Revenue:</th><th>{employee_doc.custom_monthly_salary * 5}</th></tr>
#                     <tr><th>Actual Revenue:</th><th>{employee_actual_total_revenue_for_the_month}</th></tr>
#                     <tr><th>X Factor:</th><th>{employee_actual_total_revenue_for_the_month / employee_doc.custom_monthly_salary}</th></tr>
#                 </thead>
#                 <tbody>
#                     <!-- Rows will be inserted here by JavaScript -->
#                 </tbody>
#             </table>
#         </div>
#     </div>
#     <script>
#     document.addEventListener('click', function(event) {{
#         // Check if the clicked element is a cell
#         var clickedCell = event.target.closest('.dt-cell__content');
#         if (clickedCell) {{
#             // Remove highlight from previously highlighted cells
#             var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
#             previouslyHighlightedCells.forEach(function(cell) {{
#                 cell.classList.remove('highlighted-cell');
#                 cell.style.backgroundColor = ''; // Remove background color
#                 cell.style.border = ''; // Remove border
#                 cell.style.fontWeight = '';
#             }});
            
#             // Highlight the clicked row's cells
#             var clickedRow = event.target.closest('.dt-row');
#             var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
#             cellsInClickedRow.forEach(function(cell) {{
#                 cell.classList.add('highlighted-cell');
#                 cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
#                 cell.style.border = '2px solid #90c9e3'; // Border color
#                 cell.style.fontWeight = 'bold';
#             }});
#         }}
#     }});
#     </script>
#     """
    
#     return data, html_card

# def get_month_dates_for_fiscal_year(month_name, fy):
#     # Split the fiscal year into start and end years
#     start_year, end_year = map(int, fy.split('-'))
    
#     # Define the months in fiscal year order (April to March)
#     fiscal_year_months = [
#         "April", "May", "June", "July", "August", "September",
#         "October", "November", "December", "January", "February", "March"
#     ]
    
#     # Determine if the month belongs to the starting year or the ending year
#     if month_name in fiscal_year_months[:9]:  # April to December
#         year = start_year
#         month = fiscal_year_months.index(month_name) + 4  # April is month 4
#     else:  # January to March
#         year = end_year
#         month = fiscal_year_months.index(month_name) - 8  # January is month 1
    
#     # Get the first and last day of the month
#     start_date = datetime(year, month, 1)
#     if month == 12:  # December
#         end_date = datetime(year, month, 31)
#     else:
#         next_month = datetime(year, month + 1, 1)
#         end_date = next_month - timedelta(days=1)
    
#     # Return the dates in the desired format
#     return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")





# #can you substitute frappe ORM with sql querry in this
