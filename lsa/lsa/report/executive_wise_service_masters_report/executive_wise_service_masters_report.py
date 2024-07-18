# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
    columns, data = [], []
     
    columns=[
        {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100, },
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200, },
        {"label": "Contact Person", "fieldname": "custom_contact_person", "fieldtype": "Data", "width": 150, },
        # {"label": "Mobile No.", "fieldname": "mobile number", "fieldtype": "Data", "width": 120, },
        # {"label": "Email", "fieldname": "custom_primary_email", "fieldtype": "Data", "width": 150, },
        # {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100, },
        # {"label": "Enabled", "fieldname": "enabled", "fieldtype": "Data", "width": 50, },
        # {"label": "Customer Payment Agree", "fieldname": "custom_customer_tags", "fieldtype": "Data", "width": 100, },
        # {"label": "Customer Behaviour", "fieldname": "custom_customer_behaviour_", "fieldtype": "Data", "width": 100, },
        # {"label": "Behaviour Note", "fieldname": "custom_behaviour_note", "fieldtype": "Data", "width": 100},
        {"label": "Customer Status", "fieldname": "custom_customer_status_", "fieldtype": "Data", "width": 100, },
        
        {"label": "Executive", "fieldname": "executive", "fieldtype": "Link","options":"User", "width": 100, },
        {"label": "Executive Name", "fieldname": "executive_name", "fieldtype": "Data", "width": 100, },
        
        {"label": "Service Name", "fieldname": "service_name", "fieldtype": "Data", "width": 100, },
        {"label": "File ID", "fieldname": "file_id", "fieldtype": "HTML", "width": 100, },
        {"label": "File Type", "fieldname": "file_type", "fieldtype": "Data", "width": 100, },
        
        {"label": "Go To file", "fieldname": "go_to_file", "fieldtype": "HTML", "width": 90, },
        
        # {"label": "Name", "fieldname": "contact_name", "fieldtype": "Data", "width": 100, },
        # {"label": "User Name", "fieldname": "user_name", "fieldtype": "Data", "width": 100, },
        # {"label": "Password", "fieldname": "password", "fieldtype": "Data", "width": 100, },
        {"label": "Current Recurring Fees", "fieldname": "current_recurring_fees", "fieldtype": "Currency", "width": 100, },
        {"label": "Frequency", "fieldname": "frequency", "fieldtype": "Data", "width": 100, },
        {"label": "Annual Fees", "fieldname": "annual_fees", "fieldtype": "Currency", "width": 100, },
        
        
    ]
     
    data = customer_services(filters)
    html_card = """

    <div style="width:100%; display: flex; justify-content: flex-end; align-items: center;">
    <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="myFunction()">
        <b style="color: #000000;">Reassign Executives</b>
    </button>
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

	 

def customer_services(filters):

    master_service_fields = {
        "Gstfile": ["gstfile", ["name","customer_id", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive","executive_name","gst_type"]],
        "IT Assessee File": ["it-assessee-file", ["name","customer_id", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
        "MCA ROC File": ["mca-roc-file", ["name","customer_id", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
        "Professional Tax File": ["professional-tax-file", ["name","customer_id", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
        "TDS File": ["tds-file", ["name","customer_id", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
        "ESI File": ["esi-file", ["name","customer_id", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
        "Provident Fund File": ["provident-fund-file", ["name","customer_id", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive","executive_name"]],
    }
    customer_id = filters.get("customer_id")
    service_name = filters.get("service_name")
    frequency_filter = filters.get("frequency_filter")
    executive = filters.get("executive")
    assigned_executive= filters.get("assigned_executive")

    advance_filter={"enabled": 1}
    
    if customer_id:
        advance_filter["customer_id"]=customer_id
    if frequency_filter:
        frequency_filter_l=frequency_filter.split(",")
        frequency_filter_l=[f.strip() for f in frequency_filter_l if f]
        print(frequency_filter_l)
        advance_filter["frequency"]=["in",frequency_filter_l]
    if executive and assigned_executive:
        advance_filter["executive"]=executive
    if not assigned_executive:
        advance_filter["executive"]=["in",[None]]


    # Get all customers
    customers = frappe.get_all("Customer",
                               fields=["name", "customer_name","custom_contact_person","custom_primary_mobile_no",
                                       "disabled","custom_primary_email","custom_customer_status_",
                                       "custom_customer_tags","custom_customer_behaviour_","custom_behaviour_note",
                                        "custom_customer_status_"])

    custome_map={}
    for customer in customers:
        custome_map[customer["name"]]={z:customer[z] for z in customer if z!= "name"}

    del customers
    services = frappe.get_all("Customer Chargeable Doctypes", fields=["name"])

    data=[]

    for service in services:
        customer_services = frappe.get_all(service.name,
                                    fields=master_service_fields[service.name][1],
                                    filters=advance_filter
                                    )
        slug_service="-".join([se.lower() for se in service.name.split(" ")])
        if not(service_name) or service_name==service.name:
            for customer_service in customer_services:
                file_link=f'<a href = "https://online.lsaoffice.com/app/{slug_service}/{customer_service[master_service_fields[service.name][1][0]]}"> {customer_service[master_service_fields[service.name][1][0]]} </a>'
                
                cid=customer_service["customer_id"]
                data_row = {
                    "customer_id": cid,
                    "customer_name": custome_map[cid]["customer_name"],
                    "custom_contact_person": custome_map[cid]["custom_contact_person"],
                    "mobile number": custome_map[cid]["custom_primary_mobile_no"],
                    "custom_primary_email": custome_map[cid]["custom_primary_email"],
                    # "enabled": custome_map[cid]["disabled"],
                    "status": custome_map[cid]["custom_customer_status_"],
                    "custom_customer_tags":custome_map[cid]["custom_customer_tags"],
                    "custom_customer_behaviour_":custome_map[cid]["custom_customer_behaviour_"],
                    "custom_behaviour_note":custome_map[cid]["custom_behaviour_note"],
                    "custom_customer_status_":custome_map[cid]["custom_customer_status_"],

                    "service_name":service.name,
                    "file_id":file_link,
                    "contact_name":customer_service[master_service_fields[service.name][1][2]],
                    "user_name":customer_service[master_service_fields[service.name][1][4]],
                    "password":customer_service[master_service_fields[service.name][1][5]],
                    "current_recurring_fees":customer_service[master_service_fields[service.name][1][6]],
                    "frequency":customer_service[master_service_fields[service.name][1][7]],
                    "annual_fees":customer_service[master_service_fields[service.name][1][8]],
                    "executive_name":customer_service[master_service_fields[service.name][1][10]],
                    "executive":customer_service[master_service_fields[service.name][1][9]],
                }
                if service.name=="Gstfile":
                    data_row["file_type"]=customer_service[master_service_fields[service.name][1][10]]
                else:
                    data_row["file_type"]="Non-GST"

                if custome_map[cid]["disabled"]==0:
                    data_row["enabled"]="Yes"
                else:
                    data_row["enabled"]="No"
                    continue
                data_row["go_to_file"]=f'''<a href="https://online.lsaoffice.com/app/{master_service_fields[service.name][0]}/{customer_service[master_service_fields[service.name][1][0]]}">
                                        <button class="btn btn-sm" style="background-color:#BCBCBC; height:20px; font-size: 12px;   text-align: center; display: inline-block; ">
                                        <b>Go To File</b></button></a>
                                        '''

                data.append(data_row)
        del customer_services

    return data


def get_services():
    services = frappe.get_all("Customer Chargeable Doctypes", fields=["name"])
    services = [ser.name for ser in services]
    return json.dumps(services)



@frappe.whitelist()
def erp_last_checkin(service,new_exe,old_exe=None):
        
    if old_exe:
        service_masters_list = frappe.get_all(service, filters={"executive":old_exe})
        if not service_masters_list:
            return {"status":False,"msg":f"No {service} found with {old_exe} as executive"}
    else:
        service_masters_list = frappe.get_all(service, filters={"executive":("in",[None])})
        if not service_masters_list:
            return {"status":False,"msg":f"No record found in Service Master {service}"}
    try:
        
        for serv in service_masters_list:
            
            service_masters_doc = frappe.get_doc(service,serv.name)
            service_masters_doc.executive=new_exe
            service_masters_doc.save()

            service_assignment_doc = frappe.new_doc('Service Executive Assignment')
            service_assignment_doc.customer_id = service_masters_doc.customer_id
            service_assignment_doc.service_master = service
            service_assignment_doc.service_id = serv.name
            service_assignment_doc.old_executive = old_exe
            service_assignment_doc.new_executive = new_exe
            service_assignment_doc.assigned_by = frappe.session.user
            service_assignment_doc.insert()
            frappe.db.commit()

        return {"status":True,"msg":f"Reassigning of executive for {service} from {old_exe} to {new_exe} done Successfully!"}
    except Exception as er:
        return {"status":False,"msg":f"Error reassigning executive for {service} from {old_exe} to {new_exe}: {er}"}
