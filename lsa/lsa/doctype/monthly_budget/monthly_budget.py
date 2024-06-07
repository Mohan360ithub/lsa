# # Copyright (c) 2024, Mohan and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MonthlyBudget(Document):
	pass



@frappe.whitelist()
def get_sales_orders_for_month(month, year):
    from datetime import datetime
    import calendar

    # Convert month name to month number
    month_number = list(calendar.month_name).index(month)
    
    # Create start and end dates for the selected month
    start_date = datetime(int(year), month_number, 1)
    end_date = datetime(int(year), month_number, calendar.monthrange(int(year), month_number)[1])

    # Fetch Sales Orders for the selected month
    sales_orders = frappe.db.sql("""
        SELECT name,transaction_date, total AS amount
        FROM `tabSales Order`
        WHERE docstatus = 1 AND transaction_date BETWEEN %s AND %s
    """, (start_date, end_date), as_dict=True)
    sales_invoices = frappe.db.sql("""
        SELECT name, posting_date, grand_total AS amount
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
    """, (start_date, end_date), as_dict=True)

    return {"sales_orders":sales_orders,"sales_invoices":sales_invoices}



# @frappe.whitelist()
# def get_sales_orders_and_invoices_for_month(month, year):
#     from datetime import datetime
#     import calendar

#     # Convert month name to month number
#     month_number = list(calendar.month_name).index(month)
    
#     # Create start and end dates for the selected month
#     start_date = datetime(int(year), month_number, 1)
#     end_date = datetime(int(year), month_number, calendar.monthrange(int(year), month_number)[1])

#     # Fetch Sales Orders and Sales Invoices for the selected month
#     sales_orders = frappe.db.sql("""
#         SELECT name, transaction_date, total AS amount
#         FROM `tabSales Order`
#         WHERE docstatus = 1 AND transaction_date BETWEEN %s AND %s
#     """, (start_date, end_date), as_dict=True)

#     sales_invoices = frappe.db.sql("""
#         SELECT name, posting_date, grand_total AS amount
#         FROM `tabSales Invoice`
#         WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
#     """, (start_date, end_date), as_dict=True)

#     records = []
#     records.extend(sales_orders)
#     records.extend(sales_invoices)

#     return records
