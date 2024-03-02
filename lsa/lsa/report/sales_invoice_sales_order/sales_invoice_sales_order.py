import frappe


# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        {"label": "Sales Invoice", "fieldname": "sales_invoice", "fieldtype": "Link","options": "Sales Invoice", "width": 200},
        # {"label": "Payment Entries Item", "fieldname": "payment_entry_ref", "fieldtype": "Data", "width": 100},
        {"label": "SI with SO", "fieldname": "status", "fieldtype": "Data", "width": 50},
        {"label": "Sales Order", "fieldname": "sales_order", "fieldtype": "Link","options": "Sales Order", "width": 250},

        
    ]

    # Get data for the report
    data = get_data(filters)


    return columns, data

# Function to retrieve data based on filters

def get_data(filters):
    data = []
    si_s = frappe.get_all("Sales Invoice",
                          filters={"docstatus":["not in",[2]]},
                          fields=["name"])

    for si in si_s:
        si_i = frappe.get_all("Sales Invoice Item",
                                          filters={"parent": si.name,
                                                   "sales_order":["not in",[None]],
                                                   "docstatus":["not in",[2]]},
											fields=["sales_order"],
												   )
        if si_i:
            data.append({
                "sales_invoice":si.name,
                "status":"Yes",
                "sales_order":si_i[0].sales_order,
				})
   
        else:
            data.append({
                "sales_invoice":si.name,
                "status":"No",
                "sales_order":None,
				})

    return data

