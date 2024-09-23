import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # print('filtersssssssssssssssssssssssss',filters)
    # Define columns for the report
    columns = [
        # Customer details columns
        {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": "Status PE", "fieldname": "custom_payment_status", "fieldtype": "Select", "width": 60},
        {"label": "SI", "fieldname": "si_status", "fieldtype": "Data", "width": 35},

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
        {"label": "Status SI", "fieldname": "custom_payment_status_si", "fieldtype": "Data", "width": 100},
        {"label": "Sales Invoice", "fieldname": "custom_si_ids", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": "Amount Paid SI", "fieldname": "si_advanced_paid", "fieldtype": "Currency", "width": 100},
        {"label": "Due Amount SI", "fieldname": "custom_so_balance_amount_si", "fieldtype": "Currency", "width": 100},
        {
            "label": "Service", 
            "fieldname": "service", 
            "fieldtype": "Small Text", 
            "width": 150, 
            "cellStyle": {"white-space": "normal", "word-wrap": "break-word"}  # Allow text wrapping
        }
    ]
    base_url=frappe.utils.get_url() 
    # Get data for the report
    data,followup_data = get_data(filters)
    so_wo_followup=followup_data["so_wo_followup"]
    overdue_followup=followup_data["overdue_followup"]
    today_followup=followup_data["today_followup"]
    upcoming_followup=followup_data["upcoming_followup"]


    item_summary = {}
    data, item_summary = get_data(filters)

    # If `data` is a list of dictionaries, iterate through it to find item_summary
    for item in data, item_summary:
        # Check if the item contains 'item_summary' key
        if isinstance(item, dict) and 'item_summary' in item:
            item_summary = item['item_summary']
            break  # Exit the loop if item_summary is found

    # Ensure item_summary is a dictionary
    if isinstance(item_summary, dict):
        # Initialize variables for total amount and grand total
        total_amount = 0

        # Generate HTML for item summary
        item_rows = ""
        for item_code, amount in item_summary.items():
            if isinstance(amount, (int, float)):  # Ensure amount is numeric
                taxed_amount = amount * 1.18  # Calculate the taxed amount
                total_amount += amount  # Sum up the amounts
                item_rows += f"""
                <tr>
                    <td style="border:1px solid #A9A9A9;">{item_code}</td>
                    <td class="currency" style="border:1px solid #A9A9A9;">{amount:.2f}</td>
                    <td class="currency" style="border:1px solid #A9A9A9;">{taxed_amount:.2f}</td>
                </tr>
                """
            else:
                # Handle the case where amount is not a number
                item_rows += f"""
                <tr>
                    <td style="border:1px solid #A9A9A9;">{item_code}</td>
                    <td style="border:1px solid #A9A9A9;">Invalid Amount</td>
                    <td style="border:1px solid #A9A9A9;">N/A</td>
                </tr>
                
                """

        # Calculate the grand total including 18% tax
        grand_total = total_amount * 1.18

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
        <div class="frappe-card-head" data-toggle="collapse" data-target="#followup-summary-content">
            <h5><strong>FollowUp Summary</strong></h5>
        </div>
        <div id="followup-summary-content" class="collapse">
            <div class="frappe-card-body">
                <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
                    <thead>
                        <tr>
                            <th style="border:1px solid #A9A9A9;width: 350px;">SO without FollowUps:</th>
                            <th style="border:1px solid #A9A9A9;">{followup_data["so_wo_followup"]}</th>
                        </tr>
                        <tr>
                            <th style="border:1px solid #A9A9A9;">Overdue FollowUps:</th>
                            <th style="border:1px solid #A9A9A9;">{followup_data["overdue_followup"]}</th>
                        </tr>
                        <tr>
                            <th style="border:1px solid #A9A9A9;">Today's FollowUps:</th>
                            <th style="border:1px solid #A9A9A9;">{followup_data["today_followup"]}</th>
                        </tr>
                        <tr>
                            <th style="border:1px solid #A9A9A9;">Upcoming FollowUps:</th>
                            <th style="border:1px solid #A9A9A9;">{followup_data["upcoming_followup"]}</th>
                        </tr>
                    </thead>
                </table>
            </div>
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
    <br>
    <div class="frappe-card">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#item-content">
            <h5><strong>Service and Amount</strong></h5>
            <span class="collapse-icon"><strong>Grand Total (Including 18% Tax): </strong> : {grand_total:.2f}</span>
        </div>
        <div id="item-content" class="collapse">
            <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
                <thead>
                    <tr>
                        <th style="border:1px solid #A9A9A9;">Item Code</th>
                        <th style="border:1px solid #A9A9A9;">Amount</th>
                        <th style="border:1px solid #A9A9A9;">Amount with Tax (18%)</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>
           
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Function to format numbers as currency
            function formatCurrency(value) {{
                const formatter = new Intl.NumberFormat('en-US', {{
                    style: 'currency',
                    currency: 'INR'
                }});
                return formatter.format(value);
            }}

            // Format all elements with the 'currency' class
            document.querySelectorAll('.currency').forEach(function(element) {{
                element.textContent = formatCurrency(parseFloat(element.textContent));
            }});

            // Collapsible functionality
            const toggleArea = document.querySelector('.frappe-card-head[data-toggle="collapse"]');
            const contentArea = document.getElementById('item-content');
            const icon = document.querySelector('.collapse-icon');

            toggleArea.addEventListener('click', function() {{
                contentArea.classList.toggle('collapse');
                // Toggle icon between '+' and '-'
                icon.textContent = contentArea.classList.contains('collapse') ? '+' : '-';
            }});
        }});
        
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
                if (clickedRow) {{
                    var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
                    cellsInClickedRow.forEach(function(cell) {{
                        cell.classList.add('highlighted-cell');
                        cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
                        cell.style.border = '2px solid #90c9e3'; // Border color
                        cell.style.fontWeight = 'bold';
                    }});
                }}
            }}
        }});
    </script>
    """


    return columns, data, html_card


# Function to retrieve data based on filters


from datetime import datetime
import frappe

def get_data(filters):
    today = datetime.now().date()
    base_url = frappe.utils.get_url()
    data = []
    doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    additional_filters = {}
    followup_range = None

    if filters:
        if filters.get("customer_id"):
            additional_filters["so.customer"] = filters.get("customer_id")

        if filters.get("so_approved"):
            additional_filters["so.custom_approval_status"] = filters.get("so_approved")

        if filters.get("doc_status"):
            status_list = filters.get("doc_status").split(',')
            status_list = [z.strip() for z in status_list if z.isalpha()]
            status_list = [doc_status_map_reverse[x] for x in status_list]
            additional_filters["so.docstatus"] = ["IN", tuple(status_list)]

        if filters.get("from_date"):
            additional_filters["so.custom_so_from_date"] = [">=", filters.get("from_date")]

        if filters.get("to_date"):
            additional_filters["so.custom_so_to_date"] = ["<=", filters.get("to_date")]

        if filters.get("followup_range"):
            followup_range = filters.get("followup_range")
            followup_range = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in followup_range]

    # Construct the WHERE conditions
    conditions = []
    for key, value in additional_filters.items():
        if isinstance(value, list):
            if value[0] == "IN":
                in_values = ', '.join(f"'{v}'" for v in value[1])
                conditions.append(f"{key} {value[0]} ({in_values})")
            elif len(value) >= 2:
                operator, val = value[0], value[1]
                if isinstance(val, str):
                    val = f"'{val}'"
                conditions.append(f"{key} {operator} {val}")
            else:
                conditions.append(f"{key} = '{value[0]}'")
        else:
            if isinstance(value, str):
                value = f"'{value}'"
            conditions.append(f"{key} = {value}")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Apply item filter clause if provided
    if filters.get("items"):
        item_filter = filters.get("items")
        item_string = "', '".join(str(item) for item in item_filter)

        # Subquery to find sales orders where all items are in the filter
        sales_order_filter_subquery = f"""
        AND so.name IN (
            SELECT parent
            FROM `tabSales Order Item` soi
            WHERE soi.item_code IN ('{item_string}')
            GROUP BY parent
            HAVING COUNT(DISTINCT soi.item_code) = (
                SELECT COUNT(DISTINCT soi2.item_code)
                FROM `tabSales Order Item` soi2
                WHERE soi2.parent = soi.parent
            )
        )
        """
        where_clause += sales_order_filter_subquery

    # SQL query to fetch the sales orders and join with Sales Order Item
    query = f"""
    SELECT 
        so.name, 
        so.customer, 
        so.customer_name, 
        so.contact_mobile, 
        so.custom_so_from_date, 
        so.custom_so_to_date, 
        so.transaction_date, 
        so.rounded_total, 
        so.advance_paid,
        so.docstatus, 
        so.custom_followup_count, 
        so.custom_approval_status,
        GROUP_CONCAT(DISTINCT soi.item_code ORDER BY soi.item_code SEPARATOR ', ') AS item_codes,  
        SUM(soi.qty) AS total_qty,  
        SUM(soi.amount) AS total_amount  
    FROM
        `tabSales Order` so
    JOIN
        `tabSales Order Item` soi ON so.name = soi.parent
    WHERE
        {where_clause}
    GROUP BY
        so.name;
    """

    # Execute query
    so_s = frappe.db.sql(query, as_dict=True)
    print('so_ssssssssssssssssssssss',so_s)
    total_amount = 0
    item_summary = {}

    # Retrieve filters for customer status, customer enabled, and payment status
    customer_enabled_filter = filters.get("customer_enabled", [])
    custom_customer_status_filter = filters.get("custom_customer_status_", [])

    # Ensure custom_customer_status_filter is a list (in case of multiple statuses)
    if isinstance(custom_customer_status_filter, str):
        custom_customer_status_filter = custom_customer_status_filter.split(",")

    if isinstance(customer_enabled_filter, str):
        customer_enabled_filter = customer_enabled_filter.split(",")

    # Map "Customer Enabled" and "Customer Disabled" to 0 and 1
    customer_enabled_filter_mapped = []
    for status in customer_enabled_filter:
        if status == "Customer Enabled":
            customer_enabled_filter_mapped.append(0)  # 0 means Customer Enabled
        elif status == "Customer Disabled":
            customer_enabled_filter_mapped.append(1)  # 1 means Customer Disabled

    # Retrieve the custom payment status filter (e.g., Unpaid, Partially Paid, Cleared)
    payment_status_filter = filters.get("custom_payment_status", "")
    payment_status_list = [status.strip() for status in payment_status_filter.split(",") if status.strip()]

    # Loop through the result to calculate total amount and extract item codes
    for row in so_s:
        item_code = row.get('item_codes')  # Changed to 'item_codes' from 'item_code'
        customer_name = row.get('customer')  # Assuming the customer field exists in so_s
        rounded_total = row.get('rounded_total', 0)
        advance_paid = row.get('advance_paid', 0)
        total_amount_order = row.get('total_amount', 0)
        # print("item_codeeeeeeeeeeeeeeeeee",item_code)
        # Fetch customer details from the Customer doctype (use frappe.db.get_value)
        customer_details = frappe.db.get_value("Customer", customer_name, ["disabled", "custom_customer_status_"], as_dict=True)

        if customer_details:
            customer_enabled = customer_details.get("disabled")
            custom_customer_status = customer_details.get("custom_customer_status_")

            # Determine the custom payment status based on rounded_total and advance_paid
            if advance_paid == 0:
                payment_status = "Unpaid"
            elif advance_paid >= rounded_total:
                payment_status = "Cleared"
            else:
                payment_status = "Partially Paid"

            # Apply the filters for customer_enabled, custom_customer_status_, and custom_payment_status
            # Check if customer_enabled matches the mapped filter (if filter is provided)
            if (not customer_enabled_filter_mapped or customer_enabled in customer_enabled_filter_mapped) and \
            (not custom_customer_status_filter or custom_customer_status in custom_customer_status_filter) and \
            (not payment_status_list or payment_status in payment_status_list):

                # Check if the item_code is in the filter list
                if item_code in filters.get("items", []):
                    amount = total_amount_order or 0

                    # Ensure amount is a valid number
                    try:
                        amount = float(amount)
                    except (TypeError, ValueError):
                        amount = 0

                    # Update the item_summary dictionary
                    if item_code not in item_summary:
                        item_summary[item_code] = 0
                    item_summary[item_code] += amount

                    # Add the amount to the total amount
                    total_amount += amount


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
                "service":so.item_codes
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
    print('testtttttttttttttttttttttttt',item_summary)
    return data,{"item_summary":item_summary,"so_with_fu":len(so_with_fu),"so_wo_followup":len(so_wo_followup),"overdue_followup":len(overdue_followup),"today_followup":len(today_followup),"upcoming_followup":len(upcoming_followup),}


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














#######################################################################################

# import frappe
# from datetime import datetime
# from frappe.utils import escape_html

# # Define the main function to generate the report based on filters
# def execute(filters=None):
#     # print('filtersssssssssssssssssssssssss',filters)
#     # Define columns for the report
#     columns = [
#         # Customer details columns
#         {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
#         {"label": "Status PE", "fieldname": "custom_payment_status", "fieldtype": "Select", "width": 60},
#         {"label": "SI", "fieldname": "si_status", "fieldtype": "Data", "width": 35},

#         {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 90},
#         {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
#         {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 125},
#         {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 110},
#         {"label": "Shared with Client", "fieldname": "shared_with_client", "fieldtype": "Data", "width": 50},

#         # {"label": "Total Amount", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
#         # {"label": "Advance Paid", "fieldname": "advance_paid", "fieldtype": "Currency", "width": 100},

#         {"label": "SO Balance Amount", "fieldname": "custom_so_balance_amount", "fieldtype": "Currency", "width": 100},
#         # {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "HTML", "width": 80},
#         {"label": "SO Approved", "fieldname": "so_tag", "fieldtype": "HTML", "width": 80},
#         {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 65},
#         # {"label": "Customer Disabled", "fieldname": "custom_customer_disabled_", "fieldtype": "Data", "width": 50},
#         {"label": "Next Follwup Date", "fieldname": "next_followup_date", "fieldtype": "Date", "width": 100},

#         {"label": "FollowUp Count", "fieldname": "followup_count", "fieldtype": "Int", "width": 30},
#         {"label": "FollowUp", "fieldname": "followup_button", "fieldtype": "HTML", "width": 30},
#         {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 110},
#         {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 110},
#         {"label": "Status SI", "fieldname": "custom_payment_status_si", "fieldtype": "Data", "width": 100},
#         {"label": "Sales Invoice", "fieldname": "custom_si_ids", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
#         {"label": "Amount Paid SI", "fieldname": "si_advanced_paid", "fieldtype": "Currency", "width": 100},
#         {"label": "Due Amount SI", "fieldname": "custom_so_balance_amount_si", "fieldtype": "Currency", "width": 100},
#     ]
#     base_url=frappe.utils.get_url() 
#     # Get data for the report
#     data,followup_data = get_data(filters)
#     # print('mohannnnnnnnnnnnnnnnnnnnnnnnnnn',data)
#     so_wo_followup=followup_data["so_wo_followup"]
#     overdue_followup=followup_data["overdue_followup"]
#     today_followup=followup_data["today_followup"]
#     upcoming_followup=followup_data["upcoming_followup"]


#     item_summary = {}
#     data, item_summary = get_data(filters)

#     # If `data` is a list of dictionaries, iterate through it to find item_summary
#     for item in data, item_summary:
#         # Check if the item contains 'item_summary' key
#         if isinstance(item, dict) and 'item_summary' in item:
#             item_summary = item['item_summary']
#             break  # Exit the loop if item_summary is found

#     # Ensure item_summary is a dictionary
#     if isinstance(item_summary, dict):
#         # Initialize variables for total amount and grand total
#         total_amount = 0

#         # Generate HTML for item summary
#         item_rows = ""
#         for item_code, amount in item_summary.items():
#             if isinstance(amount, (int, float)):  # Ensure amount is numeric
#                 taxed_amount = amount * 1.18  # Calculate the taxed amount
#                 total_amount += amount  # Sum up the amounts
#                 item_rows += f"""
#                 <tr>
#                     <td style="border:1px solid #A9A9A9;">{item_code}</td>
#                     <td class="currency" style="border:1px solid #A9A9A9;">{amount:.2f}</td>
#                     <td class="currency" style="border:1px solid #A9A9A9;">{taxed_amount:.2f}</td>
#                 </tr>
#                 """
#             else:
#                 # Handle the case where amount is not a number
#                 item_rows += f"""
#                 <tr>
#                     <td style="border:1px solid #A9A9A9;">{item_code}</td>
#                     <td style="border:1px solid #A9A9A9;">Invalid Amount</td>
#                     <td style="border:1px solid #A9A9A9;">N/A</td>
#                 </tr>
                
