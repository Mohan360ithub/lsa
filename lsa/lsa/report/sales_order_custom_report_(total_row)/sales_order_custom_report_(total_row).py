import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns
        # {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},

        # {"label": "Doc Status", "fieldname": "doc_status", "fieldtype": "Select", "width": 100},
        {"label": "Payment Status", "fieldname": "custom_payment_status", "fieldtype": "HTML", "width": 80},
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 150, },
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 120, },
        # {"label": "Email", "fieldname": "custom_primary_email", "fieldtype": "Data", "width": 150, },
        
        # {"label": "SO Count", "fieldname": "so_count", "fieldtype": "Int", "width": 100}, #Faulty fix it

        {"label": "Next Follwup Date", "fieldname": "next_followup_date", "fieldtype": "Date", "width": 100},

        {"label": "SO Balance Amount", "fieldname": "custom_so_balance_amount", "fieldtype": "Currency", "width": 100},

        

        # {"label": "Customer Behaviour", "fieldname": "custom_customer_behaviour_", "fieldtype": "Data", "width": 80},
        # {"label": "Behaviour Note", "fieldname": "custom_behaviour_note", "fieldtype": "Data", "width": 100},
        # {"label": "SO Date", "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
        # {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 100},
        
        # {"label": "Grand Total", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
        # {"label": "Advance Paid", "fieldname": "advance_paid", "fieldtype": "Currency", "width": 100},
        {"label": "Followup Count", "fieldname": "custom_followup_count", "fieldtype": "Int", "width": 50},

        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 80},

        {"label": "FollowUp", "fieldname": "followup_button", "fieldtype": "HTML", "width": 50},

        {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "Data", "width": 100},


        {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 100},
        {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 100},

        # {"label": "PE Count", "fieldname": "custom_pe_counts", "fieldtype": "Int", "width": 50},
        # {"label": "PE IDs", "fieldname": "custom_pe_ids", "fieldtype": "Data", "width": 200},
    ]

    # Get data for the report
    data = get_data(filters)
    html_card = f"""
	<div style="width:100%;display: flex;justify-content: flex-end;align-items: center;">
    <button class="btn btn-sm " style="background-color:#A9A9A9;" onclick="window.location.href='http://online.lsaoffice.com/app/customer-followup/view/report'">
    <b style="color:#000000;" >Followups</b>
    </button>
    </div>
    """

    return columns, data, html_card

# Function to retrieve data based on filters

