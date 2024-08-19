# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta

def execute(filters=None):
    columns, data = [], []

    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 200},
        {"label": _("Total Monthly Effort Hours"), "fieldname": "total_monthly_effort_hours", "fieldtype": "Float", "width": 200},
        # {"label": _("Total Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 200},
        {"label": _("Revenue Per Hour"), "fieldname": "revenue_per_hour", "fieldtype": "Currency", "width": 200},
    ]

    data, html_card = get_data(filters)

    return columns, data, html_card

def get_data(filters):
    data = []
    html_card = ''
    
    if filters.get("customer_id") and filters.get("fy"):
        customer_id = filters.get("customer_id")
        fy = filters.get("fy")
    else:
        return data

    month_fy = get_month_dates_for_fiscal_year(fy)
    monthly_billing = 0.00
    
    for month in month_fy:
        resp_get_monthly_revenue = get_monthly_revenue(customer_id, month_fy[month][0], month_fy[month][1])
        monthly_hour_spent = resp_get_monthly_revenue["monthly_hour_spent"]
        monthly_billing = resp_get_monthly_revenue["monthly_billing"]
        revenue_per_hour = resp_get_monthly_revenue["revenue_per_hour"]
        
        data.append({
            "month": month,
            "total_monthly_effort_hours": monthly_hour_spent,
            "revenue": monthly_billing,
            "revenue_per_hour": revenue_per_hour,
        })
        
    customer_doc = frappe.get_doc("Customer",customer_id)

    html_card = f"""  
    <div class="frappe-card">
    <div class="frappe-card-head">
        <h5><strong>Customer Summary</strong></h5>
        <span class="caret"></span>
    </div>
    <div class="frappe-card-body" id="executive-content">
        <table class="table table-bordered" style="border-color: #4a4a4a;">
            <thead>
                <tr ><th style="border:1px solid #A9A9A9;width: 350px;">CID:</th><th style="border:1px solid #A9A9A9;">{customer_id}</th></tr>
                <tr ><th style="border:1px solid #A9A9A9;">Customer Name:</th><th style="border:1px solid #A9A9A9;">{customer_doc.customer_name}</th></tr>
                <tr ><th style="border:1px solid #A9A9A9;">Total Billing:</th><th style="border:1px solid #A9A9A9;">{monthly_billing}</th></tr>
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

def get_month_dates_for_fiscal_year(fiscal_year):
    month_fy = {}
    
    # Split the fiscal year into start and end years
    start_year, end_year = map(int, fiscal_year.split('-'))
    
    # Fiscal year starts in April of the start year and ends in March of the end year
    fiscal_year_start = datetime(start_year, 4, 1)
    fiscal_year_end = datetime(end_year, 3, 31)

    current_date = fiscal_year_start

    while current_date <= fiscal_year_end:
        month_name = current_date.strftime("%B")
        start_date = current_date.replace(day=1)
        if current_date.month == 12:
            end_date = current_date.replace(day=31)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)
            end_date = next_month - timedelta(days=1)

        month_fy[month_name] = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        current_date = end_date + timedelta(days=1)
    
    return month_fy




def get_monthly_revenue(customer_id, from_date, to_date, emp_id=None):
    monthly_billing = 0.00
    monthly_minutes_spent = 0
    employee_monthly_minutes_spent = 0
    service_master_file_list = []

    # Fetch the services
    services = frappe.get_all("Customer Chargeable Doctypes", fields=["name", "doctype_name"])

    # Loop through each service to get the current recurring fees
    for service in services:
        service_query = f"""
            SELECT name, current_recurring_fees
            FROM `tab{service['doctype_name']}`
            WHERE customer_id = %s AND frequency = 'M'
        """
        service_files = frappe.db.sql(service_query, (customer_id,), as_dict=True)
        
        for service_file in service_files:
            monthly_billing += service_file.current_recurring_fees
            service_master_file_list.append(service_file.name)
    
    # Fetch timesheet list using SQL
    timesheet_filter_query = """
        SELECT employee, name
        FROM `tabTeam Timesheet`
        WHERE date BETWEEN %s AND %s AND docstatus = 1
    """
    timesheet_list = frappe.db.sql(timesheet_filter_query, (from_date, to_date), as_dict=True)
    
    if emp_id:
        employee_timesheet_list = [i.name for i in timesheet_list if i.employee == emp_id]
    else:
        employee_timesheet_list = []
    
    timesheet_list = [i.name for i in timesheet_list]

    if timesheet_list and service_master_file_list:
        # Fetch timesheet logged records using SQL
        timesheet_logged_query = """
            SELECT time, parent
            FROM `tabCustom Timesheet Detail`
            WHERE customer_id = %s
            AND linked_file IN ({})
            AND parent IN ({})
        """.format(", ".join(["%s"] * len(service_master_file_list)), ", ".join(["%s"] * len(timesheet_list)))
        
        params = [customer_id] + service_master_file_list + timesheet_list
        timesheet_logged_records = frappe.db.sql(timesheet_logged_query, tuple(params), as_dict=True)
    else:
        timesheet_logged_records = []

    for record in timesheet_logged_records:
        monthly_minutes_spent += record['time']
        if emp_id and record['parent'] in employee_timesheet_list:
            employee_monthly_minutes_spent += record['time']

    monthly_hour_spent = round(monthly_minutes_spent / 60,2)
    employee_monthly_hour_spent = round(employee_monthly_minutes_spent / 60,2)
    revenue_per_hour = round(monthly_billing / monthly_hour_spent,2) if monthly_hour_spent else None
    
    return {
        "monthly_hour_spent": monthly_hour_spent,
        "monthly_billing": monthly_billing,
        "revenue_per_hour": revenue_per_hour,
        "employee_monthly_hour_spent": employee_monthly_hour_spent
    }




# def get_monthly_revenue(customer_id, from_date, to_date, emp_id=None):
#     monthly_billing = 0.00
#     monthly_minutes_spent = 0
#     employee_monthly_minutes_spent = 0
#     service_master_file_list = []
#     services = frappe.get_all("Customer Chargeable Doctypes", fields=["name", "doctype_name"])

#     for service in services:
#         service_files = frappe.get_all(service.name, 
#                                        filters={
#                                            "customer_id": customer_id, 
#                                            "frequency": "M"
#                                        }, 
#                                        fields=["name", "current_recurring_fees"])
        
#         for service_file in service_files:
#             monthly_billing += service_file.current_recurring_fees
#             service_master_file_list += [service_file.name]
        
#     timesheet_filter = {"date": ("between", [from_date, to_date]),"docstatus":1}
#     timesheet_list = frappe.get_all("Team Timesheet",
#                                     filters=timesheet_filter,
#                                     fields=["employee", "name"])
    
#     if emp_id:
#         employee_timesheet_list = [i.name for i in timesheet_list if i.employee == emp_id]
#     else:
#         employee_timesheet_list = []
    
#     timesheet_list = [i.name for i in timesheet_list]

#     timesheet_logged_records = frappe.get_all("Custom Timesheet Detail",
#                                               filters={
#                                                   "customer_id": customer_id,
#                                                   "linked_file": ("in", service_master_file_list),
#                                                   "parent": ("in", timesheet_list)
#                                               }, 
#                                               fields=["time", "parent"])
    
#     for record in timesheet_logged_records:
#         monthly_minutes_spent += record['time']
#         if emp_id and record['parent'] in employee_timesheet_list:
#             employee_monthly_minutes_spent += record['time']

#     monthly_hour_spent = round(monthly_minutes_spent / 60,2)
#     employee_monthly_hour_spent = round(employee_monthly_minutes_spent / 60,2)
#     revenue_per_hour = monthly_billing / monthly_hour_spent if monthly_hour_spent else None
    
#     return {
#         "monthly_hour_spent": monthly_hour_spent,
#         "monthly_billing": monthly_billing,
#         "revenue_per_hour": revenue_per_hour,
#         "employee_monthly_hour_spent": employee_monthly_hour_spent
#     }