#                 """

#         # Calculate the grand total including 18% tax
#         grand_total = total_amount * 1.18

#     # so_with_fu=followup_data["so_with_fu"]
#     # cu_fos = frappe.get_all("Customer Followup", filters={"status":"Open"},fields=["name"])
#     # cu_fos=[i.name for i in cu_fos]
#     # count=0
#     # for fo in so_with_fu:
#     #     if  fo not in cu_fos:
#     #         print(fo)  
#     #     else:
#     #         count+=1         
#     # print(count,len(cu_fos),len(so_with_fu))


#     # print(len(set(so_with_fu)))

#     html_card = f"""
#     <div style="display: flex; flex-wrap: wrap;">
#         <!-- Customer Summary Card -->
#         <div class="frappe-card" style="width: 60%; padding-right: 10px; box-sizing: border-box;">
#         <div class="frappe-card-head" data-toggle="collapse" data-target="#followup-summary-content">
#             <h5><strong>FollowUp Summary</strong></h5>
#         </div>
#         <div id="followup-summary-content" class="collapse">
#             <div class="frappe-card-body">
#                 <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
#                     <thead>
#                         <tr>
#                             <th style="border:1px solid #A9A9A9;width: 350px;">SO without FollowUps:</th>
#                             <th style="border:1px solid #A9A9A9;">{followup_data["so_wo_followup"]}</th>
#                         </tr>
#                         <tr>
#                             <th style="border:1px solid #A9A9A9;">Overdue FollowUps:</th>
#                             <th style="border:1px solid #A9A9A9;">{followup_data["overdue_followup"]}</th>
#                         </tr>
#                         <tr>
#                             <th style="border:1px solid #A9A9A9;">Today's FollowUps:</th>
#                             <th style="border:1px solid #A9A9A9;">{followup_data["today_followup"]}</th>
#                         </tr>
#                         <tr>
#                             <th style="border:1px solid #A9A9A9;">Upcoming FollowUps:</th>
#                             <th style="border:1px solid #A9A9A9;">{followup_data["upcoming_followup"]}</th>
#                         </tr>
#                     </thead>
#                 </table>
#             </div>
#         </div>
#     </div>