def get_data(filters):
    data = []
    doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    additional_filters = {}
    if filters:
        if filters.get("customer_id"):
            additional_filters["customer"] = filters.get("customer_id")
        if filters.get("doc_status"):
            status_list=filters.get("doc_status").split(',')
            status_list=[z.strip() for z in status_list if z.isalpha()]
            status_list=[doc_status_map_reverse[x] for x in status_list]
            additional_filters["docstatus"] = ["in", status_list]

    so_s = frappe.get_all("Sales Order",
                          filters=additional_filters,
                          fields=["name","customer","customer_name","contact_mobile","custom_so_from_date","custom_so_to_date",
                                  "transaction_date","rounded_total","docstatus","custom_followup_count"])
    
    op_fus=frappe.get_all("Customer Followup",
                          filters={"status":"Open"},
                          fields=["name","sales_order_summary"]
                          )
    op_fus={h.name:h.sales_order_summary.split(", ") for h in op_fus}
    op_fu_so={}
    for op_fu in op_fus:
        for so in op_fus[op_fu]:
            if so not in op_fu_so:
                op_fu_so[so]=op_fu
    # print(op_fu_so)
    customer_open_so={} 
    for sos in so_s:
        if sos["customer"] not in customer_open_so:
            # customer_open_so[sos["customer"]]=1   faulty fix it
            pass
        else:
            # customer_open_so[sos["customer"]]+=1    faulty fix it
            pass
    cu=[]
    for cu_so in so_s:
        if cu_so.customer not in cu:
            cu.append(cu_so.customer)

    cu_s = frappe.get_all("Customer",
                    #   filters={"name":["in", cu]},
                        fields=["name","custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
                                  "custom_customer_status_","custom_contact_person","custom_primary_mobile_no","custom_primary_email","disabled"])
    cu_l={}
    for cu in cu_s:
        cu_l[cu["name"]]={cu_i:cu[cu_i] for cu_i in cu if cu_i !="name"}
    cu_s=cu_l
    
    pe_s = frappe.get_all("Payment Entry Reference",
                             filters={"reference_doctype": "Sales Order","docstatus": 1},
                             fields=["name","reference_name", "parent", "allocated_amount"])
    pe_s_d={}
    for pe_i in pe_s:
        if pe_i["reference_name"] in pe_s_d:
            pe_s_d[pe_i["reference_name"]]+=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
        else:
            pe_s_d[pe_i["reference_name"]]=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]

    for so in so_s:
        doc_status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
        # so_doc = frappe.get_doc("Sales Order", so.name)
        # c_doc = frappe.get_doc("Customer", so.customer)
        data_row = {
            "so_id": so.name,
            "customer_id": so.customer,
            "customer_name": so.customer_name,
            
            "custom_contact_person": cu_s[so.customer]["custom_contact_person"],
            "mobile number": cu_s[so.customer]["custom_primary_mobile_no"],
            "custom_primary_email": cu_s[so.customer]["custom_primary_email"],

            "custom_customer_tags": cu_s[so.customer]["custom_customer_tags"],
            "custom_customer_behaviour_":cu_s[so.customer]["custom_customer_behaviour_"],
            "custom_behaviour_note": cu_s[so.customer]["custom_behaviour_note"],
            "custom_customer_status_": cu_s[so.customer]["custom_customer_status_"],

            "custom_so_from_date": so.custom_so_from_date,
            "custom_so_to_date": so.custom_so_to_date,
            "transaction_date": so.transaction_date,
            "rounded_total": so.rounded_total,
            "doc_status": doc_status_map[so.docstatus],
            "custom_followup_count": so.custom_followup_count,
        }

        custom_so_balance = so.rounded_total
        custom_advanced_paid = 0.00
        custom_pe_ids = []
        # pes = frappe.get_all("Payment Entry Reference",
        #                      filters={"reference_doctype": "Sales Order", "reference_name": so.name, "docstatus": 1},
        #                      fields=["name", "parent", "allocated_amount"])

        

        if so.name in pe_s_d:
            data_row["custom_pe_counts"] = len(pe_s_d[so.name])
            for pe in pe_s_d[so.name]:
                custom_so_balance = custom_so_balance - pe[2]
                custom_pe_ids.append(pe[1])
                custom_advanced_paid = custom_advanced_paid + pe[2]
        else:
            data_row["custom_pe_counts"] = 0

        data_row["custom_pe_ids"] = ",".join(custom_pe_ids)
        data_row["custom_so_balance_amount"] = custom_so_balance
        data_row["advance_paid"] = custom_advanced_paid

        if custom_so_balance == 0:
            # data_row["so_count"] =????0   faulty fix it
            # data_row["custom_payment_status"] = "Cleared"
            payment_status= "Cleared"
            data_row["custom_payment_status"] = f'''<a href="https://online.lsaoffice.com/app/sales-order/{so.name}">Cleared</a>'''
        elif custom_so_balance == so.rounded_total:
            # data_row["custom_payment_status"] = "Unpaid"
            payment_status= "Unpaid"
            data_row["custom_payment_status"] = f'''<a href="https://online.lsaoffice.com/app/sales-order/{so.name}">Unpaid</a>'''
            # data_row["so_count"] =????customer_open_so[so.customer]   faulty fix it
            if so.name not in op_fu_so:
                data_row["followup_button"] = f'''<a href="https://online.lsaoffice.com/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#BCBCBC; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
            else:
                data_row["followup_button"] = f'''<a href="https://online.lsaoffice.com/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#BCBCBC; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
        elif custom_so_balance > 0:
            # data_row["custom_payment_status"] = "Partially Paid"
            payment_status= "Partially Paid"
            data_row["custom_payment_status"] = f'''<a href="https://online.lsaoffice.com/app/sales-order/{so.name}">Partially Paid</a>'''
            # data_row["so_count"] =?????customer_open_so[so.customer]  faulty fix it
            if so.name not in op_fu_so:
                data_row["followup_button"] = f'''<a href="https://online.lsaoffice.com/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#BCBCBC; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
            else:
                data_row["followup_button"] = f'''<a href="https://online.lsaoffice.com/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#BCBCBC; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
        
        # print(data_row["custom_payment_status"])
        next_followup_date = ""
        if data_row["custom_payment_status"] != "Cleared":
            cu_fos = frappe.get_all("Customer Followup", filters={"customer_id": so.customer})
            
            if cu_fos:
                for cu_fo in cu_fos:
                    fo_doc = frappe.get_doc("Customer Followup", cu_fo.name)
                    if fo_doc.next_followup_date:
                        date_format = "%Y-%m-%d"
                        this_followup_date = datetime.strptime(str(fo_doc.next_followup_date), date_format).date()
                        if next_followup_date == "" or this_followup_date >= next_followup_date:
                            next_followup_date = this_followup_date
            data_row["next_followup_date"] = next_followup_date

        if filters.get("custom_payment_status"):
            if payment_status in filters.get("custom_payment_status") and cu_s[so.customer]["disabled"]==0:
                data += [data_row]
        else:
            data += [data_row]
    
    return data




