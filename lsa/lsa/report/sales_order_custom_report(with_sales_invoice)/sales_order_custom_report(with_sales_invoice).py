import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns
        {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": "Status PE", "fieldname": "custom_payment_status", "fieldtype": "Select", "width": 60},
        # {"label": "SI", "fieldname": "si_status", "fieldtype": "Data", "width": 35},

        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 90},
        {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 125},
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 110},
        {"label": "Shared with Client", "fieldname": "shared_with_client", "fieldtype": "Data", "width": 50},

        # {"label": "Total Amount", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
        # {"label": "Advance Paid", "fieldname": "advance_paid", "fieldtype": "Currency", "width": 100},

        {"label": "SO Balance Amount", "fieldname": "custom_so_balance_amount", "fieldtype": "Currency", "width": 100},
        # {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "HTML", "width": 80},
        {"label": "SO Approved", "fieldname": "so_tag", "fieldtype": "HTML", "width": 80},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 65},
        # {"label": "Customer Disabled", "fieldname": "custom_customer_disabled_", "fieldtype": "Data", "width": 50},
        {"label": "Next Follwup Date", "fieldname": "next_followup_date", "fieldtype": "Date", "width": 100},

        {"label": "FollowUp Count", "fieldname": "followup_count", "fieldtype": "Int", "width": 30},
        {"label": "FollowUp", "fieldname": "followup_button", "fieldtype": "HTML", "width": 30},
        {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 110},
        {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 110},
        # {"label": "Status SI", "fieldname": "custom_payment_status_si", "fieldtype": "Data", "width": 100},
        # {"label": "Sales Invoice", "fieldname": "custom_si_ids", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        # {"label": "Amount Paid SI", "fieldname": "si_advanced_paid", "fieldtype": "Currency", "width": 100},
        # {"label": "Due Amount SI", "fieldname": "custom_so_balance_amount_si", "fieldtype": "Currency", "width": 100},
    ]
    base_url=frappe.utils.get_url() 
    # Get data for the report
    data,followup_data = get_data(filters)
    so_wo_followup=followup_data["so_wo_followup"]
    overdue_followup=followup_data["overdue_followup"]
    today_followup=followup_data["today_followup"]
    upcoming_followup=followup_data["upcoming_followup"]


    # so_with_fu=followup_data["so_with_fu"]
    # cu_fos = frappe.get_all("Customer Followup", filters={"status":"Open"},fields=["name"])
    # cu_fos=[i.name for i in cu_fos]
    # count=0
    # for fo in so_with_fu:
    #     if  fo not in cu_fos:
    #         print(fo)  
    #     else:
    #         count+=1         
    # print(count,len(cu_fos),len(so_with_fu))


    # print(len(set(so_with_fu)))
    html_card = f"""
    <div style="display: flex; flex-wrap: wrap;">
    <!-- Customer Summary Card -->
    <div class="frappe-card" style="width: 60%; padding-right: 10px; box-sizing: border-box;">
        <div class="frappe-card-head">
            <h5><strong>FollowUp Summary</strong></h5>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body" id="executive-content">
            <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
                <thead>
                    <tr>
                        <th style="border:1px solid #A9A9A9;width: 350px;">SO without FollowUps:</th>
                        <th style="border:1px solid #A9A9A9;">{so_wo_followup}</th>
                    </tr>
                    <tr>
                        <th style="border:1px solid #A9A9A9;">Overdue FollowUps:</th>
                        <th style="border:1px solid #A9A9A9;">{overdue_followup}</th>
                    </tr>
                    <tr>
                        <th style="border:1px solid #A9A9A9;">Today's FollowUps:</th>
                        <th style="border:1px solid #A9A9A9;">{today_followup}</th>
                    </tr>
                    <tr>
                        <th style="border:1px solid #A9A9A9;">Upcoming FollowUps:</th>
                        <th style="border:1px solid #A9A9A9;">{upcoming_followup}</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Rows will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <!-- Button Section -->
    <div style="width: 40%; display: flex; justify-content: flex-end; align-items: flex-start; padding-top: 10px; box-sizing: border-box;">
    <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/customer-followup/view/report'">
        <b style="color: #000000;">FollowUps</b>
    </button>
    <button class="btn btn-sm" style="background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/sales-order/new-sales-order-nyuseuxyqs'">
        <b style="color: #000000;">New Sales Order</b>
    </button>
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

    return columns, data, html_card


# Function to retrieve data based on filters
def get_data(filters):
    today = datetime.now().date()
    base_url=frappe.utils.get_url() 
    data = []
    doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    additional_filters = {}
    followup_range=None
    if filters:
        if filters.get("customer_id"):
            additional_filters["customer"] = filters.get("customer_id")
        if filters.get("so_approved"):
            additional_filters["custom_approval_status"] = filters.get("so_approved")
        if filters.get("doc_status"):
            status_list=filters.get("doc_status").split(',')
            status_list=[z.strip() for z in status_list if z.isalpha()]
            status_list=[doc_status_map_reverse[x] for x in status_list]
            additional_filters["docstatus"] = ["in", status_list]
        if filters.get("from_date"):
            additional_filters["custom_so_from_date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            additional_filters["custom_so_to_date"] = ["<=", filters.get("to_date")]
        if filters.get("followup_range"):
            followup_range=filters.get("followup_range")
            followup_range = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in followup_range]


    # customer_filter={}
    # if filters.get("customer_enabled"):
    #     if filters.get("customer_enabled")=="Customer Enabled":
    #         customer_filter["disabled"] = 0
    #     elif filters.get("customer_enabled")=="Customer Disabled":
    #         customer_filter["disabled"] = 1
    

    so_s = frappe.get_all("Sales Order",
                          filters=additional_filters,
                          fields=["name","customer","customer_name","contact_mobile","custom_so_from_date","custom_so_to_date",
                                  "transaction_date","rounded_total","docstatus","custom_followup_count","custom_approval_status"])
    
    cu=[]
    for cu_so in so_s:
        if cu_so.customer not in cu:
            cu.append(cu_so.customer)

    cu_s = frappe.get_all("Customer",
                        #   filters=customer_filter,
                        fields=["name","custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
                                  "custom_customer_status_","custom_contact_person","custom_primary_mobile_no","custom_primary_email","disabled"])
    so_shared_with_client=get_latest_sales_order_ids()
    #so_shared_with_client=[]

    cu_l={}
    for cu in cu_s:
        cu_l[cu["name"]]={cu_i:cu[cu_i] for cu_i in cu if cu_i !="name"}
    # print(cu_l)
    cu_s=cu_l

    pe_s = frappe.get_all("Payment Entry Reference",
                           filters={"reference_doctype": "Sales Order","docstatus": 1},
                           fields=["name","reference_name", "parent", "allocated_amount"])
    
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
    pe_s_d={}
    for pe_i in pe_s:
        if pe_i["reference_name"] in pe_s_d:
            pe_s_d[pe_i["reference_name"]]+=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
        else:
            pe_s_d[pe_i["reference_name"]]=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
	
    so_wo_followup=set()
    overdue_followup=set()
    today_followup=set()
    upcoming_followup=set()
    so_with_fu={}
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
                "shared_with_client":"Yes" if so.name in so_shared_with_client else "No",
            }

            custom_so_balance = so.rounded_total
            custom_advanced_paid = 0.00
            custom_pe_ids = []

            if so.name in pe_s_d:
                data_row["custom_pe_counts"] = len(pe_s_d[so.name])
                for pe in pe_s_d[so.name]:
                    custom_so_balance = custom_so_balance - pe[2]
                    custom_pe_ids.append(pe[1])
                    custom_advanced_paid = custom_advanced_paid + pe[2]
            else:
                data_row["custom_pe_counts"] = 0
            
            # custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":"Not Approved","Not Approached SO":"Not Approached"}
            # if cu_s[so.customer]["custom_customer_tags"]=="SO Approved":
            #     data_row["custom_customer_tags"]=f'''<p style="color:Green;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            # elif cu_s[so.customer]["custom_customer_tags"]=="SO Not Approved":
            #     data_row["custom_customer_tags"]=f'''<p style="color:Red;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            # elif cu_s[so.customer]["custom_customer_tags"]=="Not Approached SO":
            #     data_row["custom_customer_tags"]=f'''<p style="color:Orange;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            
            
            if so.custom_approval_status=="Approved":
                data_row["so_tag"]=f'''<p style="color:Green;">{so.custom_approval_status}</p>'''
            elif so.custom_approval_status=="Not Approved":
                data_row["so_tag"]=f'''<p style="color:Red;">{so.custom_approval_status}</p>'''
            
            data_row["custom_pe_ids"] = ",".join(custom_pe_ids)
            data_row["custom_so_balance_amount"] = custom_so_balance
            data_row["advance_paid"] = custom_advanced_paid

            if custom_so_balance == 0:
                payment_status= "Cleared"
                data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:Green;" >Cleared</a>'''
                # data_row["followup_button"] = f'''<p>({so.custom_followup_count})</p>'''
                data_row["followup_count"]=so.custom_followup_count
            elif custom_so_balance == so.rounded_total:
                payment_status= "Unpaid"
                data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:Red;">Unpaid</a>'''
                if so.name not in op_fu_so:
                    data_row["followup_count"]=so.custom_followup_count
                    data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
                else:
                    data_row["followup_count"]=so.custom_followup_count
                    data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
            elif custom_so_balance > 0:
                payment_status= "Partially Paid"
                data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:#b34700;" >Partially Paid</a>'''
                if so.name not in op_fu_so:
                    data_row["followup_count"]=so.custom_followup_count
                    data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
                else:
                    data_row["followup_count"]=so.custom_followup_count
                    data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
            
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
                        per_s = frappe.get_all("Payment Entry Reference",
                                                filters={"reference_doctype": "Sales Invoice","reference_name":si,"docstatus": 1},
                                                fields=["allocated_amount"])
                        # si_advanced_paid += (si.net_amount*1.18)
                        # custom_so_balance_amount_si -= (si.net_amount*1.18)
                        for per in per_s:
                            si_advanced_paid+=per.allocated_amount
                            custom_so_balance_amount_si -= (per.allocated_amount)
                        custom_si_ids.append(si)
            
                    data_row["custom_si_ids"] = ",".join(custom_si_ids)
                    data_row["custom_so_balance_amount_si"] = custom_so_balance_amount_si
                    data_row["si_advanced_paid"] = si_advanced_paid
                    data_row["si_status"] = "Yes"
                    if custom_so_balance_amount_si <= 0:
                        data_row["custom_payment_status_si"] = "Cleared"
                    elif custom_so_balance_amount_si == so.rounded_total:
                        data_row["custom_payment_status_si"] = "Unpaid"
                    elif custom_so_balance_amount_si > 0:
                        data_row["custom_payment_status_si"] = "Partially Paid"
                else:
                    data_row["custom_si_ids"] = None
                    data_row["custom_so_balance_amount_si"] = None
                    data_row["si_status"] = "No"
                    data_row["si_advanced_paid"] = None
                    data_row["custom_payment_status_si"] = None
            else:    
                data_row["si_status"] = "NA"
                data_row["custom_si_ids"] = None
                data_row["custom_so_balance_amount_si"] = None
                data_row["si_status"] = "No"
                data_row["si_advanced_paid"] = None
                data_row["custom_payment_status_si"] = None

            next_followup_date = ""
            sales_order_summary=""
            latest_sales_order_summary=""
            next_followup_name=""
            if payment_status != "Cleared":
                cu_fos = frappe.get_all("Customer Followup", filters={"status":"Open","customer_id": so.customer},fields=["name","sales_order_summary"],order_by="creation desc")
                
                if cu_fos:
                    for cu_fo in cu_fos:
                        sales_order_summary += cu_fo.sales_order_summary
                        fo_doc = frappe.get_doc("Customer Followup", cu_fo.name)
                        if fo_doc.next_followup_date:
                            date_format = "%Y-%m-%d"
                            this_followup_date = datetime.strptime(str(fo_doc.next_followup_date), date_format).date()
                            if next_followup_date == "" or this_followup_date >= next_followup_date:
                                next_followup_date = this_followup_date
                                latest_sales_order_summary=cu_fo.sales_order_summary
                                next_followup_name=cu_fo.name
                                
                            # print(type(this_followup_date))
                if next_followup_date:
                    if today>next_followup_date:
                        overdue_followup.add(next_followup_name)
                    elif today==next_followup_date:
                        today_followup.add(next_followup_name)
                    elif today<next_followup_date:
                        upcoming_followup.add(next_followup_name)
                if so.name not in sales_order_summary:
                    so_wo_followup.add(next_followup_name)
                    
                    
                if followup_range and next_followup_date and \
                    next_followup_date>= followup_range[0] and next_followup_date<= followup_range[1]:
                    data_row["next_followup_date"] = next_followup_date
                elif not followup_range:
                    data_row["next_followup_date"] = next_followup_date
                else:
                    continue

            customer_filter=[0,1]
            if filters.get("customer_enabled"):
                if filters.get("customer_enabled")=="Customer Enabled":
                    customer_filter=[0]
                elif filters.get("customer_enabled")=="Customer Disabled":
                    customer_filter=[1]

            customer_status_filter="ACTIVE,ON NOTICE,HOLD"
            if filters.get("custom_customer_status_"):
                customer_status_filter=filters.get("custom_customer_status_")
                

            if filters.get("custom_payment_status"):
                # if payment_status in filters.get("custom_payment_status") and cu_s[so.customer]["disabled"]==0:
                if payment_status in filters.get("custom_payment_status") and \
                    cu_s[so.customer]["disabled"] in customer_filter and \
                    cu_s[so.customer]["custom_customer_status_"] in customer_status_filter :
                    if filters.get("sales_invoice"):
                        if filters.get("sales_invoice") =="Yes" and data_row["si_status"] == "Yes":
                            data += [data_row]
                        elif filters.get("sales_invoice") =="No" and data_row["si_status"] == "No":
                            data += [data_row]
                    else:
                        data += [data_row]
            else:
                data += [data_row]

    return data,{"so_with_fu":len(so_with_fu),"so_wo_followup":len(so_wo_followup),"overdue_followup":len(overdue_followup),"today_followup":len(today_followup),"upcoming_followup":len(upcoming_followup),}


def get_latest_sales_order_ids():
    query = """
        SELECT
            document_id
        FROM
            (
                SELECT
                    document_id,
                    ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY creation DESC) AS rn
                FROM
                    `tabMessage Detail`
                WHERE
                    type = 'Sales Order'
            ) AS message_log
        WHERE
            message_log.rn = 1;
    """
    
    # Execute the SQL query
    result = frappe.db.sql(query, as_dict=True)
    
    # Extract document_id values from the result
    sales_order_ids = [row['document_id'] for row in result]
    
    return sales_order_ids