#         <!-- Button Section -->
#         <div style="width: 40%; display: flex; justify-content: flex-end; align-items: flex-start; padding-top: 10px; box-sizing: border-box;">
#             <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/customer-followup/view/report'">
#                 <b style="color: #000000;">FollowUps</b>
#             </button>
#             <button class="btn btn-sm" style="background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/sales-order/new-sales-order-nyuseuxyqs'">
#                 <b style="color: #000000;">New Sales Order</b>
#             </button>
#         </div>
#     </div>
#     <br>
#     <div class="frappe-card">
#         <div class="frappe-card-head" data-toggle="collapse" data-target="#item-content">
#             <h5><strong>Service and Amount</strong></h5>
#             <span class="collapse-icon"><strong>Grand Total (Including 18% Tax): </strong> : {grand_total:.2f}</span>
#         </div>
#         <div id="item-content" class="collapse">
#             <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
#                 <thead>
#                     <tr>
#                         <th style="border:1px solid #A9A9A9;">Item Code</th>
#                         <th style="border:1px solid #A9A9A9;">Amount</th>
#                         <th style="border:1px solid #A9A9A9;">Amount with Tax (18%)</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     {item_rows}
#                 </tbody>
#             </table>
           
#         </div>
#     </div>

#     <script>
#         document.addEventListener('DOMContentLoaded', function() {{
#             // Function to format numbers as currency
#             function formatCurrency(value) {{
#                 const formatter = new Intl.NumberFormat('en-US', {{
#                     style: 'currency',
#                     currency: 'INR'
#                 }});
#                 return formatter.format(value);
#             }}

