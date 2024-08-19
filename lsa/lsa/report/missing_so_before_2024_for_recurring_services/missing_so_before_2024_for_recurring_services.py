import frappe
from datetime import datetime,date
import calendar
from lsa.custom_sales_order import so_payment_status



master_service_fields = {
        "Gstfile": ["gstfile", ["name", "customer_id", "company_name", "gst_number", "gst_user_name", "gst_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency","enabled"]],
        "IT Assessee File": ["it-assessee-file", ["name", "customer_id", "assessee_name", "pan", "it_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency","enabled"]],
        "MCA ROC File": ["mca-roc-file", ["name", "customer_id", "company_name", "cin", "trace_user_id", "trace_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency"]],
        "Professional Tax File": ["professional-tax-file", ["name", "customer_id", "assessee_name", "registration_no", "user_id", "trace_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency","enabled"]],
        "TDS File": ["tds-file", ["name", "customer_id", "deductor_name", "tan_no", "trace_user_id", "trace_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency"]],
        "ESI File": ["esi-file", ["name", "customer_id", "assessee_name", "registartion_no", "trace_user_id", "trace_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency"]],
        "Provident Fund File": ["provident-fund-file", ["name", "customer_id", "assessee_name", "registartion_no", "trace_user_id", "trace_password", "current_recurring_fees", "frequency", "annual_fees", "executive_name", "service_name", "description", "frequency","enabled"]],
    }
frequency_map={
                    "M":12,
                    "Q":4,
                    "H":2,
                    "Y":1,
                }
def execute(filters=None):
    columns, data = [], []

    # Define report columns
    columns = [
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 100},
        
        {"label": "File Type", "fieldname": "file_type", "fieldtype": "Link","options": "Customer", "width": 100},
        {"label": "File ID", "fieldname": "name", "fieldtype": "Dynamic Link", "options":"file_type", "width": 100},
        {"label": "File Name", "fieldname": "file_name", "fieldtype": "Data", "width": 150},
        # {"label": "Service Name", "fieldname": "service_name", "fieldtype": "Data", "width": 100},
        # {"label": "Enabled", "fieldname": "enabled", "fieldtype": "Check", "width": 50},
        {"label": "Current Recurring Fees", "fieldname": "current_recurring_fees", "fieldtype": "Currency", "width": 100},
        {"label": "Frequency", "fieldname": "frequency", "fieldtype": "Data", "width": 50},
        {"label": "Annual Fees", "fieldname": "annual_fees", "fieldtype": "Currency", "width": 100},
        
        # {"label": "Go To file", "fieldname": "go_to_file", "fieldtype": "HTML", "width": 90},
        {"label": "Ideal Quantity", "fieldname": "ideal_qty", "fieldtype": "Int", "width": 100},
        {"label": "Net Quantity", "fieldname": "net_qty", "fieldtype": "Int", "width": 100},
        {"label": "Quantity Difference", "fieldname": "qty_difference", "fieldtype": "Int", "width": 100},
        {"label": "Completion Status", "fieldname": "completion_status", "fieldtype": "Data", "width": 150},
        {"label": "Missing Months", "fieldname": "missing_months", "fieldtype": "Data", "width": 500},
        {"label": "Sales Order Count", "fieldname": "sales_order_count", "fieldtype": "Int", "width": 50},
        {"label": "Sales Order Details", "fieldname": "sales_order_details", "fieldtype": "Data", "width": 500},
    ]

    data = customer_services(filters)

    # Add JavaScript for row highlighting
    html_card = """
    <script>
        document.addEventListener('click', function(event) {
            var clickedCell = event.target.closest('.dt-cell__content');
            if (clickedCell) {
                var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
                previouslyHighlightedCells.forEach(function(cell) {
                    cell.classList.remove('highlighted-cell');
                    cell.style.backgroundColor = '';
                    cell.style.border = '';
                    cell.style.fontWeight = '';
                });

                var clickedRow = event.target.closest('.dt-row');
                var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
                cellsInClickedRow.forEach(function(cell) {
                    cell.classList.add('highlighted-cell');
                    cell.style.backgroundColor = '#d7eaf9';
                    cell.style.border = '2px solid #90c9e3';
                    cell.style.fontWeight = 'bold';
                });
            }
        });
    </script>
    """

    return columns, data, html_card

