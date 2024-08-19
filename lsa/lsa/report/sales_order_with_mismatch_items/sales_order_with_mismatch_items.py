
        
import frappe
from datetime import datetime
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns
        {"label": "ID", "fieldname": "so_id", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": "SO Status", "fieldname": "doc_status", "fieldtype": "Data", "width": 65},
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 90},
        {"label": "Company Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 125},
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 110},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 65},
        {"label": "FollowUp Count", "fieldname": "followup_count", "fieldtype": "Int", "width": 30},
        {"label": "Rounded Total", "fieldname": "rounded_total", "fieldtype": "Currency", "width": 100},
        {"label": "SO Approved", "fieldname": "custom_approval_status", "fieldtype": "Data", "width": 100},

        {"label": "SO From Date", "fieldname": "custom_so_from_date", "fieldtype": "Date", "width": 110},
        {"label": "SO To Date", "fieldname": "custom_so_to_date", "fieldtype": "Date", "width": 110},
        {"label": "Items WO Service Ref", "fieldname": "item_wo_service_ref", "fieldtype": "Small Text", "width": 300},
        {"label": "Payment Status", "fieldname": "payment_status", "fieldtype": "Data", "width": 100},
    ]

    # Get data for the report
    data = get_data(filters)

    html_card = """
</div>

    <script>
        document.addEventListener('click', function(event) {
            // Check if the clicked element is a cell
            var clickedCell = event.target.closest('.dt-cell__content');
            if (clickedCell) {
                // Remove highlight from previously highlighted cells
                var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
                previouslyHighlightedCells.forEach(function(cell) {
                    cell.classList.remove('highlighted-cell');
                    cell.style.backgroundColor = ''; // Remove background color
                    cell.style.border = ''; // Remove border
                    cell.style.fontWeight = '';
                });
                
                // Highlight the clicked row's cells
                var clickedRow = event.target.closest('.dt-row');
                var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
                cellsInClickedRow.forEach(function(cell) {
                    cell.classList.add('highlighted-cell');
                    cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
                    cell.style.border = '2px solid #90c9e3'; // Border color
                    cell.style.fontWeight = 'bold';
                });
            }
        });
    </script>
    """

    return columns, data, html_card


# Function to retrieve data based on filters
def get_data(filters):
    data = []
    doc_status_map_reverse = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
    additional_filters = {}
    item_filters = {
        "item_code": ("in", ["GST Filling", "PT Filling", "TDS Filling", "Incometax Filing", "ROC Filling"]),
        "custom_service_master": ("in", [None])
    }
    customer_filter={}
    if filters:
        if filters.get("customer_id"):
            additional_filters["customer"] = filters.get("customer_id")
        if filters.get("doc_status"):
            status_list = filters.get("doc_status").split(',')
            status_list = [z.strip() for z in status_list if z.isalpha()]
            status_list = [doc_status_map_reverse[x] for x in status_list]
            additional_filters["docstatus"] = ["in", status_list]
            item_filters["docstatus"] = ["in", status_list]
        if filters.get("from_date"):
            additional_filters["custom_so_from_date"] = [">=", filters.get("from_date")]
            item_filters["custom_soi_from_date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            additional_filters["custom_so_to_date"] = ["<=", filters.get("to_date")]
            item_filters["custom_soi_to_date"] = ["<=", filters.get("to_date")]
        if filters.get("customer_enabled_filter"):
            if filters.get("customer_enabled_filter")=="Customer Enabled":
                customer_filter["disabled"] = 0
            else:
                customer_filter["disabled"] = 1

    sales_orders = frappe.get_all(
        "Sales Order",
        filters=additional_filters,
        fields=["name", "customer", "customer_name", "contact_mobile", "custom_so_from_date", "custom_so_to_date",
                "transaction_date", "rounded_total", "docstatus", "custom_followup_count", "custom_approval_status","advance_paid"]
    )

    sales_order_items = frappe.get_all(
        "Sales Order Item",
        filters=item_filters,
        fields=["name", "item_code", "parent"]
    )

    soi_so = {}
    for soi in sales_order_items:
        if soi.parent not in soi_so:
            soi_so[soi.parent] = [(soi.item_code, soi.name)]
        else:
            soi_so[soi.parent] += [(soi.item_code, soi.name)]

    cu = []
    for cu_so in sales_orders:
        if cu_so.customer not in cu:
            cu.append(cu_so.customer)

    cu_s = frappe.get_all(
							"Customer",
							filters=customer_filter,
							fields=["name", "custom_customer_tags", "custom_customer_behaviour_", "custom_behaviour_note",
									"custom_customer_status_", "custom_contact_person", "custom_primary_mobile_no", "custom_primary_email", "disabled"]
						)

    cu_l = {}
    for cu in cu_s:
        cu_l[cu["name"]] = {cu_i: cu[cu_i] for cu_i in cu if cu_i != "name"}

    cu_s = cu_l

    for so in sales_orders:
        doc_status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
        # Determine payment status
        if so.advance_paid >= so.rounded_total:
            payment_status = "Paid"
        elif so.advance_paid > 0:
            payment_status = "Partially Paid"
        else:
            payment_status = "Unpaid"
        # if so.customer in cu_s and so.name in soi_so and cu_s[so.customer]["custom_customer_status_"] in filters.get("custom_customer_status_"):
        if so.customer in cu_s and so.name in soi_so :
            data_row = {
                "so_id": so.name,
                "customer_id": so.customer,
                "customer_name": so.customer_name,
                "custom_contact_person": cu_s[so.customer]["custom_contact_person"],
                "mobile number": cu_s[so.customer]["custom_primary_mobile_no"],
                "custom_customer_behaviour_": cu_s[so.customer]["custom_customer_behaviour_"],
                "custom_behaviour_note": cu_s[so.customer]["custom_behaviour_note"],
                "custom_customer_status_": cu_s[so.customer]["custom_customer_status_"],
                "custom_customer_disabled_": cu_s[so.customer]["disabled"],
                "custom_so_from_date": so.custom_so_from_date,
                "custom_so_to_date": so.custom_so_to_date,
                "transaction_date": so.transaction_date,
                "rounded_total": so.rounded_total,
                "custom_approval_status": so.custom_approval_status,
                "doc_status": doc_status_map[so.docstatus],
                "custom_followup_count": so.custom_followup_count,
                "payment_status": payment_status,
            }
            items=soi_so[so.name]
            summary={}
            for item in items:
                if item[0] not in summary:
                    summary[item[0]]=1
                else:
                    summary[item[0]]+=1
            lst_summary=[f"{it}({summary[it]})" for it in summary]
            str_summary=", ".join(lst_summary)
            data_row["item_wo_service_ref"]=str_summary

            data += [data_row]

    return data