#             // Format all elements with the 'currency' class
#             document.querySelectorAll('.currency').forEach(function(element) {{
#                 element.textContent = formatCurrency(parseFloat(element.textContent));
#             }});

#             // Collapsible functionality
#             const toggleArea = document.querySelector('.frappe-card-head[data-toggle="collapse"]');
#             const contentArea = document.getElementById('item-content');
#             const icon = document.querySelector('.collapse-icon');

#             toggleArea.addEventListener('click', function() {{
#                 contentArea.classList.toggle('collapse');
#                 // Toggle icon between '+' and '-'
#                 icon.textContent = contentArea.classList.contains('collapse') ? '+' : '-';
#             }});
#         }});
        
#         document.addEventListener('click', function(event) {{
#             // Check if the clicked element is a cell
#             var clickedCell = event.target.closest('.dt-cell__content');
#             if (clickedCell) {{
#                 // Remove highlight from previously highlighted cells
#                 var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
#                 previouslyHighlightedCells.forEach(function(cell) {{
#                     cell.classList.remove('highlighted-cell');
#                     cell.style.backgroundColor = ''; // Remove background color
#                     cell.style.border = ''; // Remove border
#                     cell.style.fontWeight = '';
#                 }});
                
#                 // Highlight the clicked row's cells
#                 var clickedRow = event.target.closest('.dt-row');
#                 if (clickedRow) {{
#                     var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
#                     cellsInClickedRow.forEach(function(cell) {{
#                         cell.classList.add('highlighted-cell');
#                         cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
#                         cell.style.border = '2px solid #90c9e3'; // Border color
#                         cell.style.fontWeight = 'bold';
#                     }});
#                 }}
#             }}
#         }});
#     </script>
#     """

# #     html_card = f"""
# #     <div style="display: flex; flex-wrap: wrap;">
# #     <!-- Customer Summary Card -->
# #     <div class="frappe-card" style="width: 60%; padding-right: 10px; box-sizing: border-box;">
# #         <div class="frappe-card-head">
# #             <h5><strong>FollowUp Summary</strong></h5>
# #             <span class="caret"></span>
# #         </div>
# #         <div class="frappe-card-body" id="executive-content">
# #             <table class="table table-bordered" style="border-color: #4a4a4a; width: 100%;">
# #                 <thead>
# #                     <tr>
# #                         <th style="border:1px solid #A9A9A9;width: 350px;">SO without FollowUps:</th>
# #                         <th style="border:1px solid #A9A9A9;">{so_wo_followup}</th>
# #                     </tr>
# #                     <tr>
# #                         <th style="border:1px solid #A9A9A9;">Overdue FollowUps:</th>
# #                         <th style="border:1px solid #A9A9A9;">{overdue_followup}</th>
# #                     </tr>
# #                     <tr>
# #                         <th style="border:1px solid #A9A9A9;">Today's FollowUps:</th>
# #                         <th style="border:1px solid #A9A9A9;">{today_followup}</th>
# #                     </tr>
# #                     <tr>
# #                         <th style="border:1px solid #A9A9A9;">Upcoming FollowUps:</th>
# #                         <th style="border:1px solid #A9A9A9;">{upcoming_followup}</th>
# #                     </tr>
# #                 </thead>
# #                 <tbody>
# #                     <!-- Rows will be inserted here by JavaScript -->
# #                 </tbody>
# #             </table>
# #         </div>
# #     </div>

