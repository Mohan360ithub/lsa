// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["So Final Due CID Wise"] = {
    "filters": [
        {
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "Link",
            options: "Customer",
            // default: "All",
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: ["All", "ACTIVE", "HOLD"],
            default: "All",
        }, 
        {
            "fieldname": "client_group",
            "label": __("Client Group"),
            "fieldtype": "MultiSelectList",
            "options": "Client Group",
            "get_data": function (txt) {
                return frappe.db.get_link_options("Client Group", txt);
            }
        },
        {
            fieldname: "from_date",
            label: __("Sales Order From Date"),
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: __("Sales Order To Date"),
            fieldtype: "Date",
        }      
        
    ]
};

// Define the openSalesOrders function outside the query_reports configuration
function openSalesOrders(customer_id) {
    // Create a dialog with a placeholder for the HTML table
    const d = new frappe.ui.Dialog({
        title: 'Sales Orders for Customer: ' + customer_id,
        fields: [
            {
                label: 'Sales Orders',
                fieldname: 'sales_orders_html',
                fieldtype: 'HTML'
            }
        ]
    });

    // Show the dialog
    d.show();

    // Call the server-side method to fetch sales orders for the customer
    frappe.call({
        method: "lsa.lsa.report.so_final_due_cid_wise.so_final_due_cid_wise.get_prompt_so",
        args: {
            customer_id: customer_id
        },
        callback: function(response) {
            if (response.message) {
                // Prepare the HTML table with sales order data
                let salesOrders = response.message;
                let html = `<table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Order Name</th>
                                        <th>SO From Date</th>
                                        <th>SO To Date</th>
                                        <th>Amount</th>
                                        <th>Paid Amount</th>
                                        <th>Balance Amount</th>
                                        <th>Payment Status</th>
                                    </tr>
                                </thead>
                                <tbody>`;

                // Iterate through sales orders and append rows to the table
                salesOrders.forEach(order => {
                    html += `<tr>
                                <td><a href="/app/sales-order/${order.name}" target="_blank">${order.name}</a></td>
                                <td>${order.custom_so_from_date}</td>
                                <td>${order.custom_so_to_date}</td>
                                <td>${order.rounded_total}</td>
                                <td>${order.paid_amount}</td>
                                <td>${order.balance_amount}</td>
                                <td>${order.payment_status}</td>
                            </tr>`;
                });

                html += `   </tbody>
                        </table>`;

                // Set the HTML content in the dialog
                d.fields_dict.sales_orders_html.$wrapper.html(html);
            } else {
                // Show a message if there are no sales orders
                d.fields_dict.sales_orders_html.$wrapper.html("<p>No Sales Orders found for this customer.</p>");
            }
        }
    });
}

