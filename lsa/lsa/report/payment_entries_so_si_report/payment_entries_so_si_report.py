import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        {"label": "Payment Entries", "fieldname": "payment_entry", "fieldtype": "Link","options": "Payment Entry", "width": 150},
        # {"label": "Payment Entries Item", "fieldname": "payment_entry_ref", "fieldtype": "Data", "width": 100},
        {"label": "PE Against", "fieldname": "payment_entry_ref_doctype", "fieldtype": "Data", "width": 100},
        {"label": "Reference Number", "fieldname": "payment_entry_ref_doctype_ref", "fieldtype": "HTML", "width": 175},

        # {"label": "Sales Invoice Item", "fieldname": "si_item", "fieldtype": "Data", "width": 100},
         {"label": "SO", "fieldname": "si_so", "fieldtype": "Data", "width": 50},
        {"label": "SO Number", "fieldname": "si_item_so", "fieldtype": "HTML", "width": 175},
        {"label": "Date", "fieldname": "reference_date", "fieldtype": "Data", "width": 120},
        {"label": "Customer ID", "fieldname": "party", "fieldtype": "Data", "width": 100},
        {"label": "Customer Name", "fieldname": "party_name", "fieldtype": "Data", "width": 150},
        {"label": "Amount", "fieldname": "paid_amount", "fieldtype": "Data", "width": 80},
        {"label": "Paid To", "fieldname": "paid_to", "fieldtype": "Data", "width": 150},
        {"label": "Ref. No.", "fieldname": "reference_no", "fieldtype": "Data", "width": 200},
        
    ]

    # Get data for the report
    data = get_data(filters)


    return columns, data

# Function to retrieve data based on filters

def get_data(filters):
    data = []
    pe_s = frappe.get_all("Payment Entry",
                          filters={"docstatus":1},
                          fields=["name","reference_date","reference_no","party","party_name","paid_to","paid_amount"])

    for pe in pe_s:
        per_s = frappe.get_all("Payment Entry Reference",
                               filters={"parent": pe.name,"docstatus":1},
                               fields=["name", "reference_doctype", "reference_name"])
        if per_s:
            for per in per_s:
                if per.reference_doctype == "Sales Order":
                    data.append({
                        "payment_entry": pe.name,
                        "payment_entry_ref": per.name,
                        "payment_entry_ref_doctype": per.reference_doctype,
                        "payment_entry_ref_doctype_ref": f'''<a href="https://online.lsaoffice.com/app/sales-order/{per.reference_name}">{per.reference_name}</a>''',
                        "si_item": "NA",
                        "si_so":"No",
                        "si_item_so": "NA",
                        "reference_date":pe.reference_date,
                        "reference_no":pe.reference_no,
                        "party":pe.party,
                        "party_name":pe.party_name,
                        "paid_to":pe.paid_to,
                        "paid_amount":pe.paid_amount,
                    })
                else:
                    si_s = frappe.get_all("Sales Invoice Item",
                                          filters={"parent": per.reference_name,
                                                   "sales_order":["not in",[None]],
                                                   "docstatus":["not in",[2]]},
                                          fields=["name", "sales_order"])
                    if si_s:
                        for si in si_s:
                            data.append({
                                "payment_entry": pe.name,
                                "payment_entry_ref": per.name,
                                "payment_entry_ref_doctype": per.reference_doctype,
                                "payment_entry_ref_doctype_ref": f'''<a href="https://online.lsaoffice.com/app/sales-invoice/{per.reference_name}">{per.reference_name}</a>''',
                                "si_item": si.name,
                                "si_so":"Yes",
                                "si_item_so": f'''<a href="https://online.lsaoffice.com/app/sales-order/{si.sales_order}">{si.sales_order}</a>''',
                            })
                    else:
                        data.append({
                            "payment_entry": pe.name,
                            "payment_entry_ref": per.name,
                            "payment_entry_ref_doctype": per.reference_doctype,
                            "payment_entry_ref_doctype_ref": f'''<a href="https://online.lsaoffice.com/app/sales-invoice/{per.reference_name}">{per.reference_name}</a>''',
                            "si_item": "NA",
                            "si_so":"No",
                            "si_item_so": "NA",
                        })
        else:
            data.append({
                "payment_entry": pe.name,
                "payment_entry_ref": "NA",
                "payment_entry_ref_doctype": "NA",
                "payment_entry_ref_doctype_ref": "NA",
                "si_item": "NA",
                "si_so":"No",
                "si_item_so": "NA",
            })

    return data


