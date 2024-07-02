# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

# import frappe

# Import necessary modules from frappe
import frappe
from frappe.utils import escape_html

# Define the main function to generate the report based on filters
def execute(filters=None):
    # Define columns for the report
    columns = [
        # Customer details columns
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100, "height": 100},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200, "height": 100},
        
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 150, },
        {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 120, },
        {"label": "Email", "fieldname": "custom_primary_email", "fieldtype": "Data", "width": 150, },
        

        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100, "height": 100},
        {"label": "Enabled", "fieldname": "enable", "fieldtype": "Data", "width": 50, "height": 100},

        #RSP
        {"label": "RSP", "fieldname": "rsp", "fieldtype": "Link", "options": "Recurring Service Pricing", "width": 100, "height": 100},

        # Sales Order related columns
        {"label": "Service Count", "fieldname": "service_count", "fieldtype": "Int", "width": 100, "height": 100},
        {"label": "Service Amount", "fieldname": "service_amount", "fieldtype": "Currency", "width": 100, "height": 100},
        {"label": "SO Count", "fieldname": "so_count", "fieldtype": "Int","default": "0", "width": 100, "height": 100},

        {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "Data", "width": 100, "height": 100},
        {"label": "Customer Behaviour", "fieldname": "custom_customer_behaviour_", "fieldtype": "Data", "width": 100, "height": 100},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 100, "height": 100},

        {"label": "Pending Amount", "fieldname": "pending_amount", "fieldtype": "Currency","default": "0", "width": 100, "height": 100},
    ]
    
    # Get all service doctypes from "Customer Chargeable Doctypes"
    unsorted_services = frappe.get_all("Customer Chargeable Doctypes", fields=["name", "doctype_name"])
    
    # Calculate the count for each service doctype
    counts = {service.doctype_name: len(frappe.get_all(service.doctype_name)) for service in unsorted_services}
    
    # Sort the services based on the counts in descending order
    services = sorted(unsorted_services, key=lambda x: counts[x["doctype_name"]], reverse=True)
    
    # Add columns for each service
    for service in services:
        # Add column for service count
        servic_doc = {"label": str(service.doctype_name)[:-4] + " Count", "fieldname": service.name + " count", "fieldtype": "Int","default": "0", "width": 50, "height": 100}
        columns.append(servic_doc)
        
        # Add column for service amount
        servic_doc = {"label": str(service.doctype_name)[:-4] + " Amount", "fieldname": service.name + " amount", "fieldtype": "Currency","default": "0", "width": 100, "height": 100}
        columns.append(servic_doc)

        if service.doctype_name=="Gstfile":
            # Add column for service amount
            servic_doc = {"label": "GST Type", "fieldname": "gst_type", "fieldtype": "Data", "width": 100, "height": 100}
            columns.append(servic_doc)

        # Add column for service customer details
        servic_doc = {"label": str(service.doctype_name)[:-4] + " Customer", "fieldname": service.name + " customer", "fieldtype": "Text Editor", "width": 250, "height": 100}
        columns.append(servic_doc)
    print(columns)
    # Get data for the report
    data = get_data(services, filters)


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
def get_data(services, filters):
    data = []

    service_masters=frappe.get_all("Customer Chargeable Doctypes")
    service_masters=[ser.name for ser in service_masters]
    
    # Extract filters
    service_filter = filters.get("service_user")
    status_filter = filters.get("status")
    enabled_filter = filters.get("enabled")

    # Get all customers
    customers = frappe.get_all("Customer", 
                               fields=["name", "customer_name", "custom_contact_person", "custom_primary_mobile_no",
                                       "custom_primary_email","disabled","custom_customer_status_","custom_customer_tags",
                                       "custom_customer_behaviour_","custom_customer_status_"])
    
    unsettled_sales_orders = frappe.get_all(
                "Sales Order",
                fields=["name","customer", "rounded_total","advance_paid","status"], 
                )
    rsp_list = frappe.get_all(
                "Recurring Service Pricing",
                filters={"status":"Approved"},
                fields=["name","customer_id"], 
                ) 
    rsp_dict={rs.customer_id:rs.name for rs in rsp_list}

    sos={}
    for unsettled_sales_order in unsettled_sales_orders:
        if unsettled_sales_order["customer"] in sos:
            sos[unsettled_sales_order["customer"]]+=[{z:unsettled_sales_order[z] for z in unsettled_sales_order if z!= "customer"}]
        else:
            sos[unsettled_sales_order["customer"]]=[{z:unsettled_sales_order[z] for z in unsettled_sales_order if z!= "customer"}]
    del unsettled_sales_orders
    customer_services={}
    for service in services:
            # Get services for the customer
            if service.doctype_name=="Gstfile":
                service_i = frappe.get_all(
                                        service.doctype_name,
                                        fields=["customer_id","description", "current_recurring_fees","annual_fees","frequency","gst_type"], 
                                        filters={"enabled": 1}
                                        )
                for s in service_i:
                    # print(s)
                    # print(s.customer_id)
                    # print(service)
                    if s.customer_id not in customer_services:
                        customer_services[s.customer_id]={}
                        customer_services[s.customer_id][service["name"]]=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                    elif service["name"] not in customer_services[s.customer_id]:
                        customer_services[s.customer_id][service["name"]]=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                    else:
                        customer_services[s.customer_id][service["name"]]+=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                    # break
                del service_i
            else:
                service_i = frappe.get_all(
                                        service.doctype_name,
                                        fields=["customer_id","description", "current_recurring_fees","annual_fees","frequency"], 
                                        filters={"enabled": 1}
                                        )
                for s in service_i:
                    # print(s)
                    if s.customer_id not in customer_services:
                        customer_services[s.customer_id]={}
                        customer_services[s.customer_id][service["name"]]=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                        # if s.customer_id =="20130221":
                        #     print(s)
                        #     l=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                        #     print(l)
                    elif service["name"] not in customer_services[s.customer_id]:
                        customer_services[s.customer_id][service["name"]]=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                    else:
                        customer_services[s.customer_id][service["name"]]+=[{s_i:s[s_i] for s_i in s if s_i!= "customer_id"}]
                    # break
                    
                del service_i
    # customer_services={}
                

    # Iterate through each customer
    # print(len(customers))

    # print(len(customer_services))

    for i in customers:
        data_row = {
            "customer_id": i.name,
            "customer_name": i.customer_name,

            "custom_contact_person": i.custom_contact_person,
            "mobile number": i.custom_primary_mobile_no,
            "custom_primary_email": i.custom_primary_email,

            "status": i.custom_customer_status_,
            "custom_customer_tags":i.custom_customer_tags,
            "custom_customer_behaviour_":i.custom_customer_behaviour_,
            "custom_customer_status_":i.custom_customer_status_,
        }

        # Set enable status based on 'disabled' field
        data_row["enable"] = "No" if i.disabled else "Yes"

        if i.name in rsp_dict:
            data_row["rsp"] = rsp_dict[i.name]
        else:
            data_row["rsp"] = None

        # Sales Order Details associated with Customer
        # unsettled_sales_orders = frappe.get_all(
        #         "Sales Order",
        #         fields=["name", "rounded_total","advance_paid","status"], 
        #         filters={"customer": i.name}
        #         )


        if i.name in sos:
            unsettled_sales_orders_c=sos[i.name]

            filtered_unsettled_sales_orders = []
            net_unsettled_sales_order_amount = 0.00
            net_sales_order_amount = 0.00
            for unsettled_sales_order in unsettled_sales_orders_c:
                if unsettled_sales_order["status"] != "Cancelled" and \
                unsettled_sales_order["rounded_total"] > unsettled_sales_order["advance_paid"]:
                    filtered_unsettled_sales_orders.append(unsettled_sales_order)
                    net_sales_order_amount += unsettled_sales_order["rounded_total"]
                    net_unsettled_sales_order_amount += unsettled_sales_order["rounded_total"] - unsettled_sales_order["advance_paid"]
            data_row["so_count"] = len(filtered_unsettled_sales_orders)
            data_row["pending_amount"] = net_unsettled_sales_order_amount
        else:
            data_row["so_count"] = 0
            data_row["pending_amount"] = 0.00

        c=0
        service_count = 0
        service_amount = 0.00
        # Iterate through each service doctype
        # print(customer_services["20130221"])
        if True:
            for service in service_masters:
                # Get services for the customer

                description_value = []
                each_service_amount = 0.00
                gst_type_gstfile = []
                master_service_count=0
                if i.name in customer_services and service in customer_services[i.name]:
                    # Iterate through each service record
                    for j in customer_services[i.name][service]:
                        if not(j["description"] is None):
                            description_list = j["description"].split("-")
                        else:
                            description_list=["NA","NA"]

                        if len(description_list) == 2:
                            description_value += [f"{description_list[0]}-({description_list[1]})-{j['frequency']}-(Rs {j['current_recurring_fees']})"]
                        else:
                            description_value += [f"{description_list[0]}-{j['frequency']}-(Rs {j['current_recurring_fees']})"]
                        
                        if service=="Gstfile":
                            gst_type_gstfile.append(j["gst_type"])
                        service_count += 1
                        if j["annual_fees"]:
                            each_service_amount += j["annual_fees"]

                        if j["annual_fees"]:
                            service_amount += j["annual_fees"]
                        master_service_count+=1
                
                
                    if service=="Gstfile":
                            gst_type_gstfile=[l for l in gst_type_gstfile if not(l is None)]
                            gst_type_gstfile=", ".join(gst_type_gstfile)
                            data_row["gst_type"] = gst_type_gstfile

                    # Set description value for service customer

                data_row[service + " customer"] = ", \n".join(description_value)
                data_row[service + " count"] = master_service_count
                data_row[service + " amount"] = each_service_amount


            # Set total service count and amount for the customer
            data_row["service_count"] = service_count
            data_row["service_amount"] = service_amount
            c+=1

        data += [data_row]
    
    # Filter data based on service_user
    filtered_data=[]
    for d in data:
        service=False
        customer_status=False
        customer_enabled=False
        if service_filter and service_filter!="All":
            if service_filter == "Customers without Services" and d["service_count"] == 0:
                service=True
            elif service_filter == "Customers with Services" and d["service_count"] != 0:
                service=True
        else:
            service=True
        if status_filter and status_filter!="All":
            if status_filter==d["status"]:
                customer_status=True
        else:
            customer_status=True

        if enabled_filter and enabled_filter!="All":
            if enabled_filter==d["enable"]:
                customer_enabled=True
        else:
            customer_enabled=True
        
        if service and customer_status and customer_enabled:
            filtered_data.append(d)

    # print(len(filtered_data))
    return filtered_data