# #     <!-- Button Section -->
# #     <div style="width: 40%; display: flex; justify-content: flex-end; align-items: flex-start; padding-top: 10px; box-sizing: border-box;">
# #     <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/customer-followup/view/report'">
# #         <b style="color: #000000;">FollowUps</b>
# #     </button>
# #     <button class="btn btn-sm" style="background-color: #A9A9A9;" onclick="window.location.href='{base_url}/app/sales-order/new-sales-order-nyuseuxyqs'">
# #         <b style="color: #000000;">New Sales Order</b>
# #     </button>
# # </div>

# # </div>

# #     <script>
# #         document.addEventListener('click', function(event) {{
# #             // Check if the clicked element is a cell
# #             var clickedCell = event.target.closest('.dt-cell__content');
# #             if (clickedCell) {{
# #                 // Remove highlight from previously highlighted cells
# #                 var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
# #                 previouslyHighlightedCells.forEach(function(cell) {{
# #                     cell.classList.remove('highlighted-cell');
# #                     cell.style.backgroundColor = ''; // Remove background color
# #                     cell.style.border = ''; // Remove border
# #                     cell.style.fontWeight = '';
# #                 }});
                
# #                 // Highlight the clicked row's cells
# #                 var clickedRow = event.target.closest('.dt-row');
# #                 var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
# #                 cellsInClickedRow.forEach(function(cell) {{
# #                     cell.classList.add('highlighted-cell');
# #                     cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
# #                     cell.style.border = '2px solid #90c9e3'; // Border color
# #                     cell.style.fontWeight = 'bold';
# #                 }});
# #             }}
# #         }});



    
# #     </script>
# #     """

#     return columns, data, html_card


# # Function to retrieve data based on filters
# def get_data(filters):
#     today = datetime.now().date()
#     base_url=frappe.utils.get_url() 
#     data = []
#     doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
#     additional_filters = {}
#     followup_range=None
#     if filters:
#         if filters.get("customer_id"):
#             additional_filters["so.customer"] = filters.get("customer_id")

#         if filters.get("so_approved"):
#             additional_filters["so.custom_approval_status"] = filters.get("so_approved")

#         if filters.get("items"):
#             item_filter = filters.get("items")
#             # Format the item filter correctly for SQL IN clause
#             item_string = "', '".join(str(item) for item in item_filter)
#             item_filter_clause = f"AND soi.item_code IN ('{item_string}')"
#         else:
#             item_filter_clause = ""

#         if filters.get("doc_status"):
#             status_list = filters.get("doc_status").split(',')
#             status_list = [z.strip() for z in status_list if z.isalpha()]
#             status_list = [doc_status_map_reverse[x] for x in status_list]
#             # Use tuple for SQL 'IN' clause
#             additional_filters["so.docstatus"] = ["IN", tuple(status_list)]

#         if filters.get("from_date"):
#             additional_filters["so.custom_so_from_date"] = [">=", filters.get("from_date")]

#         if filters.get("to_date"):
#             additional_filters["so.custom_so_to_date"] = ["<=", filters.get("to_date")]

#         if filters.get("followup_range"):
#             followup_range = filters.get("followup_range")
#             followup_range = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in followup_range]

#     # Construct the WHERE conditions
#     conditions = []
#     for key, value in additional_filters.items():
#         if isinstance(value, list):
#             if value[0] == "IN":
#                 # Format the IN clause correctly
#                 in_values = ', '.join(f"'{v}'" for v in value[1])
#                 conditions.append(f"{key} {value[0]} ({in_values})")
#             elif len(value) >= 2:  # Ensure there are at least two elements for operator conditions
#                 operator, val = value[0], value[1]
#                 if isinstance(val, str):
#                     val = f"'{val}'"
#                 conditions.append(f"{key} {operator} {val}")
#             else:
#                 conditions.append(f"{key} = '{value[0]}'")  # Fallback for unexpected list formats
#         else:
#             if isinstance(value, str):
#                 value = f"'{value}'"
#             conditions.append(f"{key} = {value}")

#     where_clause = " AND ".join(conditions) if conditions else "1=1"
#     if item_filter_clause:
#         where_clause += f" {item_filter_clause}"

#     # SQL query to fetch the sales orders and join with Sales Order Item
#     query = f"""
#     SELECT 
#         so.name, 
#         so.customer, 
#         so.customer_name, 
#         so.contact_mobile, 
#         so.custom_so_from_date, 
#         so.custom_so_to_date, 
#         so.transaction_date, 
#         so.rounded_total, 
#         so.advance_paid,
#         so.docstatus, 
#         so.custom_followup_count, 
#         so.custom_approval_status,
#         soi.item_code, 
#         soi.qty, 
#         soi.rate,
#         soi.amount
#     FROM
#         `tabSales Order` so
#     JOIN
#         `tabSales Order Item` soi ON so.name = soi.parent
#     WHERE
#         {where_clause};
#     """
    
#     # print(query)  # For debugging; remove or replace with logging in production
#     # Execute query
#     so_s = frappe.db.sql(query, as_dict=True)

#     total_amount = 0
#     item_summary = {}

