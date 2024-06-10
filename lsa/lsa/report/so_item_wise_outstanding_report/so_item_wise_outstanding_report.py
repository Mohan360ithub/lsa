import frappe
from datetime import datetime,timedelta
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns
        
        {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        # {"label": "SO Item ID", "fieldname": "item_id", "fieldtype": "Data", "width": 100},
        {"label": "SI", "fieldname": "si_status", "fieldtype": "Data", "width": 50},
        {"label": "SO Item", "fieldname": "item_code", "fieldtype": "Data", "width": 100},
        {"label": "Payment Status", "fieldname": "custom_payment_status", "fieldtype": "Select", "width": 100},
        {"label": "Item Total", "fieldname": "total_with_gst", "fieldtype": "Currency", "width": 100},
        {"label": "Item Balance", "fieldname": "item_balance", "fieldtype": "Currency", "width": 100},

        {"label": "Executive", "fieldname": "executive", "fieldtype": "Data", "width": 100},
        {"label": "Frequency", "fieldname": "frequency", "fieldtype": "Data", "width": 100},

        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 125},
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 110},

        {"label": "Total Amount", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
        {"label": "SO Advance Paid", "fieldname": "payment_recieved", "fieldtype": "Currency", "width": 100},
        {"label": "SO Payment Status", "fieldname": "so_payment_status", "fieldtype": "Select", "width": 100},
        {"label": "Payment Entry", "fieldname": "payment_entry", "fieldtype": "Data", "width": 100},
        {"label": "SO Unallocated Advance", "fieldname": "unallocated_amount_to_item", "fieldtype": "Currency", "width": 100},
        
        {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "HTML", "width": 100},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 100},
        {"label": "Customer Disabled", "fieldname": "custom_customer_disabled_", "fieldtype": "Data", "width": 100},
        

        {"label": "Doc Status", "fieldname": "doc_status", "fieldtype": "Select", "width": 100},
        {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 110},
        {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 110},
        {"label": "Sales Invoice", "fieldname": "custom_si_ids", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
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
    service_item=["GST Filling","TDS Filling","PT Filling","ROC Filling","Incometax Filing"]
    additional_filters = {}
    if filters:
        if filters.get("customer_id"):
            additional_filters["customer"] = filters.get("customer_id")
        # if filters.get("doc_status"):
        #     status_list=filters.get("doc_status").split(',')
        #     status_list=[z.strip() for z in status_list if z.isalpha()]
        #     status_list=[doc_status_map_reverse[x] for x in status_list]
        #     additional_filters["docstatus"] = ["in", status_list]
        
        
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        if from_date and to_date:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
            max_date_range = timedelta(days=365)

            if to_date_obj - from_date_obj > max_date_range:
                frappe.throw("Date range cannot exceed one year")
                return [],""

        additional_filters["custom_so_from_date"] = [">=", from_date]
        additional_filters["custom_so_to_date"] = ["<=", to_date]

    customer_filter={}
    if filters.get("customer_enabled"):
        if filters.get("customer_enabled")=="Customer Enabled":
            customer_filter["disabled"] = 0
        elif filters.get("customer_enabled")=="Customer Disabled":
            customer_filter["disabled"] = 1

    if filters.get("customer_tag"):
        customer_filter["custom_customer_tags"] = filters.get("customer_tag")

    if filters.get("service_type"):
        service_filter_item=filters.get("service_type")
    else:
        service_filter_item=["GST Filling","TDS Filling","PT Filling","ROC Filling","Incometax Filing"]
        

    cu_s = frappe.get_all("Customer",
                    filters=customer_filter,
                    fields=["name","custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
                                "custom_customer_status_","custom_contact_person","custom_primary_mobile_no","custom_primary_email","disabled"])

    cu_l={}
    for cu1 in cu_s:
        cu_l[cu1["name"]]={cu_i:cu1[cu_i] for cu_i in cu1 if cu_i !="name"}
    
    chargable_services=[ser.name for ser in frappe.get_all("Customer Chargeable Doctypes")]
    for ch_ser in chargable_services:
        services_executive=frappe.get_all(ch_ser,
                        # filters={"enabled":1},
                        fields=["name","customer_id","service_name","executive","frequency"])
        for ser_exe in services_executive:
            if ser_exe.customer_id in cu_l and ser_exe.service_name in cu_l[ser_exe.customer_id]:
                cu_l[ser_exe.customer_id][ser_exe.service_name]+=[(ser_exe.executive,ser_exe.frequency,ser_exe.name)]
            elif ser_exe.customer_id in cu_l:
                cu_l[ser_exe.customer_id][ser_exe.service_name]=[(ser_exe.executive,ser_exe.frequency,ser_exe.name)]

    

    so_s = frappe.get_all("Sales Order",
                          filters=additional_filters,
                          fields=["name","customer","customer_name","contact_mobile","custom_so_from_date","custom_so_to_date",
                                  "transaction_date","rounded_total","docstatus","custom_followup_count"])
    so_map={}
    for so1 in so_s:
        if so1.customer in cu_l:
            so_map[so1.name]={sof:so1[sof] for sof in so1}


    pe_s = frappe.get_all("Payment Entry Reference",
                           filters={"reference_doctype": "Sales Order","docstatus": 1},
                           fields=["name","reference_name", "parent", "allocated_amount"])


    for pe_i in pe_s:
        if pe_i.reference_name in so_map:
            if "payment_recieved" not in so_map[pe_i.reference_name]:
                so_map[pe_i.reference_name]["payment_recieved"] = pe_i.allocated_amount
                so_map[pe_i.reference_name]["unallocated_amount_to_item"] = pe_i.allocated_amount
                so_map[pe_i.reference_name]["payment_entry"] = pe_i.parent
            else:
                so_map[pe_i.reference_name]["payment_recieved"] += pe_i.allocated_amount
                so_map[pe_i.reference_name]["unallocated_amount_to_item"] += pe_i.allocated_amount
                so_map[pe_i.reference_name]["payment_entry"] += ", "+pe_i.parent

	
        
    
    
    for item in service_item:
        so_i = frappe.get_all("Sales Order Item",
                              filters={"docstatus": ("in", [0, 1]), "item_code": item},
                              fields=["name", "parent", "item_code", "net_amount", 
                                    #   "igst_amount", "cgst_amount","sgst_amount"
                                      ])
        for it in so_i:
            if it.parent in so_map:
                if "so_item_list" not in so_map[it.parent]:
                    so_map[it.parent]["so_item_list"]={}
                item_dict1 = {itf: it.itf for itf in it}
                # it_balance = it.net_amount + it.sgst_amount + it.cgst_amount + it.igst_amount
                it_balance = it.net_amount * 1.18
                item_dict1["total_with_gst"] = it_balance
                if it.item_code not in so_map[it.parent]["so_item_list"]:
                    if "unallocated_amount_to_item" in so_map[it.parent] and so_map[it.parent]["unallocated_amount_to_item"] > 0:
                        if so_map[it.parent]["unallocated_amount_to_item"] > it_balance:
                            so_map[it.parent]["unallocated_amount_to_item"] -= it_balance
                            item_dict1["item_balance"] = 0.00
                            so_map[it.parent]["so_item_list"][it.item_code] = [item_dict1]
                        else:
                            item_dict1["item_balance"] = it_balance - so_map[it.parent]["unallocated_amount_to_item"]
                            so_map[it.parent]["unallocated_amount_to_item"] = 0.00
                            so_map[it.parent]["so_item_list"][it.item_code] = [item_dict1]
                    else:
                        item_dict1["item_balance"] = it_balance
                        so_map[it.parent]["so_item_list"][it.item_code] = [item_dict1]
                else:
                    if "unallocated_amount_to_item" in so_map[it.parent] and so_map[it.parent]["unallocated_amount_to_item"] > 0:
                        if so_map[it.parent]["unallocated_amount_to_item"] > it_balance:
                            so_map[it.parent]["unallocated_amount_to_item"] -= it_balance
                            item_dict1["item_balance"] = 0.00
                            so_map[it.parent]["so_item_list"][it.item_code] += [item_dict1]
                        else:
                            item_dict1["item_balance"] = it_balance - so_map[it.parent]["unallocated_amount_to_item"]
                            so_map[it.parent]["unallocated_amount_to_item"] = 0.00
                            so_map[it.parent]["so_item_list"][it.item_code] += [item_dict1]
                    else:
                        item_dict1["item_balance"] = it_balance
                        so_map[it.parent]["so_item_list"][it.item_code] += [item_dict1]

    si_item_s = frappe.get_all("Sales Invoice Item",
                                    filters={"sales_order": ("not in",[None]),"docstatus": 1},
                                    fields=["name", "parent","sales_order"])
    so_si_map={si_item.sales_order:si_item.parent  for si_item in si_item_s}

    
	
    for so_i in so_map:
        doc_status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
        # custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":" Not Approved","Not Approached SO":"Not Approached"}
        # if so.customer=="20130563":
        #     # print(so)
        #     pass
        so=so_map[so_i]
        data_row = {
            "so_id": so["name"],
            "customer_id": so["customer"],
            "customer_name": so["customer_name"],
            "custom_contact_person": cu_l[so["customer"]]["custom_contact_person"],
            "mobile number": cu_l[so["customer"]]["custom_primary_mobile_no"],
            # "custom_customer_tags": cu_l[so.customer]["custom_customer_tags"],
            "custom_customer_behaviour_":cu_l[so["customer"]]["custom_customer_behaviour_"],
            "custom_behaviour_note": cu_l[so["customer"]]["custom_behaviour_note"],
            "custom_customer_status_": cu_l[so["customer"]]["custom_customer_status_"],
            "custom_customer_disabled_": cu_l[so["customer"]]["disabled"],
            "custom_so_from_date": so["custom_so_from_date"],
            "custom_so_to_date": so["custom_so_to_date"],
            "transaction_date": so["transaction_date"],
            "rounded_total": so["rounded_total"],
            "doc_status": doc_status_map[so["docstatus"]],
            "custom_followup_count": so["custom_followup_count"],
            "payment_recieved":so["payment_recieved"] if "payment_recieved" in so else 0.0,
            "payment_entry":so["payment_entry"] if "payment_entry" in so else 0.0,
            "unallocated_amount_to_item":so["unallocated_amount_to_item"] if "unallocated_amount_to_item" in so else 0.0,
        }

        if so_i in so_si_map:
            data_row["si_status"]="Yes"
            data_row["custom_si_ids"]=so_si_map[so_i]
            data+=[data_row]
            continue
        data_row["si_status"]="No"
        if "payment_recieved" in so and so["payment_recieved"] == so["rounded_total"]:
            payment_status= "Cleared"
            data_row["so_payment_status"] = f'''<p style="color:Green;" >Cleared</p>'''
        elif "payment_recieved" in so and so["payment_recieved"] > 0:
            payment_status= "Partially Paid"
            data_row["so_payment_status"] = f'''<p style="color:#b34700;" >Partially Paid</p>'''
        else:
            payment_status= "Unpaid"
            data_row["so_payment_status"] = f'''<p style="color:Red;">Unpaid</p>'''


        custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":"Not Approved","Not Approached SO":"Not Approached"}
        if cu_l[so["customer"]]["custom_customer_tags"]=="SO Approved":
            data_row["custom_customer_tags"]=f'''<p style="color:Green;">{custom_customer_tags_small[cu_l[so["customer"]]["custom_customer_tags"]]}</p>'''
        elif cu_l[so["customer"]]["custom_customer_tags"]=="SO Not Approved":
            data_row["custom_customer_tags"]=f'''<p style="color:Red;">{custom_customer_tags_small[cu_l[so["customer"]]["custom_customer_tags"]]}</p>'''
        elif cu_l[so["customer"]]["custom_customer_tags"]=="Not Approached SO":
            data_row["custom_customer_tags"]=f'''<p style="color:Orange;">{custom_customer_tags_small[cu_l[so["customer"]]["custom_customer_tags"]]}</p>'''
        
        if "so_item_list" in so:
            for item in so["so_item_list"]:
                if item in service_filter_item:
                    for item_instance in so["so_item_list"][item]:
                        data_row_item=data_row.copy()
                        data_row_item["item_code"]=item
                        

                        data_row_item["item_id"]=item_instance["name"]
                        data_row_item["total_with_gst"]=item_instance["total_with_gst"]
                        data_row_item["item_balance"]=item_instance["item_balance"]

                        try:
                            data_row_item["executive"]=cu_l[so["customer"]][item][0][0]
                            data_row_item["frequency"]=cu_l[so["customer"]][item][0][1]
                        except Exception as er:
                            print("START",er,cu_l[so["customer"]],data_row_item,"END")

                        if item_instance["item_balance"] == 0.0:
                            payment_status= "Cleared"
                            data_row_item["custom_payment_status"] = f'''<p style="color:Green;" >Cleared</p>'''
                        elif item_instance["item_balance"] == item_instance["total_with_gst"]:
                            payment_status= "Unpaid"
                            data_row_item["custom_payment_status"] = f'''<p style="color:Red;">Unpaid</p>'''
                        elif item_instance["item_balance"] > 0:
                            payment_status= "Partially Paid"
                            data_row_item["custom_payment_status"] = f'''<p style="color:#b34700;" >Partially Paid</p>'''

                        if filters.get("custom_payment_status"):
                            if payment_status in filters.get("custom_payment_status") :
                                    
                                    data += [data_row_item]
                        else:
                            data += [data_row_item]
            
    return data



# START
# 'Incometax Filing' 
# {'custom_customer_tags': 'Not Approached SO', 'custom_customer_behaviour_': 'Green', 'custom_behaviour_note': None, 
#         'custom_customer_status_': 'HOLD', 'custom_contact_person': None, 'custom_primary_mobile_no': None, 
#         'custom_primary_email': None, 'disabled': 0} 
# {'so_id': 'SAL-ORD-2024-00158', 'customer_id': '20130632', 'customer_name': 'DURGA ELECTRICALS', 'custom_contact_person': None, 
#         'mobile number': None, 'custom_customer_behaviour_': 'Green', 'custom_behaviour_note': None, 
#         'custom_customer_status_': 'HOLD', 'custom_customer_disabled_': 0, 'custom_so_from_date': datetime.date(2024, 2, 20), 
#         'custom_so_to_date': datetime.date(2024, 2, 20), 'transaction_date': datetime.date(2024, 2, 20), 'rounded_total': 12390.0, 
#         'doc_status': 'Submitted', 'custom_followup_count': 0, 'payment_recieved': 0.0, 'payment_entry': 0.0, 
#         'unallocated_amount_to_item': 0.0, 'so_payment_status': '<p style="color:Red;">Unpaid</p>', 
#         'custom_customer_tags': '<p style="color:Orange;">Not Approached</p>', 'item_code': 'Incometax Filing', 
#         'item_id': None, 'total_with_gst': 4500.0, 'item_balance': 4500.0} 
# END