def customer_services(filters):
    
    fy=frappe.get_doc("FY",filters.get("fy"))
    advance_filter = {}
    
    if filters.get("customer_id"):
        advance_filter["customer_id"] = filters.get("customer_id")
    if filters.get("frequency_filter"):
        frequency_filter_l = [f.strip() for f in filters.get("frequency_filter").split(",") if f]
        advance_filter["frequency"] = ["in", frequency_filter_l]
    if filters.get("service_enabled"):
        if filters.get("service_enabled")=="Yes":
            advance_filter["enabled"] = 1
        else:
            advance_filter["enabled"] = 0


    

    service_master_filter={}
    if filters.get("service_master"):
        service_master_filter["name"] = filters.get("service_master")

    # Fetch all customers
    customers = frappe.get_all("Customer", filters={"disabled": 0}, fields=["name", "customer_name", "custom_contact_person", "custom_primary_mobile_no", "disabled", "custom_primary_email", "custom_customer_status_", "custom_customer_tags", "custom_customer_behaviour_", "custom_behaviour_note", "custom_customer_status_", "custom_state"])

    custome_map = {customer["name"]: {k: v for k, v in customer.items() if k != "name"} for customer in customers}

    services = frappe.get_all("Customer Chargeable Doctypes", 
                                                            # filters={
                                                            #             # "name": ("in", ["Gstfile", "Professional Tax File", "TDS File"]),
                                                            #            }, 
                                                            filters=service_master_filter,
                                                                        )

    # Fetch all sales orders and map them by their names
    so_list = frappe.get_all("Sales Order", filters={"docstatus": ("in", [0, 1]), 
                                                    #  "customer": "20130709",
													 "custom_so_from_date":(">=",fy.title),
													 "custom_so_to_date":("<=",fy.year_end_date),
                                                     }, fields=["name", "customer","owner"])
    so_dict={}
    for i in so_list:
        so_dict[i.name]=i
        # so_dict[i.name]["payment_status"]=""
        so_dict[i.name]["payment_status"]=so_payment_status(i.name)["payment_status"]


    # Fetch all sales order items and sum up quantities by item_code and customer_id
    soi_list = frappe.get_all("Sales Order Item", filters={"docstatus": ("not in", [2]), 
                                                           "parent": ("not in", [None]),
														   "custom_soi_from_date":(">=",fy.title),
														   "custom_soi_to_date":("<=",fy.year_end_date),
                                                           }, 
                                                           fields=["name", "parent", "item_code", "rate", "description", "qty","custom_soi_from_date","custom_soi_to_date"], 
                                                           order_by="item_code asc")
    
    soi_qty_map = {}
    for soi in soi_list:
        if soi.parent in so_dict:
            # print(soi)
            customer_id = so_dict[soi.parent]["customer"]
            item_key = (soi.item_code, customer_id)
            from_date=str(soi.custom_soi_from_date)[5:7]+"-"+str(soi.custom_soi_from_date)[2:4]
            to_date=str(soi.custom_soi_to_date)[5:7]+"-"+str(soi.custom_soi_to_date)[2:4]
            so_details = f"{soi.parent}(INR {soi.rate}/-)({soi.qty})({so_dict[soi.parent]['payment_status']}) From {from_date} To {to_date} By {so_dict[soi.parent]['owner']}"
            if item_key not in soi_qty_map:
                # print(type(soi.custom_soi_from_date))
                
                soi_qty_map[item_key] = [soi.qty,[(soi.custom_soi_from_date,soi.custom_soi_to_date)],[so_details]]
            else:
                soi_qty_map[item_key][0] += soi.qty
                soi_qty_map[item_key][1] += [(soi.custom_soi_from_date,soi.custom_soi_to_date)]
                soi_qty_map[item_key][2] += [so_details]

    data = []

    for service in services:
        customer_services = frappe.get_all(service.name, fields=master_service_fields[service.name][1], filters=advance_filter)
        if True:
            for customer_service in customer_services:
                if customer_service["customer_id"] not in custome_map:
                    continue
                service_frequency=customer_service.frequency
                yearly_frequency_count=frequency_map[service_frequency]
                # Calculate net quantity
                item_key = (customer_service["service_name"], customer_service["customer_id"])
                net_qty=0
                missing_months=['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December','January', 'February', 'March']
                sales_order_count=0
                sales_order_details=""
                if item_key in soi_qty_map:
                    net_qty = soi_qty_map[item_key][0]
                    missing_months=get_missing_months_in_fy(fy.title,fy.year_end_date,soi_qty_map[item_key][1])
                    sales_order_count=len(soi_qty_map[item_key][2])
                    sales_order_details=", \n".join(soi_qty_map[item_key][2])
                    

                completion_status =  "No Biling"
                if net_qty == yearly_frequency_count:
                    completion_status = "Complete Biling"
                elif net_qty > yearly_frequency_count:
                    completion_status = "Extra Biling"
                elif net_qty > 0:
                    completion_status = "Incomplete Biling"

                custome_map_value = custome_map.get(customer_service["customer_id"], {})
                customer_service.update(custome_map_value)
                customer_service.update({
                    "file_type":service.name,
                    "file_name":customer_service[master_service_fields[service.name][1][2]],
                    "go_to_file": f"<button class='btn btn-xs btn-primary' title='{service.name}' onclick=\"frappe.set_route('Form', '{service.name}', '{customer_service['name']}')\">View File</button>",
                    "ideal_qty":yearly_frequency_count,
					"net_qty": net_qty,
                    "qty_difference":(yearly_frequency_count-net_qty),
                    "completion_status": completion_status,
                    "missing_months": ", ".join(missing_months),
                    "sales_order_count": sales_order_count,
                    "sales_order_details": sales_order_details,

                })

                data.append(customer_service)

    return data




def get_missing_months_in_fy(fy_start_date, fy_end_date, date_ranges):
    try:
        # Helper function to get all months in a given range
        def get_months_in_range(start_date, end_date):
            months = set()
            # Ensure dates are datetime.date
            start_date = start_date if isinstance(start_date, date) else start_date.date()
            end_date = end_date if isinstance(end_date, date) else end_date.date()

            current = start_date
            while current <= end_date:
                months.add(calendar.month_name[current.month])
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
            return months

        # Ensure fiscal year dates are datetime.date
        fy_start = fy_start_date if isinstance(fy_start_date, date) else fy_start_date.date()
        fy_end = fy_end_date if isinstance(fy_end_date, date) else fy_end_date.date()

        # All months in the fiscal year
        all_months_in_fy = get_months_in_range(fy_start, fy_end)

        # Collect covered months from all date ranges
        covered_months = set()
        for date_range in date_ranges:
            start_date, end_date = date_range
            covered_months.update(get_months_in_range(start_date, end_date))

        # Determine missing months
        missing_months = sorted(all_months_in_fy - covered_months, key=lambda x: list(calendar.month_name).index(x))
        return missing_months
    except Exception as e:
        #  print("errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",e)
         frappe.log_error(f"Error while getting missing biling months in 'Missing SO before 2024 for Recurring Services' Report: {e}")



