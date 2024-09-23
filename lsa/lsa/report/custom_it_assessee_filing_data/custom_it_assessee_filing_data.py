# # Copyright (c) 2024, Mohan and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from lsa.custom_whatsapp_api import validate_whatsapp_instance,send_custom_whatsapp_message

# def execute(filters=None):
#     columns = [
#         {"fieldname": "name", "label": _("ID"), "fieldtype": "Link", "options": "IT Assessee Filing Data", "width": 150},
#         {"fieldname": "can_be_filed", "label": _("Can Be Filed"), "fieldtype": "Data",  "width": 50},
#         {"fieldname": "customer_id", "label": _("CID"), "fieldtype": "Link", "options": "Customer", "width": 100},
#         {"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 100},
#         {"fieldname": "contact_person", "label": _("Contact Person"), "fieldtype": "Data", "width": 100},
#         {"fieldname": "assessee_full_name", "label": _("Assessee Full Name"), "fieldtype": "Data", "width": 120},
        
#         {"fieldname": "customer_status", "label": _("Customer Status"), "fieldtype": "Data", "width": 100},
#         {"fieldname": "it_assessee_file", "label": _("PAN"), "fieldtype": "Link", "options": "IT Assessee File", "width": 165},
#         {"fieldname": "filing_status", "label": _("Filing Status"), "fieldtype": "Data", "width": 170},
#         {"fieldname": "filing_type", "label": _("Filing Type"), "fieldtype": "Data", "width": 150},
#         # {"fieldname": "pan", "label": _("PAN"), "fieldtype": "Data", "width": 50},
#         {"fieldname": "executive", "label": _("Executive"), "fieldtype": "Data", "width": 150},
#         {"fieldname": "mobile_no", "label": _("Mobile No"), "fieldtype": "Data", "width": 100},
#         # {"fieldname": "created_manually", "label": _("Created Manually"), "fieldtype": "Check", "width": 100},
#         # {"fieldname": "ay", "label": _("IT Assessee File Yearly Report"), "fieldtype": "Data", "width": 150},
#         # {"fieldname": "filing_notes", "label": _("Filing Notes"), "fieldtype": "Data", "width": 150},
#     ]

#     # Construct additional filters based on the provided filters
#     additional_filters = {"it_enabled":1}

#     # Check if the mandatory filters are provided
#     if filters.get("ay"):
#         additional_filters["ay"] = filters["ay"]
#     else:
#         # If mandatory filters are not provided, return empty data
#         return columns, [], ""

#     data = frappe.get_all(
#         "IT Assessee Filing Data",
#         filters=additional_filters,
#         fields=["name", "can_be_filed", "customer_id","customer_name","contact_person", "assessee_full_name","customer_status", "it_assessee_file","filing_status", "filing_type", "executive","mobile_no",  ],
#         as_list=True
#     )

#     # Fetch counts for different filing statuses using custom SQL queries
#     statuses = ["PENDING INITIAL CONTACT", "DOCUMENTS REQUESTED", "DOCUMENTS PARTIALLY RECEIVED",
#                 "DOCUMENTS FULLY COLLECTED", "REVIEWED AND VERIFIED", "RETURN PREPARED", "SHARED TO CLIENT REVIEW",
#                 "FILED", "ACK AND VERIFIED", "DOCS SHARED WITH CLIENT"]
#     status_counts = {}

#     for status in statuses:
#         count_query = f"""
#             SELECT COUNT(name) as count
#             FROM `tabIT Assessee Filing Data`
#             WHERE filing_status = %s
#             AND ay = %s
#             AND it_enabled = 1
#         """

#         count_result = frappe.db.sql(count_query, [status, additional_filters["ay"]], as_dict=True)
#         status_count = count_result[0].get("count") if count_result else 0
#         status_counts[status] = status_count

#     total_records_count = sum(status_counts.values())

