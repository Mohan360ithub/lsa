import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns

        {"label": "Payment Entry", "fieldname": "pe_id", "fieldtype": "Link", "options": "Payment Entry", "width": 100},
        # {"label": "Total Allocated Amount", "fieldname": "total_allocated_amount", "fieldtype": "Currency", "width": 100},
        # {"label": "Unallocated Amount", "fieldname": "unallocated_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Allocated Amount", "fieldname": "allocated_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Paid Amount", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Cheque/Reference No", "fieldname": "reference_no", "fieldtype": "Data", "width": 150},
        {"label": "Cheque/Reference Date", "fieldname": "reference_date", "fieldtype": "Date", "width": 100},
        {"label": "Account Paid To", "fieldname": "paid_to", "fieldtype": "Data","width": 150},
        {"label": "Mode of Payment", "fieldname": "mode_of_payment", "fieldtype": "Data","width": 100},
        {"label": "Sales Order", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        # {"label": "Status PE", "fieldname": "custom_payment_status", "fieldtype": "Select", "width": 60},

        {"label": "Payment Status", "fieldname": "payment_status", "fieldtype": "Data", "width": 80},
        {"label": "SI", "fieldname": "si_status", "fieldtype": "Data", "width": 50},

        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 90},
        {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 125},
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 110},

        {"label": "Total Amount", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
        # {"label": "Advance Paid", "fieldname": "advance_paid", "fieldtype": "Currency", "width": 100},

        # {"label": "SO Balance Amount", "fieldname": "custom_so_balance_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "HTML", "width": 80},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 65},
        {"label": "Customer Disabled", "fieldname": "custom_customer_disabled_", "fieldtype": "Data", "width": 50},

        {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 110},
        {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 110},

        {"label": "Sales Invoice", "fieldname": "si_id", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},




    ]

    # Get data for the report
    data = get_data(filters)
    html_card = f"""

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

    return columns, data, html_card


# Function to retrieve data based on filters
def get_data(filters):
    data = []
    doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    additional_filters = {}
    additional_filters_pe={"docstatus": 1}
    si_filter=""
    payment_status_filter=""
    if filters:
        if filters.get("customer_id"):
            additional_filters["customer"] = filters.get("customer_id")
        if filters.get("doc_status"):
            status_list=filters.get("doc_status").split(',')
            status_list=[z.strip() for z in status_list if z.isalpha()]
            status_list=[doc_status_map_reverse[x] for x in status_list]
            additional_filters["docstatus"] = ["in", status_list]
        if filters.get("from_date"):
            additional_filters["custom_so_from_date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            additional_filters["custom_so_to_date"] = ["<=", filters.get("to_date")]
        if filters.get("sales_invoice"):
            si_filter=filters.get("sales_invoice")
        if filters.get("custom_payment_status"):
            payment_status_filter=filters.get("custom_payment_status")

        if filters.get("mode_of_payment"):
                additional_filters_pe["mode_of_payment"]=filters.get("mode_of_payment")
        if filters.get("paid_to"):
                additional_filters_pe["paid_to"]=filters.get("paid_to")

    # additional_filters["customer"] = "20130301"

    # customer_filter={}
    # if filters.get("customer_enabled"):
    #     if filters.get("customer_enabled")=="Customer Enabled":
    #         customer_filter["disabled"] = 0
    #     elif filters.get("customer_enabled")=="Customer Disabled":
    #         customer_filter["disabled"] = 1
    

    so_s = frappe.get_all("Sales Order",
                          filters=additional_filters,
                          fields=["name","customer","customer_name","contact_mobile","custom_so_from_date","custom_so_to_date",
                                  "transaction_date","rounded_total","docstatus","custom_followup_count"])
    
    cu=[]
    for cu_so in so_s:
        if cu_so.customer not in cu:
            cu.append(cu_so.customer)

    cu_s = frappe.get_all("Customer",
                        #   filters=customer_filter,
                        fields=["name","custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
                                  "custom_customer_status_","custom_contact_person","custom_primary_mobile_no","custom_primary_email","disabled"])
    
    cu_l={}
    for cu in cu_s:
        cu_l[cu["name"]]={cu_i:cu[cu_i] for cu_i in cu if cu_i !="name"}
    # print(cu_l)
    cu_s=cu_l

    
    
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
    
    pe_s = frappe.get_all("Payment Entry Reference",
                           filters={"reference_doctype":("in", ["Sales Order","Sales Invoice"]),"docstatus": 1},
                           fields=["name","reference_name", "parent", "allocated_amount","reference_doctype"])
    pe_so_d={}
    pe_si_d={}
    for pe_i in pe_s:
        if pe_i["reference_doctype"] =="Sales Order":
            if pe_i["reference_name"] in pe_so_d:
                pe_so_d[pe_i["reference_name"]]+=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
            else:
                pe_so_d[pe_i["reference_name"]]=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
        elif pe_i["reference_doctype"] =="Sales Invoice":
            if pe_i["reference_name"] in pe_si_d:
                pe_si_d[pe_i["reference_name"]]+=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
            else:
                pe_si_d[pe_i["reference_name"]]=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]


    pe_p_s = frappe.get_all("Payment Entry",
                           filters=additional_filters_pe,
                           fields=["name","total_allocated_amount", "unallocated_amount","paid_to","paid_amount", "mode_of_payment","reference_no","reference_date"])
    pe_p_s_l={}
    for pe_p in pe_p_s:
        pe_p_s_l[pe_p["name"]]={pe_i:pe_p[pe_i] for pe_i in pe_p}
	
    # for so in so_s:
    for so in so_s:
        doc_status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
        # custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":" Not Approved","Not Approached SO":"Not Approached"}
        # if so.customer=="20130563":
        #     # print(so)
        #     pass
        if so.customer in cu_s:
            data_row = {
                "so_id": so.name,
                "customer_id": so.customer,
                "customer_name": so.customer_name,
                "custom_contact_person": cu_s[so.customer]["custom_contact_person"],
                "mobile number": cu_s[so.customer]["custom_primary_mobile_no"],
                # "custom_customer_tags": cu_s[so.customer]["custom_customer_tags"],
                "custom_customer_behaviour_":cu_s[so.customer]["custom_customer_behaviour_"],
                "custom_behaviour_note": cu_s[so.customer]["custom_behaviour_note"],
                "custom_customer_status_": cu_s[so.customer]["custom_customer_status_"],
                "custom_customer_disabled_": cu_s[so.customer]["disabled"],
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

            if so.name in pe_so_d:
                data_row["custom_pe_counts"] = len(pe_so_d[so.name])
                for pe in pe_so_d[so.name]:
                    custom_so_balance = custom_so_balance - pe[2]
                    custom_pe_ids.append(pe[1])
                    custom_advanced_paid = custom_advanced_paid + pe[2]
            else:
                data_row["custom_pe_counts"] = 0
            
            custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":"Not Approved","Not Approached SO":"Not Approached"}
            if cu_s[so.customer]["custom_customer_tags"]=="SO Approved":
                data_row["custom_customer_tags"]=f'''<p style="color:Green;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            elif cu_s[so.customer]["custom_customer_tags"]=="SO Not Approved":
                data_row["custom_customer_tags"]=f'''<p style="color:Red;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            elif cu_s[so.customer]["custom_customer_tags"]=="Not Approached SO":
                data_row["custom_customer_tags"]=f'''<p style="color:Orange;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            
            data_row["custom_pe_ids"] = ",".join(custom_pe_ids)
            
            data_row["custom_so_balance_amount"] = custom_so_balance
            data_row["advance_paid"] = custom_advanced_paid

            if custom_so_balance == 0:
                payment_status= "Cleared"
                data_row["custom_payment_status"] = f'''<a href="http://lsa.local:8009/app/sales-order/{so.name}" style="color:Green;" >Cleared</a>'''
                data_row["followup_button"] = f'''<p>({so.custom_followup_count})</p>'''
                data_row["so_id"] = so.name
                data_row["si_status"] = "No"
                data_row["payment_status"] = payment_status
                count=0
                if so.name in pe_so_d:
                    for pe in pe_so_d[so.name]:
                        # data_row_n=data_row.copy()
                        data_row_n=data_row
                        # print(pe_p_s_l[pe[1]]["name"],so.name)
                        if pe[1] in pe_p_s_l:
                            pe_child_parent=pe_p_s_l[pe[1]]
                            # print(pe_child_parent)
                            for pe_k in pe_child_parent:
                                data_row_n[pe_k] = pe_child_parent[pe_k]
                                # print(pe_k)
                            data_row_n["si_id"]=None
                            data_row_n["allocated_amount"]=pe[2]
                            data_row_n["pe_id"]=pe_child_parent["name"]
                            if (not si_filter or si_filter=="No") and (not payment_status_filter or "Cleared" in payment_status_filter):
                                data.append(data_row_n)
                                print(data_row_n)
                                count+=1
                # print("Count",count)
                # print(data)

            elif custom_so_balance == so.rounded_total:
                payment_status= "Unpaid"
                data_row["custom_payment_status"] = f'''<a href="http://lsa.local:8009/app/sales-order/{so.name}" style="color:Red;">Unpaid</a>'''
                if so.name not in op_fu_so:
                    data_row["followup_button"] = f'''<a href="http://lsa.local:8009/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button><span>({so.custom_followup_count})</span></a>'''
                else:
                    data_row["followup_button"] = f'''<a href="http://lsa.local:8009/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button><span>({so.custom_followup_count})</span></a>'''
            elif custom_so_balance > 0:
                payment_status= "Partially Paid"
                data_row["so_id"] = so.name
                data_row["si_status"] = "No"
                data_row["payment_status"] = payment_status
                # print(data_row)
                count=0
                if so.name in pe_so_d:
                    for pe in pe_so_d[so.name]:
                        data_row_n=data_row.copy()
                        if pe[1] in pe_p_s_l:
                            pe_child_parent=pe_p_s_l[pe[1]]
                            for pe_k in pe_child_parent:
                                data_row_n[pe_k] = pe_child_parent[pe_k]
                            data_row_n["si_id"]=None
                            data_row_n["allocated_amount"]=pe[2]
                            data_row_n["pe_id"]=pe_child_parent["name"]
                            
                            if (not si_filter or si_filter=="No") and (not payment_status_filter or "Partially Paid" in payment_status_filter):
                                data.append(data_row_n)
                                count+=1
                                # pass
                # print("Count",count)
                data_row["custom_payment_status"] = f'''<a href="http://lsa.local:8009/app/sales-order/{so.name}" style="color:#b34700;" >Partially Paid</a>'''
                if so.name not in op_fu_so:
                    data_row["followup_button"] = f'''<a href="http://lsa.local:8009/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button><span>({so.custom_followup_count})</span></a>'''
                else:
                    data_row["followup_button"] = f'''<a href="http://lsa.local:8009/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button><span>({so.custom_followup_count})</span></a>'''
            
            si_advanced_paid = 0.0
            custom_so_balance_amount_si=custom_so_balance
            custom_si_ids = []

            if custom_so_balance_amount_si>0:
                si_item_s = frappe.get_all("Sales Invoice Item",
                                    filters={"sales_order": so.name,"docstatus": 1},
                                    fields=["name", "parent", "net_amount"])
                
                si_s=[]
                si_s=set([x.parent for x in si_item_s if x.parent not in si_s])
                si_s=list(si_s)
                # print(si_s)
                if si_s:
                    for si in si_s:
                        if si in pe_si_d:
                            for pe in pe_si_d[si]:
                                data_row_n=data_row.copy()
                                # print(pe)
                                if pe[1] in pe_p_s_l:
                                    pe_child_parent=pe_p_s_l[pe[1]]
                                    for pe_k in pe_child_parent:
                                        data_row_n[pe_k] = pe_child_parent[pe_k]
                                    data_row_n["si_id"]=si
                                    data_row_n["allocated_amount"]=pe[2]
                                    data_row_n["si_status"]="Yes"
                                    data_row_n["pe_id"]=pe_child_parent["name"]
                                    if not si_filter or si_filter=="Yes":
                                        data.append(data_row_n)
                        



            # customer_filter=[0,1]
            # if filters.get("customer_enabled"):
            #     if filters.get("customer_enabled")=="Customer Enabled":
            #         customer_filter=[0]
            #     elif filters.get("customer_enabled")=="Customer Disabled":
            #         customer_filter=[1]

            # if filters.get("custom_payment_status"):
            #     # if payment_status in filters.get("custom_payment_status") and cu_s[so.customer]["disabled"] in customer_filter:
            #     if payment_status in ["Cleared"] and cu_s[so.customer]["disabled"] in customer_filter:
            #         if filters.get("sales_invoice"):
            #             if filters.get("sales_invoice") =="Yes" and data_row["si_status"] == "Yes":
            #                 data += [data_row]
            #             elif filters.get("sales_invoice") =="No" and data_row["si_status"] == "No":
            #                 data += [data_row]
            #         else:
            #             data += [data_row]
            # else:
            #     data += [data_row]
    # print(data)
    return data