#     # Retrieve filters for customer status, customer enabled, and payment status
#     customer_enabled_filter = filters.get("customer_enabled", [])
#     custom_customer_status_filter = filters.get("custom_customer_status_", [])

#     # Ensure custom_customer_status_filter is a list (in case of multiple statuses)
#     if isinstance(custom_customer_status_filter, str):
#         custom_customer_status_filter = custom_customer_status_filter.split(",")

#     if isinstance(customer_enabled_filter, str):
#         customer_enabled_filter = customer_enabled_filter.split(",")

#     # Map "Customer Enabled" and "Customer Disabled" to 0 and 1
#     customer_enabled_filter_mapped = []
#     for status in customer_enabled_filter:
#         if status == "Customer Enabled":
#             customer_enabled_filter_mapped.append(0)  # 0 means Customer Enabled
#         elif status == "Customer Disabled":
#             customer_enabled_filter_mapped.append(1)  # 1 means Customer Disabled

#     # Retrieve the custom payment status filter (e.g., Unpaid, Partially Paid, Cleared)
#     payment_status_filter = filters.get("custom_payment_status", "")
#     payment_status_list = [status.strip() for status in payment_status_filter.split(",") if status.strip()]

#     # Loop through the result to calculate total amount and extract item codes
#     for row in so_s:
#         item_code = row.get('item_code')
#         customer_name = row.get('customer')  # Assuming the customer field exists in so_s
#         rounded_total = row.get('rounded_total', 0)
#         advance_paid = row.get('advance_paid', 0)

#         # Fetch customer details from the Customer doctype (use frappe.db.get_value)
#         customer_details = frappe.db.get_value("Customer", customer_name, ["disabled", "custom_customer_status_"], as_dict=True)

#         if customer_details:
#             customer_enabled = customer_details.get("disabled")
#             custom_customer_status = customer_details.get("custom_customer_status_")

#             # Determine the custom payment status based on rounded_total and advance_paid
#             if advance_paid == 0:
#                 payment_status = "Unpaid"
#             elif advance_paid >= rounded_total:
#                 payment_status = "Cleared"
#             else:
#                 payment_status = "Partially Paid"

#             # Apply the filters for customer_enabled, custom_customer_status_, and custom_payment_status
#             # Check if customer_enabled matches the mapped filter (if filter is provided)
#             if (not customer_enabled_filter_mapped or customer_enabled in customer_enabled_filter_mapped) and \
#             (not custom_customer_status_filter or custom_customer_status in custom_customer_status_filter) and \
#             (not payment_status_list or payment_status in payment_status_list):

#                 # Check if the item_code is in the filter list
#                 if item_code in filters.get("items", []):
#                     amount = row.get('amount') or 0

#                     # Ensure amount is a valid number
#                     try:
#                         amount = float(amount)
#                     except (TypeError, ValueError):
#                         amount = 0

#                     # Update the item_summary dictionary
#                     if item_code not in item_summary:
#                         item_summary[item_code] = 0
#                     item_summary[item_code] += amount

#                     # Add the amount to the total amount
#                     total_amount += amount

#     # After the loop, you can use `item_summary` and `total_amount` as needed.



#     # if filters:
#     #     if filters.get("customer_id"):
#     #         additional_filters["customer"] = filters.get("customer_id")

#     #     if filters.get("so_approved"):
#     #         additional_filters["custom_approval_status"] = filters.get("so_approved")

#     #     if filters.get("items"):
#     #         additional_filters["items.item_code"] = filters.get("item")

#     #     if filters.get("doc_status"):
#     #         status_list=filters.get("doc_status").split(',')
#     #         status_list=[z.strip() for z in status_list if z.isalpha()]
#     #         status_list=[doc_status_map_reverse[x] for x in status_list]
#     #         additional_filters["docstatus"] = ["in", status_list]
#     #     if filters.get("from_date"):
#     #         additional_filters["custom_so_from_date"] = [">=", filters.get("from_date")]
#     #     if filters.get("to_date"):
#     #         additional_filters["custom_so_to_date"] = ["<=", filters.get("to_date")]
#     #     if filters.get("followup_range"):
#     #         followup_range=filters.get("followup_range")
#     #         followup_range = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in followup_range]


#     # customer_filter={}
#     # if filters.get("customer_enabled"):
#     #     if filters.get("customer_enabled")=="Customer Enabled":
#     #         customer_filter["disabled"] = 0
#     #     elif filters.get("customer_enabled")=="Customer Disabled":
#     #         customer_filter["disabled"] = 1
    
#     # Construct the WHERE conditions
    
#     # so_s = frappe.get_all("Sales Order",
#     #                       filters=additional_filters,
                          
#     #                       fields=["name","customer","customer_name","contact_mobile","custom_so_from_date","custom_so_to_date",
#     #                               "transaction_date","rounded_total","docstatus","custom_followup_count","custom_approval_status"])
    
#     cu=[]
#     for cu_so in so_s:
#         if cu_so.customer not in cu:
#             cu.append(cu_so.customer)

#     cu_s = frappe.get_all("Customer",
#                         #   filters=customer_filter,
#                         fields=["name","custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
#                                   "custom_customer_status_","custom_contact_person","custom_primary_mobile_no","custom_primary_email","disabled"])
#     so_shared_with_client=get_latest_sales_order_ids()
#     #so_shared_with_client=[]

#     cu_l={}
#     for cu in cu_s:
#         cu_l[cu["name"]]={cu_i:cu[cu_i] for cu_i in cu if cu_i !="name"}
#     # print(cu_l)
#     cu_s=cu_l

#     pe_s = frappe.get_all("Payment Entry Reference",
#                            filters={"reference_doctype": "Sales Order","docstatus": 1},
#                            fields=["name","reference_name", "parent", "allocated_amount"])
    