#     doc_shared_with_client = status_counts.get("DOCS SHARED WITH CLIENT", 0)
#     filed = status_counts.get("FILED", 0)
#     ack_and_verified = status_counts.get("ACK AND VERIFIED", 0)
#     completed_docs=doc_shared_with_client+filed+ack_and_verified
#     # doc_shared_with_client_percentage = (doc_shared_with_client / total_records_count) * 100 if total_records_count != 0 else 0
#     doc_shared_with_client_percentage = (completed_docs / total_records_count) * 100 if total_records_count != 0 else 0

#     executive_counts = {}

#     for executive in set(row[8] for row in data):
#         # Count for all filing statuses
#         count_query = f"""
#             SELECT COUNT(name) as count
#             FROM `tabIT Assessee Filing Data`
#             WHERE executive = %s
#             AND ay = %s
#             AND it_enabled = 1
#         """

#         count_result = frappe.db.sql(count_query, [executive, additional_filters["ay"]], as_dict=True)
#         executive_count = count_result[0].get("count") if count_result else 0

#         # Count specifically for "Filed Summery Shared With Client"
#         filed_summery_shared_query = f"""
#             SELECT COUNT(name) as count
#             FROM `tabIT Assessee Filing Data`
#             WHERE executive = %s
#             AND filing_status = 'DOCS SHARED WITH CLIENT'
#             AND ay = %s
#             AND it_enabled = 1
#         """

#         filed_summery_shared_count_result = frappe.db.sql(filed_summery_shared_query, [executive, additional_filters["ay"]], as_dict=True)
#         filed_summery_shared_count = filed_summery_shared_count_result[0].get("count") if filed_summery_shared_count_result else 0

#         # Count specifically for statuses other than "DOCS SHARED WITH CLIENT"
#         not_doc_shared_with_client_query = f"""
#             SELECT COUNT(name) as count
#             FROM `tabIT Assessee Filing Data`
#             WHERE executive = %s
#             AND filing_status != 'DOCS SHARED WITH CLIENT'
#             AND ay = %s
#             AND it_enabled = 1
#         """

#         not_doc_shared_with_client_result = frappe.db.sql(not_doc_shared_with_client_query, [executive, additional_filters["ay"]], as_dict=True)
#         not_doc_shared_with_client_count = not_doc_shared_with_client_result[0].get("count") if not_doc_shared_with_client_result else 0

#         # Assign the counts to the executive
#         executive_counts[executive] = {
#             "total_count": executive_count,
#             "filed_summery_shared_count": filed_summery_shared_count,
#             "not_doc_shared_with_client_count": not_doc_shared_with_client_count
#         }

#     executive_table = """
#     <table class="table table-bordered">
#         <thead>
#             <tr>
#                 <th>Executive</th>
#                 <th>Total Count</th>
#                 <th>Filed Summery Shared</th>
#                 <th>Not Filed Summery Shared</th>
#                 <th>Target Achieved</th>
#             </tr>
#         </thead>
#         <tbody>
#             {0}
#         </tbody>
#     </table>
#     """

#     executive_rows = "".join([
#         f"""
#         <tr>
#             <td>{executive}</td>
#             <td>{executive_counts[executive]["total_count"]}</td>
#             <td>{executive_counts[executive]["filed_summery_shared_count"]}</td>
#             <td>{executive_counts[executive]["not_doc_shared_with_client_count"]}</td>
#             <td>
#     {("{:.2f}".format((executive_counts[executive]["filed_summery_shared_count"] / executive_counts[executive]["total_count"]) * 100) 
#         if executive_counts[executive]["total_count"] > 0 
#         else 'No count')}
# </td>


#         </tr>
#         """
#         for executive in executive_counts.keys()
#     ])

#     response_user_validation=valiadting_user_for_bulk_wa_msg()
#     bulk_wa_button=''
#     if response_user_validation["status"]:
#         bulk_wa_button='''<div style="width:100%; display: flex; justify-content: flex-end; align-items: center;">
#         <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="bulk_wa_txt_message()">
#             <b style="color: #000000;">Send Custom WA Bulk Message</b>
#         </button>
#         </div>'''

