import frappe
from frappe import _
from datetime import datetime, timedelta
from lsa.lsa.report.customer_revenue_report.customer_revenue_report import get_monthly_revenue

def execute(filters=None):
    columns, data = [], []

    columns = [
        {"label": _("CID"), "fieldname": "customer_id", "fieldtype": "Link","options":"Customer", "width": 100},
        {"label": _("Customer Name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Contact Person"), "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 200},
        {"label": _("Primary Mobile No"), "fieldname": "custom_primary_mobile_no", "fieldtype": "Data", "width": 120},
        {"label": _("Total Monthly Effort Hours"), "fieldname": "total_monthly_effort_hours", "fieldtype": "Float", "width": 120},
        {"label": _("Total Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": _("Revenue Per Hour"), "fieldname": "revenue_per_hour", "fieldtype": "Currency", "width": 120},
    ]

    data, html_card = get_data(filters)

    return columns, data, html_card

def get_data(filters):
    data = []
    html_card=''

    if filters.get("month") and filters.get("fy"):
        month = filters.get("month")
        fy = filters.get("fy")
    else:
        return data

    start_date, end_date = get_month_dates_for_fiscal_year(month, fy)
    
    # Fetch customer list using SQL
    customer_query = """
        SELECT name, customer_name, custom_contact_person, custom_primary_mobile_no
        FROM `tabCustomer`
        WHERE disabled = 0
    """
    customer_list = frappe.db.sql(customer_query, as_dict=True)

    total_cid_count = 0
    total_revenue_per_hour = 0.00
    total_revenue = 0.00
    
    for customer in customer_list:
        resp_get_monthly_revenue = get_monthly_revenue(customer.name, start_date, end_date)
        monthly_hour_spent = resp_get_monthly_revenue["monthly_hour_spent"]
        monthly_billing = resp_get_monthly_revenue["monthly_billing"]
        revenue_per_hour = resp_get_monthly_revenue["revenue_per_hour"]

        if monthly_billing:
            data.append({
                "customer_id": customer.name,
                "customer_name": customer.customer_name,
                "custom_contact_person": customer.custom_contact_person,
                "custom_primary_mobile_no": customer.custom_primary_mobile_no,
                "total_monthly_effort_hours": monthly_hour_spent,
                "revenue": monthly_billing,
                "revenue_per_hour": revenue_per_hour,
            })
            total_cid_count += 1
            total_revenue_per_hour += revenue_per_hour if revenue_per_hour else 0
            total_revenue += monthly_billing if monthly_billing else 0
    
    html_card = f"""  
    <div class="frappe-card">
        <div class="frappe-card-head" >
            <h5><strong>Month Summary</strong></h5>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body" id="executive-content">
            <table class="table table-bordered">
                <thead>
                    <tr><th style="border:1px solid #A9A9A9;width: 350px;">Total CID for Monthly Biling:</th><th style="border:1px solid #A9A9A9;">{total_cid_count}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Average Revenue Per Hour:</th><th style="border:1px solid #A9A9A9;">{round(total_revenue_per_hour / total_cid_count,2) if total_cid_count else 0}</th></tr>
                    <tr><th style="border:1px solid #A9A9A9;">Total Month Revenue:</th><th style="border:1px solid #A9A9A9;">{total_revenue}</th></tr>
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