#     op_fus=frappe.get_all("Customer Followup",
#                           filters={"status":"Open"},
#                           fields=["name","sales_order_summary"]
#                           )
#     op_fus={h.name:h.sales_order_summary.split(", ") for h in op_fus}
#     op_fu_so={}
#     for op_fu in op_fus:
#         for so in op_fus[op_fu]:
#             if so not in op_fu_so:
#                 op_fu_so[so]=op_fu
#     pe_s_d={}
#     for pe_i in pe_s:
#         if pe_i["reference_name"] in pe_s_d:
#             pe_s_d[pe_i["reference_name"]]+=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
#         else:
#             pe_s_d[pe_i["reference_name"]]=[[pe_i["name"],pe_i["parent"],pe_i["allocated_amount"]]]
	
#     so_wo_followup=set()
#     overdue_followup=set()
#     today_followup=set()
#     upcoming_followup=set()
#     so_with_fu={}
#     for so in so_s:
#         doc_status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
#         # custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":" Not Approved","Not Approached SO":"Not Approached"}
#         # if so.customer=="20130563":
#         #     # print(so)
#         #     pass
#         if so.customer in cu_s:
#             data_row = {
#                 "so_id": so.name,
#                 "customer_id": so.customer,
#                 "customer_name": so.customer_name,
#                 "custom_contact_person": cu_s[so.customer]["custom_contact_person"],
#                 "mobile number": cu_s[so.customer]["custom_primary_mobile_no"],
#                 # "custom_customer_tags": cu_s[so.customer]["custom_customer_tags"],
#                 "custom_customer_behaviour_":cu_s[so.customer]["custom_customer_behaviour_"],
#                 "custom_behaviour_note": cu_s[so.customer]["custom_behaviour_note"],
#                 "custom_customer_status_": cu_s[so.customer]["custom_customer_status_"],
#                 "custom_customer_disabled_": cu_s[so.customer]["disabled"],
#                 "custom_so_from_date": so.custom_so_from_date,
#                 "custom_so_to_date": so.custom_so_to_date,
#                 "transaction_date": so.transaction_date,
#                 "rounded_total": so.rounded_total,
#                 "doc_status": doc_status_map[so.docstatus],
#                 "custom_followup_count": so.custom_followup_count,
#                 "shared_with_client":"Yes" if so.name in so_shared_with_client else "No",
#             }

#             custom_so_balance = so.rounded_total
#             custom_advanced_paid = 0.00
#             custom_pe_ids = []

#             if so.name in pe_s_d:
#                 data_row["custom_pe_counts"] = len(pe_s_d[so.name])
#                 for pe in pe_s_d[so.name]:
#                     custom_so_balance = custom_so_balance - pe[2]
#                     custom_pe_ids.append(pe[1])
#                     custom_advanced_paid = custom_advanced_paid + pe[2]
#             else:
#                 data_row["custom_pe_counts"] = 0
            
#             # custom_customer_tags_small={"SO Approved":"Approved","SO Not Approved":"Not Approved","Not Approached SO":"Not Approached"}
#             # if cu_s[so.customer]["custom_customer_tags"]=="SO Approved":
#             #     data_row["custom_customer_tags"]=f'''<p style="color:Green;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
#             # elif cu_s[so.customer]["custom_customer_tags"]=="SO Not Approved":
#             #     data_row["custom_customer_tags"]=f'''<p style="color:Red;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
#             # elif cu_s[so.customer]["custom_customer_tags"]=="Not Approached SO":
#             #     data_row["custom_customer_tags"]=f'''<p style="color:Orange;">{custom_customer_tags_small[cu_s[so.customer]["custom_customer_tags"]]}</p>'''
            
            
#             if so.custom_approval_status=="Approved":
#                 data_row["so_tag"]=f'''<p style="color:Green;">{so.custom_approval_status}</p>'''
#             elif so.custom_approval_status=="Not Approved":
#                 data_row["so_tag"]=f'''<p style="color:Red;">{so.custom_approval_status}</p>'''
            
#             data_row["custom_pe_ids"] = ",".join(custom_pe_ids)
#             data_row["custom_so_balance_amount"] = custom_so_balance
#             data_row["advance_paid"] = custom_advanced_paid

#             if custom_so_balance == 0:
#                 payment_status= "Cleared"
#                 data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:Green;" >Cleared</a>'''
#                 # data_row["followup_button"] = f'''<p>({so.custom_followup_count})</p>'''
#                 data_row["followup_count"]=so.custom_followup_count
#             elif custom_so_balance == so.rounded_total:
#                 payment_status= "Unpaid"
#                 data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:Red;">Unpaid</a>'''
#                 if so.name not in op_fu_so:
#                     data_row["followup_count"]=so.custom_followup_count
#                     data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
#                 else:
#                     data_row["followup_count"]=so.custom_followup_count
#                     data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
#             elif custom_so_balance > 0:
#                 payment_status= "Partially Paid"
#                 data_row["custom_payment_status"] = f'''<a href="{base_url}/app/sales-order/{so.name}" style="color:#b34700;" >Partially Paid</a>'''
#                 if so.name not in op_fu_so:
#                     data_row["followup_count"]=so.custom_followup_count
#                     data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/new-customer-followup-ukduqiedhw?customer_id={so.customer}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
#                 else:
#                     data_row["followup_count"]=so.custom_followup_count
#                     data_row["followup_button"] = f'''<a href="{base_url}/app/customer-followup/{op_fu_so[so.name]}"><button class="btn btn-sm" style="background-color:#3498DB;color:white; height:20px; font-size: 12px;   text-align: center; display: inline-block; "><b>F</b></button></a>'''
            
#             si_advanced_paid = 0.0
#             custom_so_balance_amount_si=custom_so_balance
#             custom_si_ids = []
#             if custom_so_balance_amount_si>0:
#                 si_item_s = frappe.get_all("Sales Invoice Item",
#                                     filters={"sales_order": so.name,"docstatus": 1},
#                                     fields=["name", "parent", "net_amount"])
                