#     html_card = f"""{bulk_wa_button}
#     <div class="frappe-card" style="margin-bottom: 10px;">
#         <div class="frappe-card-head" data-toggle="collapse" data-target="#collapsible-content">
#             <strong>Filing Status Counts</strong>
#             <strong>(Overall Target Achieved: {doc_shared_with_client_percentage:.2f}%)</strong>
#             <strong>(Total Count: {total_records_count})</strong>
#             <span class="caret"></span>
#         </div>
#         <div class="frappe-card-body collapse" id="collapsible-content">
#             <div class="flex-container" style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("PENDING INITIAL CONTACT", 0)}</div>
#                         <div class="frappe-card-label">PENDING INITIAL CONTACT Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("DOCUMENTS REQUESTED", 0)}</div>
#                         <div class="frappe-card-label">DOCUMENTS REQUESTED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("DOCUMENTS PARTIALLY RECEIVED", 0)}</div>
#                         <div class="frappe-card-label">DOCUMENTS PARTIALLY RECEIVED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("DOCUMENTS FULLY COLLECTED", 0)}</div>
#                         <div class="frappe-card-label">DOCUMENTS FULLY COLLECTED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("REVIEWED AND VERIFIED", 0)}</div>
#                         <div class="frappe-card-label">REVIEWED AND VERIFIED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("RETURN PREPARED", 0)}</div>
#                         <div class="frappe-card-label">RETURN PREPARED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("SHARED TO CLIENT REVIEW", 0)}</div>
#                         <div class="frappe-card-label">SHARED TO CLIENT REVIEW Count</div>
#                     </div>
#                 </div>       
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("FILED", 0)}</div>
#                         <div class="frappe-card-label">FILED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("ACK AND VERIFIED", 0)}</div>
#                         <div class="frappe-card-label">ACK AND VERIFIED Count</div>
#                     </div>
#                 </div>
#                 <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
#                     <div class="frappe-card-content">
#                         <div class="frappe-card-count">{status_counts.get("DOCS SHARED WITH CLIENT", 0)}</div>
#                         <div class="frappe-card-label">DOCS SHARED WITH CLIENT Count</div>
#                     </div>
#                 </div>
#                 <!-- Add other card elements here -->
#             </div>
#         </div>
#     </div>
#     <div class="frappe-card" style="margin-bottom: 10px;">
#         <div class="frappe-card-head" data-toggle="collapse" data-target="#executive-content">
#             <strong>Executive-wise Counts</strong>
#             <span class="caret"></span>
#         </div>
#         <div class="frappe-card-body collapse" id="executive-content">
#             {executive_table.format(executive_rows)}
#         </div>
#     </div>
#     """
#     """
#     <script>
#         frappe.ui.form.on('Gst Filling Data', {
#             refresh: function (frm) {
#                 frm.fields_dict['collapsible-content'].$wrapper.find('.frappe-card-head').on('click', function () {
#                     frm.fields_dict['collapsible-content'].toggle();
#                 });
#             }
#         });
#     </script>
#     """

#     return columns, data, html_card




# def valiadting_user_for_bulk_wa_msg():
#     user = frappe.session.user
#     if user=="Administrator":
#         return {"status": True, "msg": "User has the required role."}
    
#     admin_setting_doc = frappe.get_doc("Admin Settings")
#     auhenticated_users=[]
#     for i in admin_setting_doc.bulk_custom_wa_message_for_filing:
#         auhenticated_users.append(i.user)
    
#     if user not in auhenticated_users :
#         return {"status": False, "msg": "User does not have the required role to send Bulk WhatsApp messages."}
#     return {"status": True, "msg": "User has the required role."}

# @frappe.whitelist()
# def send_bulk_wa_for_filtered_it_customer(  message,
#                                             customer_status,
#                                             ay,
#                                             it_step_2_status=None,):

#     it_step_2_filter={
#                         "customer_status":("in",customer_status),
#                         "ay":ay,
#                     }
    
#     if it_step_2_status:
#         it_step_2_filter["filing_status"]=("in",it_step_2_status)


#     customer_diable_filter_dict=frappe.get_all("Customer",
#                                     filters={"disabled":0},)
#     customer_diable_filter_list=[ cus.name for cus in customer_diable_filter_dict]

