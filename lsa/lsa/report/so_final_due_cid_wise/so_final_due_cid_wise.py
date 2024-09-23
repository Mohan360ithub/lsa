import frappe

def execute(filters=None):
    columns = [
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 150},
        {"label": "Pending Amount", "fieldname": "pending_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Next Followup Date", "fieldname": "next_followup_date", "fieldtype": "Date", "width": 120},
        {"label": "Last Comment", "fieldname": "last_comment", "fieldtype": "Text", "width": 200},
        {"label": "Mobile No.", "fieldname": "mobile_number", "fieldtype": "Data", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Client Group", "fieldname": "custom_client_group", "fieldtype": "Link", "options": "Client Group", "width": 100},
        {"label": "Group Name", "fieldname": "group_name", "fieldtype": "Data", "width": 150},  # New column for group name
        {"label": "SO Count", "fieldname": "so_count", "fieldtype": "HTML", "width": 100},
        {"label": "1st SO From Date", "fieldname": "first_so_from_date", "fieldtype": "Date", "width": 120},
        {"label": "Last SO To Date", "fieldname": "last_so_to_date", "fieldtype": "Date", "width": 120},
        {"label": "Grand Total", "fieldname": "grand_total", "fieldtype": "Currency", "width": 100},
        {"label": "Received Amount", "fieldname": "received_amount", "fieldtype": "Currency", "width": 100},
        
        {"label": "Total FollowUp Count", "fieldname": "total_followup_count", "fieldtype": "Int", "width": 120},
        {"label": "Last Followup Done Date", "fieldname": "last_followup_done_date", "fieldtype": "Date", "width": 120},
        
        
    ]
    
    # Get data for the report
    data, html = get_data(filters)

    return columns, data, html


def get_data(filters):
    html = """
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
    
    customer_filter = filters.get("customer")
    status_filter = filters.get("status")
    client_group_filter = filters.get("client_group", [])
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Build SQL conditions
    customer_condition = "1=1" if not customer_filter else "c.name = %s"
    status_condition = "1=1" if status_filter == "All" else "c.custom_customer_status_ = %s"

    if client_group_filter:
        client_group_placeholders = ', '.join(['%s'] * len(client_group_filter))
        client_group_condition = f"c.custom_client_group IN ({client_group_placeholders})"
    else:
        client_group_condition = "1=1"  # No filter on client group
    
    date_conditions = []
    if from_date:
        date_conditions.append("so.custom_so_from_date >= %s")
    if to_date:
        date_conditions.append("so.custom_so_to_date <= %s")

    date_condition = " AND ".join(date_conditions) if date_conditions else "1=1"

    sql_query = f"""
    SELECT 
        c.name AS `customer_id`,
        c.customer_name,
        c.custom_client_group,
        cg.group_name AS `group_name`,  -- Fetch the group name
        c.custom_contact_person,
        c.mobile_no AS `mobile_number`,
        c.custom_customer_status_ AS `status`,
        COALESCE(SUM(so.rounded_total), 0) AS `grand_total`,
        COALESCE(SUM(so.advance_paid), 0) AS `received_amount`,
        COALESCE(SUM(so.rounded_total) - SUM(so.advance_paid), 0) AS `pending_amount`,
        COUNT(so.name) AS `so_count`,
        MIN(so.custom_so_from_date) AS `first_so_from_date`,
        MAX(so.custom_so_to_date) AS `last_so_to_date`,
        COALESCE(f.total_followup_count, 0) AS `total_followup_count`,
        f.last_followup_done_date,
        f.last_comment,
        f.next_followup_date
    FROM 
        `tabCustomer` AS c
    LEFT JOIN 
        `tabSales Order` AS so ON c.name = so.customer
    LEFT JOIN 
        `tabClient Group` AS cg ON c.custom_client_group = cg.name  -- Join to get group name
    LEFT JOIN 
        (
            SELECT 
                customer_id,
                COUNT(name) AS total_followup_count,
                MAX(followup_date) AS last_followup_done_date,
                MAX(followup_note) AS last_comment,
                MAX(next_followup_date) AS next_followup_date
            FROM 
                `tabCustomer Followup`
            GROUP BY 
                customer_id
        ) AS f ON c.name = f.customer_id
    WHERE 
        c.disabled = 0
        AND {customer_condition}
        AND so.docstatus IN (0, 1)
        AND {status_condition}
        AND {client_group_condition}
        AND {date_condition}
    GROUP BY 
        c.name, c.customer_name, c.custom_contact_person, c.mobile_no, c.custom_customer_status_, cg.group_name
    HAVING 
        pending_amount > 0  -- Exclude records with pending_amount = 0
    """

    
    # Prepare parameters
    params = []
    if customer_filter:
        params.append(customer_filter)
    if status_filter != "All":
        params.append(status_filter)
    if client_group_filter:
        params.extend(client_group_filter)
    if from_date:
        params.append(from_date)
    if to_date:
        params.append(to_date)

    # Execute SQL query
    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
    
    # Format the 'so_count' column to be clickable
    for row in data:
        row['so_count'] = f'<a href="#" onclick="openSalesOrders(\'{row["customer_id"]}\')">{row["so_count"]}</a>'

    return data, html



@frappe.whitelist()
def get_prompt_so(customer_id):
    sales_orders = frappe.get_all(
        "Sales Order", 
        fields=["name", "rounded_total", "status", "custom_so_from_date", "custom_so_to_date", "advance_paid"], 
        filters={"customer": customer_id, "status": ["!=", "Cancelled"]}
    )
    
    # Add calculation fields
    for order in sales_orders:
        order['paid_amount'] = order['advance_paid']
        order['balance_amount'] = order['rounded_total'] - order['advance_paid']
        
        if order['advance_paid'] >= order['rounded_total']:
            order['payment_status'] = "Paid"
        elif order['advance_paid'] > 0:
            order['payment_status'] = "Partially Paid"
        else:
            order['payment_status'] = "Unpaid"
    
    return sales_orders