#                 si_s=[]
#                 si_s=set([x.parent for x in si_item_s if x.parent not in si_s])
#                 si_s=list(si_s)
#                 # print(si_s)
#                 if si_s:
#                     for si in si_s:
#                         per_s = frappe.get_all("Payment Entry Reference",
#                                                 filters={"reference_doctype": "Sales Invoice","reference_name":si,"docstatus": 1},
#                                                 fields=["allocated_amount"])
#                         # si_advanced_paid += (si.net_amount*1.18)
#                         # custom_so_balance_amount_si -= (si.net_amount*1.18)
#                         for per in per_s:
#                             si_advanced_paid+=per.allocated_amount
#                             custom_so_balance_amount_si -= (per.allocated_amount)
#                         custom_si_ids.append(si)
            
#                     data_row["custom_si_ids"] = ",".join(custom_si_ids)
#                     data_row["custom_so_balance_amount_si"] = custom_so_balance_amount_si
#                     data_row["si_advanced_paid"] = si_advanced_paid
#                     data_row["si_status"] = "Yes"
#                     if custom_so_balance_amount_si <= 0:
#                         data_row["custom_payment_status_si"] = "Cleared"
#                     elif custom_so_balance_amount_si == so.rounded_total:
#                         data_row["custom_payment_status_si"] = "Unpaid"
#                     elif custom_so_balance_amount_si > 0:
#                         data_row["custom_payment_status_si"] = "Partially Paid"
#                 else:
#                     data_row["custom_si_ids"] = None
#                     data_row["custom_so_balance_amount_si"] = None
#                     data_row["si_status"] = "No"
#                     data_row["si_advanced_paid"] = None
#                     data_row["custom_payment_status_si"] = None
#             else:    
#                 data_row["si_status"] = "NA"
#                 data_row["custom_si_ids"] = None
#                 data_row["custom_so_balance_amount_si"] = None
#                 data_row["si_status"] = "No"
#                 data_row["si_advanced_paid"] = None
#                 data_row["custom_payment_status_si"] = None

#             next_followup_date = ""
#             sales_order_summary=""
#             latest_sales_order_summary=""
#             next_followup_name=""
#             if payment_status != "Cleared":
#                 cu_fos = frappe.get_all("Customer Followup", filters={"status":"Open","customer_id": so.customer},fields=["name","sales_order_summary"],order_by="creation desc")
                
#                 if cu_fos:
#                     for cu_fo in cu_fos:
#                         sales_order_summary += cu_fo.sales_order_summary
#                         fo_doc = frappe.get_doc("Customer Followup", cu_fo.name)
#                         if fo_doc.next_followup_date:
#                             date_format = "%Y-%m-%d"
#                             this_followup_date = datetime.strptime(str(fo_doc.next_followup_date), date_format).date()
#                             if next_followup_date == "" or this_followup_date >= next_followup_date:
#                                 next_followup_date = this_followup_date
#                                 latest_sales_order_summary=cu_fo.sales_order_summary
#                                 next_followup_name=cu_fo.name
                                
#                             # print(type(this_followup_date))
#                 if next_followup_date:
#                     if today>next_followup_date:
#                         overdue_followup.add(next_followup_name)
#                     elif today==next_followup_date:
#                         today_followup.add(next_followup_name)
#                     elif today<next_followup_date:
#                         upcoming_followup.add(next_followup_name)
#                 if so.name not in sales_order_summary:
#                     so_wo_followup.add(next_followup_name)
                    
                    
#                 if followup_range and next_followup_date and \
#                     next_followup_date>= followup_range[0] and next_followup_date<= followup_range[1]:
#                     data_row["next_followup_date"] = next_followup_date
#                 elif not followup_range:
#                     data_row["next_followup_date"] = next_followup_date
#                 else:
#                     continue

#             customer_filter=[0,1]
#             if filters.get("customer_enabled"):
#                 if filters.get("customer_enabled")=="Customer Enabled":
#                     customer_filter=[0]
#                 elif filters.get("customer_enabled")=="Customer Disabled":
#                     customer_filter=[1]

#             customer_status_filter="ACTIVE,ON NOTICE,HOLD"
#             if filters.get("custom_customer_status_"):
#                 customer_status_filter=filters.get("custom_customer_status_")
                

#             if filters.get("custom_payment_status"):
#                 # if payment_status in filters.get("custom_payment_status") and cu_s[so.customer]["disabled"]==0:
#                 if payment_status in filters.get("custom_payment_status") and \
#                     cu_s[so.customer]["disabled"] in customer_filter and \
#                     cu_s[so.customer]["custom_customer_status_"] in customer_status_filter :
#                     if filters.get("sales_invoice"):
#                         if filters.get("sales_invoice") =="Yes" and data_row["si_status"] == "Yes":
#                             data += [data_row]
#                         elif filters.get("sales_invoice") =="No" and data_row["si_status"] == "No":
#                             data += [data_row]
#                     else:
#                         data += [data_row]
#             else:
#                 data += [data_row]
#     # print('testtttttttttttttttttttttttt',item_summary)
#     return data,{"item_summary":item_summary,"so_with_fu":len(so_with_fu),"so_wo_followup":len(so_wo_followup),"overdue_followup":len(overdue_followup),"today_followup":len(today_followup),"upcoming_followup":len(upcoming_followup),}


# def get_latest_sales_order_ids():
#     query = """
#         SELECT
#             document_id
#         FROM
#             (
#                 SELECT
#                     document_id,
#                     ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY creation DESC) AS rn
#                 FROM
#                     `tabMessage Detail`
#                 WHERE
#                     type = 'Sales Order'
#             ) AS message_log
#         WHERE
#             message_log.rn = 1;
#     """
    
#     # Execute the SQL query
#     result = frappe.db.sql(query, as_dict=True)
    
#     # Extract document_id values from the result
#     sales_order_ids = [row['document_id'] for row in result]
    
#     return sales_order_ids