#     it_step_2_list=frappe.get_all("IT Assessee Filing Data",
#                                     filters=it_step_2_filter,
#                                     fields=["mobile_no","name","customer_id"])
#     count=1
#     if it_step_2_list:
#         try:
#             whatsapp_instance="Operations"

#             resp_instance_validation=validate_whatsapp_instance(whatsapp_instance)

#             if not resp_instance_validation["status"]:
#                 frappe.log_error(f"An error occurred while validating Whatsapp instance{whatsapp_instance} for Bulk WhatsApp message for IT Assessee Filling Data.",f"{resp_instance_validation['msg']}")
#                 return {"status":False,"msg":f"An error occurred while validating Whatsapp instance{whatsapp_instance}."}
            
#             whatsapp_instance_doc=resp_instance_validation["whatsapp_instance_doc"]
#             credits=whatsapp_instance_doc.remaining_credits
#             # print(len(it_step_2_list),credits)
            
#             if len(it_step_2_list)<int(credits):
#                 new_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#                 for step_2 in it_step_2_list:
#                     # print(count)
#                     count+=1
#                     if customer_diable_filter_list and step_2.customer_id not in customer_diable_filter_list:
#                         new_whatsapp_log.append("details", {
#                                                                 "type": "IT Assessee Filing Data",
#                                                                 "document_id": step_2.name,
#                                                                 "mobile_number": step_2.mobile_no,
#                                                                 "customer": step_2.customer_id,
#                                                                 "message_id": None
#                                                             })
#                         frappe.log_error(f"Stopped sending Bulk WhatsApp message for IT Assessee Filling Data {step_2.name} to {step_2.mobile_no}",f"Customer is disaled")
#                         continue
#                     resp_wa_send_message=send_custom_whatsapp_message(resp_instance_validation["whatsapp_instance_doc"],step_2.mobile_no,message)
#                     if resp_wa_send_message["status"]:
#                         message_id=resp_wa_send_message["message_id"]
#                         new_whatsapp_log.append("details", {
#                                                                 "type": "IT Assessee Filing Data",
#                                                                 "document_id": step_2.name,
#                                                                 "mobile_number": step_2.mobile_no,
#                                                                 "customer": step_2.customer_id,
#                                                                 "message_id": message_id,
#                                                                 "sent_successfully":1,
#                                                             })
#                     else:
#                         new_whatsapp_log.append("details", {
#                                                                 "type": "IT Assessee Filing Data",
#                                                                 "document_id": step_2.name,
#                                                                 "mobile_number": step_2.mobile_no,
#                                                                 "customer": step_2.customer_id,
#                                                                 "message_id": message_id
#                                                             })
#                         frappe.log_error(f"An error occurred while sending Bulk WhatsApp message. For IT Assessee Filling Data {step_2.name} to {step_2.mobile_no}",f"{resp_wa_send_message['msg']}")
                
#                 new_whatsapp_log.send_date = frappe.utils.now_datetime()
#                 new_whatsapp_log.sender = frappe.session.user
#                 new_whatsapp_log.type = "Custom"
#                 new_whatsapp_log.message = message
#                 new_whatsapp_log.insert()
#                 return {"status":True,"msg":f"Successfully send bulk messages for IT Assessee Filing Data, remaining WhatsApp instance credits are {int(credits)-len(it_step_2_list)}"}
#             else:
#                 return {"status":False,"msg":f"Not enough credits available in Whatsapp Instance({credits}) to send bulk messages for IT Assessee Filing Data({len(it_step_2_list)})."}
#         except Exception as er:
#             # print("Error",er)
#             frappe.log_error(f"An Exception error occurred while sending Bulk WhatsApp messages for IT Assessee Filing Data.",f"{er}")
#             return {"status":False,"msg":f"An Exception error occurred while sending bulk WhatsApp messages for IT Assessee Filing Data."}
#     return {"status":False,"msg":f"No IT Assessee Filing Data record found for the filters set."}


# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from lsa.custom_whatsapp_api import validate_whatsapp_instance, send_custom_whatsapp_message

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": _("ID"), "fieldtype": "Link", "options": "IT Assessee Filing Data", "width": 150},
        {"fieldname": "can_be_filed", "label": _("Can Be Filed"), "fieldtype": "Data", "width": 50},
        {"fieldname": "customer_id", "label": _("CID"), "fieldtype": "Link", "options": "Customer", "width": 100},
        {"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 100},
        {"fieldname": "contact_person", "label": _("Contact Person"), "fieldtype": "Data", "width": 100},
        {"fieldname": "assessee_full_name", "label": _("Assessee Full Name"), "fieldtype": "Data", "width": 120},
        {"fieldname": "customer_status", "label": _("Customer Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "it_assessee_file", "label": _("PAN"), "fieldtype": "Link", "options": "IT Assessee File", "width": 165},
        {"fieldname": "filing_status", "label": _("Filing Status"), "fieldtype": "Data", "width": 170},
        {"fieldname": "filing_type", "label": _("Filing Type"), "fieldtype": "Data", "width": 150},
        {"fieldname": "executive", "label": _("Executive"), "fieldtype": "Data", "width": 150},
        {"fieldname": "mobile_no", "label": _("Mobile No"), "fieldtype": "Data", "width": 100}
    ]

    additional_filters = {"it_enabled": 1}

    if filters.get("ay"):
        additional_filters["ay"] = filters["ay"]
    else:
        return columns, [], ""

    data = frappe.db.sql("""
        SELECT
            filing.name,
            filing.can_be_filed,
            filing.customer_id,
            filing.customer_name,
            filing.contact_person,
            filing.assessee_full_name,
            filing.customer_status,
            filing.it_assessee_file,
            filing.filing_status,
            filing.filing_type,
            filing.executive,
            filing.mobile_no
        FROM `tabIT Assessee Filing Data` AS filing
        WHERE filing.ay = %s AND filing.it_enabled = 1
    """, additional_filters["ay"], as_dict=True)

    statuses = [
        "PENDING INITIAL CONTACT", "DOCUMENTS REQUESTED", "DOCUMENTS PARTIALLY RECEIVED",
        "DOCUMENTS FULLY COLLECTED", "REVIEWED AND VERIFIED", "RETURN PREPARED",
        "SHARED TO CLIENT REVIEW", "FILED", "ACK AND VERIFIED", "DOCS SHARED WITH CLIENT"
    ]
    status_counts = {}
    for status in statuses:
        count_query = """
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE filing_status = %s AND ay = %s AND it_enabled = 1
        """
        count_result = frappe.db.sql(count_query, [status, additional_filters["ay"]], as_dict=True)
        status_counts[status] = count_result[0].get("count", 0)

    total_records_count = sum(status_counts.values())
    doc_shared_with_client = status_counts.get("DOCS SHARED WITH CLIENT", 0)
    filed = status_counts.get("FILED", 0)
    ack_and_verified = status_counts.get("ACK AND VERIFIED", 0)
    completed_docs = doc_shared_with_client + filed + ack_and_verified
    doc_shared_with_client_percentage = (completed_docs / total_records_count) * 100 if total_records_count != 0 else 0

    executive_counts = {}

    for row in data:
        executive = row.get("executive")

        if not executive:
            continue

        count_query = """
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE it_assessee_file IN (
                SELECT name FROM `tabIT Assessee File` WHERE executive_name = %s
            ) AND ay = %s AND it_enabled = 1
        """
        count_result = frappe.db.sql(count_query, [executive, additional_filters["ay"]], as_dict=True)
        executive_count = count_result[0].get("count", 0)

        filed_summery_shared_query = """
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE it_assessee_file IN (
                SELECT name FROM `tabIT Assessee File` WHERE executive_name = %s
            ) AND filing_status = 'DOCS SHARED WITH CLIENT' AND ay = %s AND it_enabled = 1
        """
        filed_summery_shared_count_result = frappe.db.sql(filed_summery_shared_query, [executive, additional_filters["ay"]], as_dict=True)
        filed_summery_shared_count = filed_summery_shared_count_result[0].get("count", 0)

        not_doc_shared_with_client_query = """
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE it_assessee_file IN (
                SELECT name FROM `tabIT Assessee File` WHERE executive_name = %s
            ) AND filing_status != 'DOCS SHARED WITH CLIENT' AND ay = %s AND it_enabled = 1
        """
        not_doc_shared_with_client_result = frappe.db.sql(not_doc_shared_with_client_query, [executive, additional_filters["ay"]], as_dict=True)
        not_doc_shared_with_client_count = not_doc_shared_with_client_result[0].get("count", 0)

        executive_counts[executive] = {
            "total_count": executive_count,
            "filed_summery_shared_count": filed_summery_shared_count,
            "not_doc_shared_with_client_count": not_doc_shared_with_client_count
        }

    executive_rows = "".join([
        f"""
        <tr>
            <td>{executive}</td>
            <td>{executive_counts[executive]["total_count"]}</td>
            <td>{executive_counts[executive]["filed_summery_shared_count"]}</td>
            <td>{executive_counts[executive]["not_doc_shared_with_client_count"]}</td>
            <td>{("{:.2f}".format((executive_counts[executive]["filed_summery_shared_count"] / executive_counts[executive]["total_count"]) * 100) if executive_counts[executive]["total_count"] > 0 else 'No count')}</td>
        </tr>
        """
        for executive in executive_counts.keys()
    ])

    response_user_validation = valiadting_user_for_bulk_wa_msg()
    bulk_wa_button = ''
    if response_user_validation["status"]:
        bulk_wa_button = '''
        <div style="width:100%; display: flex; justify-content: flex-end; align-items: center;">
            <button class="btn btn-sm" style="margin-right: 10px; background-color: #A9A9A9;" onclick="bulk_wa_txt_message()">
                <b style="color: #000000;">Send Custom WA Bulk Message</b>
            </button>
        </div>'''

    html_card = f"""{bulk_wa_button}
    <div class="frappe-card" style="margin-bottom: 10px;">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#collapsible-content">
            <strong>Filing Status Counts</strong>
            <strong>(Overall Target Achieved: {doc_shared_with_client_percentage:.2f}%)</strong>
            <strong>(Total Count: {total_records_count})</strong>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body collapse" id="collapsible-content">
            <div class="flex-container" style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
                {"".join([f'<div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;"><div class="frappe-card-content"><div class="frappe-card-count">{status_counts[status]}</div><div class="frappe-card-label">{status.replace("_", " ").title()} Count</div></div></div>' for status in statuses])}
            </div>
        </div>
    </div>
    <div class="frappe-card" style="margin-bottom: 10px;">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#executive-content">
            <strong>Executive Counts</strong>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body collapse" id="executive-content">
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Executive</th>
                        <th>Total Count</th>
                        <th>Filed Summary Shared</th>
                        <th>Not Doc Shared With Client</th>
                        <th>Percentage Achieved</th>
                    </tr>
                </thead>
                <tbody>{executive_rows}</tbody>
            </table>
        </div>
    </div>"""
    """
    <script>
        frappe.ui.form.on('Gst Filling Data', {
            refresh: function (frm) {
                frm.fields_dict['collapsible-content'].$wrapper.find('.frappe-card-head').on('click', function () {
                    frm.fields_dict['collapsible-content'].toggle();
                });
            }
        });
    </script>
    """

    return columns, data, html_card





def valiadting_user_for_bulk_wa_msg():
    user = frappe.session.user
    if user=="Administrator":
        return {"status": True, "msg": "User has the required role."}
    
    admin_setting_doc = frappe.get_doc("Admin Settings")
    auhenticated_users=[]
    for i in admin_setting_doc.bulk_custom_wa_message_for_filing:
        auhenticated_users.append(i.user)
    
    if user not in auhenticated_users :
        return {"status": False, "msg": "User does not have the required role to send Bulk WhatsApp messages."}
    return {"status": True, "msg": "User has the required role."}

@frappe.whitelist()
def send_bulk_wa_for_filtered_it_customer(  message,
                                            customer_status,
                                            ay,
                                            it_step_2_status=None,):

    it_step_2_filter={
                        "customer_status":("in",customer_status),
                        "ay":ay,
                    }
    
    if it_step_2_status:
        it_step_2_filter["filing_status"]=("in",it_step_2_status)


    customer_diable_filter_dict=frappe.get_all("Customer",
                                    filters={"disabled":0},)
    customer_diable_filter_list=[ cus.name for cus in customer_diable_filter_dict]

    it_step_2_list=frappe.get_all("IT Assessee Filing Data",
                                    filters=it_step_2_filter,
                                    fields=["mobile_no","name","customer_id"])
    count=1
    if it_step_2_list:
        try:
            whatsapp_instance="Operations"

            resp_instance_validation=validate_whatsapp_instance(whatsapp_instance)

            if not resp_instance_validation["status"]:
                frappe.log_error(f"An error occurred while validating Whatsapp instance{whatsapp_instance} for Bulk WhatsApp message for IT Assessee Filling Data.",f"{resp_instance_validation['msg']}")
                return {"status":False,"msg":f"An error occurred while validating Whatsapp instance{whatsapp_instance}."}
            
            whatsapp_instance_doc=resp_instance_validation["whatsapp_instance_doc"]
            credits=whatsapp_instance_doc.remaining_credits
            # print(len(it_step_2_list),credits)
            
            if len(it_step_2_list)<int(credits):
                new_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
                for step_2 in it_step_2_list:
                    # print(count)
                    count+=1
                    if customer_diable_filter_list and step_2.customer_id not in customer_diable_filter_list:
                        new_whatsapp_log.append("details", {
                                                                "type": "IT Assessee Filing Data",
                                                                "document_id": step_2.name,
                                                                "mobile_number": step_2.mobile_no,
                                                                "customer": step_2.customer_id,
                                                                "message_id": None
                                                            })
                        frappe.log_error(f"Stopped sending Bulk WhatsApp message for IT Assessee Filling Data {step_2.name} to {step_2.mobile_no}",f"Customer is disaled")
                        continue
                    resp_wa_send_message=send_custom_whatsapp_message(resp_instance_validation["whatsapp_instance_doc"],step_2.mobile_no,message)
                    if resp_wa_send_message["status"]:
                        message_id=resp_wa_send_message["message_id"]
                        new_whatsapp_log.append("details", {
                                                                "type": "IT Assessee Filing Data",
                                                                "document_id": step_2.name,
                                                                "mobile_number": step_2.mobile_no,
                                                                "customer": step_2.customer_id,
                                                                "message_id": message_id,
                                                                "sent_successfully":1,
                                                            })
                    else:
                        new_whatsapp_log.append("details", {
                                                                "type": "IT Assessee Filing Data",
                                                                "document_id": step_2.name,
                                                                "mobile_number": step_2.mobile_no,
                                                                "customer": step_2.customer_id,
                                                                "message_id": message_id
                                                            })
                        frappe.log_error(f"An error occurred while sending Bulk WhatsApp message. For IT Assessee Filling Data {step_2.name} to {step_2.mobile_no}",f"{resp_wa_send_message['msg']}")
                
                new_whatsapp_log.send_date = frappe.utils.now_datetime()
                new_whatsapp_log.sender = frappe.session.user
                new_whatsapp_log.type = "Custom"
                new_whatsapp_log.message = message
                new_whatsapp_log.insert()
                return {"status":True,"msg":f"Successfully send bulk messages for IT Assessee Filing Data, remaining WhatsApp instance credits are {int(credits)-len(it_step_2_list)}"}
            else:
                return {"status":False,"msg":f"Not enough credits available in Whatsapp Instance({credits}) to send bulk messages for IT Assessee Filing Data({len(it_step_2_list)})."}
        except Exception as er:
            # print("Error",er)
            frappe.log_error(f"An Exception error occurred while sending Bulk WhatsApp messages for IT Assessee Filing Data.",f"{er}")
            return {"status":False,"msg":f"An Exception error occurred while sending bulk WhatsApp messages for IT Assessee Filing Data."}
    return {"status":False,"msg":f"No IT Assessee Filing Data record found for the filters set."}






