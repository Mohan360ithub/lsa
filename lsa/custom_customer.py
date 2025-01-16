import frappe
import requests
from frappe import _
from frappe.utils import today
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from lsa.custom_sales_order import so_payment_status
from copy import deepcopy


@frappe.whitelist()
def sync_customer(customer_id=None):
    try:
        followup_button,followup_values,values,open_followup,open_followup_i,unapproved_due_so=sync_sales_orders_customer(customer_id)
        services_values=sync_services_customer(customer_id)
        pricing_value=sync_services_pricing(customer_id)
        turnover_list=sync_turnover_gst(customer_id)
        disabled_services_values= sync_disabled_services_customer(customer_id)
        if [followup_button,followup_values,values,open_followup,open_followup_i] or services_values or pricing_value:

            return {"status":"Synced successfully.","followup_button":followup_button,"values":values,
                        "followup_values":followup_values,"services_values":services_values,"open_followup":open_followup,
                        "open_followup_i":open_followup_i,"pricing_value":pricing_value,"turnover_list":turnover_list,
                        'disabled_services_values':disabled_services_values,"unapproved_due_so":unapproved_due_so}
        else:
            return {"status":"Sync Failed."}
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False

def sync_services_pricing(customer_id=None):
    pricings=[]
    if customer_id:
        
        pricings=frappe.get_all("Recurring Service Pricing",
                                filters={"customer_id":customer_id,},
                                fields=["customer_id","name","effective_from","effective_to","status","fy"])

    return pricings

def sync_turnover_gst(customer_id):
    gst_filing_list=frappe.get_all("Gst Yearly Filing Summery",
                                filters={"cid":customer_id,},
                                fields=["cid","name","fy","company","gst_file_id","gst_executive","sales_total_taxable","purchase_total_taxable","fy_last_month_of_filling"],
                                order_by="creation")
    
    return gst_filing_list[:5]

# def sync_services_customer(customer_id=None):

#     master_service_fields = {
#         "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#     }

#     services_values=[]
#     chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
#     for chargeable_service in chargeable_services:
#         # print(chargeable_service)
#         chargeable_service_values=frappe.get_all(chargeable_service.name,
#                                            filters={"customer_id":customer_id,
#                                                    "enabled":1},
#                                             fields=master_service_fields[chargeable_service.name][1]
#                                             )
#         # print(chargeable_service_values)
#         for chargeable_service_value in chargeable_service_values:
#             chargeable_service_value=[chargeable_service_value[i] for i in master_service_fields[chargeable_service.name][1] ]
#             # print(chargeable_service_value)
#             service_slug="-".join([i.lower() for i in ((chargeable_service.name).split(" "))])
#             chargeable_service_value.append(service_slug)
#             chargeable_service_value.append(chargeable_service.name)
#             services_values.append(chargeable_service_value)
#     # print(services_values)
            
#     Client_Notices=["client-notices",["name","assessee_name", "notices_type","registration_number", "financial_year","executive_name"]]
#     chargeable_service_values_n=frappe.get_all("Client Notices",
#                                            filters={"cid":customer_id,
#                                                    "status":"Open",
#                                                    },
#                                             fields=Client_Notices[1],
#                                             )
#     for chargeable_service_value_n in chargeable_service_values_n:
#             chargeable_service_value_n=[chargeable_service_value_n[i] for i in Client_Notices[1] ]
#             # print(chargeable_service_value)
#             chargeable_service_value_n.insert(5, 1.00)
#             chargeable_service_value_n.insert(5, "Y")
#             chargeable_service_value_n.insert(5, 1.00)
#             chargeable_service_value_n.append(None)
            
            
#             service_slug=Client_Notices[0]
#             chargeable_service_value_n.append(service_slug)
#             chargeable_service_value_n.append("Client Notices")
#             services_values.append(chargeable_service_value_n)
#     return services_values


def sync_services_customer(customer_id=None):
    master_service_fields = {
        "Gstfile": [
            "gst_file",
            [
                "name",
                "company_name",
                "gst_number",
                "gst_user_name",
                "gst_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "IT Assessee File": [
            "it_assessee_file",
            [
                "name",
                "assessee_name",
                "pan",
                "pan",
                "it_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "MCA ROC File": [
            "mca_roc_file",
            [
                "name",
                "company_name",
                "cin",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "Professional Tax File": [
            "professional_tax_file",
            [
                "name",
                "assessee_name",
                "registration_no",
                "user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "TDS File": [
            "tds_file",
            [
                "name",
                "deductor_name",
                "tan_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "ESI File": [
            "esi_file",
            [
                "name",
                "assessee_name",
                "registartion_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "Provident Fund File": [
            "provident_fund_file",
            [
                "name",
                "assessee_name",
                "registartion_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
    }

    services_values = []
    chargeable_services = frappe.get_all("Customer Chargeable Doctypes")

    # Define frequency factors for annual fee calculation
    frequency_factors = {
        "Y": 1,    # Yearly
        "H": 2,    # Half-yearly
        "Q": 4,    # Quarterly
        "M": 12,   # Monthly
        # Add more if necessary
    }

    for chargeable_service in chargeable_services:
        service_slug = master_service_fields.get(chargeable_service.name, [None, None])[0]
        doctype_name = chargeable_service.name
        fields = master_service_fields.get(chargeable_service.name, [None, None])[1]

        if not doctype_name or not fields:
            frappe.log_error(
                f"Doctype mapping not found for service: {chargeable_service.name}",
                "sync_services_customer Error",
            )
            continue  # Skip if mapping is not found
        # print(doctype_name)
        # Fetch main service records
        main_service_records = frappe.get_all(
            doctype_name,
            filters={"customer_id": customer_id, "enabled": 1},
            fields=fields,
        )

        for record in main_service_records:
            # Extract main service fields in order
            main_service_data = [record.get(field) for field in fields]

            # Append slug and service name
            service_slug = "-".join(doctype_name.lower().split(" "))
            main_service_data.append(service_slug)
            main_service_data.append(chargeable_service.name)
            # services_values.append(main_service_data)

            # Fetch and process addon services
            addon_services = frappe.get_all(
                "Service Master Addon",
                filters={"parent": record.name, "status": "Active"},
                fields=["addon_service_name", "current_charges", "frequency"],
            )

            for addon in addon_services:
                service_addon_data = deepcopy(main_service_data)
                addon_type = addon.get("addon_service_name")
                fees = addon.get("current_charges", 0)
                frequency = addon.get("frequency", "Y").upper()
                frequency_factor = frequency_factors.get(frequency, 1)
                annual_fee = fees * frequency_factor

                
                service_addon_data.append(fees)
                service_addon_data.append(frequency)
                service_addon_data.append(annual_fee)
                service_addon_data.append(addon_type)

                # Prepare addon service data
                # addon_service_data = [
                #     record.get("name"),            # Parent service name
                #     addon_type,                    # Addon type
                #     fees,                          # Fees
                #     frequency,                     # Frequency
                #     annual_fee,                    # Calculated Annual Fee
                #     record.get("executive_name"),  # Executive Name
                # ]

                # Append slug and service name
                # addon_service_slug = "-".join(addon_type.lower().split(" "))
                # addon_service_data.append(addon_service_slug)
                # addon_service_data.append(f"Addon: {addon_type}")
                # services_values.append(addon_service_data)
                services_values.append(service_addon_data)
                
                

    # Process Client Notices as before
    Client_Notices = [
        "client-notices",
        [
            "name",
            "assessee_name",
            "notices_type",
            "registration_number",
            "financial_year",
            "executive_name",
            
            
        ],
    ]
    chargeable_service_values_n = frappe.get_all(
        "Client Notices",
        filters={"cid": customer_id, "status": "Open"},
        fields=Client_Notices[1],
    )
    for notice in chargeable_service_values_n:
        notice_data = [notice.get(field) for field in Client_Notices[1]]

        service_slug = Client_Notices[0]
        notice_data.append(None)
        notice_data.append(service_slug)
        notice_data.append("Client Notices")
        services_values.append(notice_data)

        # Insert additional fields as per original logic
        # notice_data.insert(5, 1.00)  # Example value, adjust as needed
        # notice_data.insert(5, "Y")    # Example value, adjust as needed
        # notice_data.insert(5, 1.00)  # Example value, adjust as needed
        notice_data.append(1.00)  # Example value, adjust as needed
        notice_data.append("Y")    # Example value, adjust as needed
        notice_data.append(1.00)  # Example value, adjust as needed
        notice_data.append(None)


    
    return services_values


##################Srikanth's Code Start#########################################################################################



# def sync_disabled_services_customer(customer_id=None):

#     master_service_fields = {
#         "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#         "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
#     }

#     services_values=[]
#     chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
#     for chargeable_service in chargeable_services:
#         # print(chargeable_service)
#         chargeable_service_values=frappe.get_all(chargeable_service.name,
#                                            filters={"customer_id":customer_id,
#                                                    "enabled":0},
#                                             fields=master_service_fields[chargeable_service.name][1]
#                                             )
#         # print(chargeable_service_values)
#         for chargeable_service_value in chargeable_service_values:
#             chargeable_service_value=[chargeable_service_value[i] for i in master_service_fields[chargeable_service.name][1] ]
#             # print(chargeable_service_value)
#             service_slug="-".join([i.lower() for i in ((chargeable_service.name).split(" "))])
#             chargeable_service_value.append(service_slug)
#             chargeable_service_value.append(chargeable_service.name)
#             services_values.append(chargeable_service_value)
#     # print(services_values)
            
    
#     return services_values


##################Srikanth's Code End#########################################################################################



def sync_disabled_services_customer(customer_id=None):
    master_service_fields = {
        "Gstfile": [
            "gst_file",
            [
                "name",
                "company_name",
                "gst_number",
                "gst_user_name",
                "gst_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "IT Assessee File": [
            "it_assessee_file",
            [
                "name",
                "assessee_name",
                "pan",
                "pan",
                "it_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "MCA ROC File": [
            "mca_roc_file",
            [
                "name",
                "company_name",
                "cin",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "Professional Tax File": [
            "professional_tax_file",
            [
                "name",
                "assessee_name",
                "registration_no",
                "user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "TDS File": [
            "tds_file",
            [
                "name",
                "deductor_name",
                "tan_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "ESI File": [
            "esi_file",
            [
                "name",
                "assessee_name",
                "registartion_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
        "Provident Fund File": [
            "provident_fund_file",
            [
                "name",
                "assessee_name",
                "registartion_no",
                "trace_user_id",
                "trace_password",
                "executive_name",
                "last_filed",
            ],
        ],
    }

    services_values = []
    chargeable_services = frappe.get_all("Customer Chargeable Doctypes")

    # Define frequency factors for annual fee calculation
    frequency_factors = {
        "Y": 1,    # Yearly
        "H": 2,    # Half-yearly
        "Q": 4,    # Quarterly
        "M": 12,   # Monthly
        # Add more if necessary
    }

    for chargeable_service in chargeable_services:
        service_slug = master_service_fields.get(chargeable_service.name, [None, None])[0]
        doctype_name = chargeable_service.name
        fields = master_service_fields.get(chargeable_service.name, [None, None])[1]

        if not doctype_name or not fields:
            frappe.log_error(
                f"Doctype mapping not found for service: {chargeable_service.name}",
                "sync_services_customer Error",
            )
            continue  # Skip if mapping is not found
        # print(doctype_name)
        # Fetch main service records
        main_service_records = frappe.get_all(
            doctype_name,
            filters={"customer_id": customer_id, "enabled": 0},
            fields=fields,
        )

        for record in main_service_records:
            # Extract main service fields in order
            main_service_data = [record.get(field) for field in fields]

            # Append slug and service name
            service_slug = "-".join(doctype_name.lower().split(" "))
            main_service_data.append(service_slug)
            main_service_data.append(chargeable_service.name)
            # services_values.append(main_service_data)

            # Fetch and process addon services
            addon_services = frappe.get_all(
                "Service Master Addon",
                filters={"parent": record.name, "status": "Active"},
                fields=["addon_service_name", "current_charges", "frequency"],
            )

            for addon in addon_services:
                service_addon_data = deepcopy(main_service_data)
                addon_type = addon.get("addon_service_name")
                fees = addon.get("current_charges", 0)
                frequency = addon.get("frequency", "Y").upper()
                frequency_factor = frequency_factors.get(frequency, 1)
                annual_fee = fees * frequency_factor

                
                service_addon_data.append(fees)
                service_addon_data.append(frequency)
                service_addon_data.append(annual_fee)
                service_addon_data.append(addon_type)

                # Prepare addon service data
                # addon_service_data = [
                #     record.get("name"),            # Parent service name
                #     addon_type,                    # Addon type
                #     fees,                          # Fees
                #     frequency,                     # Frequency
                #     annual_fee,                    # Calculated Annual Fee
                #     record.get("executive_name"),  # Executive Name
                # ]

                # Append slug and service name
                # addon_service_slug = "-".join(addon_type.lower().split(" "))
                # addon_service_data.append(addon_service_slug)
                # addon_service_data.append(f"Addon: {addon_type}")
                # services_values.append(addon_service_data)
                services_values.append(service_addon_data)
                
                

    # # Process Client Notices as before
    # Client_Notices = [
    #     "client-notices",
    #     [
    #         "name",
    #         "assessee_name",
    #         "notices_type",
    #         "registration_number",
    #         "financial_year",
    #         "executive_name",
            
            
    #     ],
    # ]
    # chargeable_service_values_n = frappe.get_all(
    #     "Client Notices",
    #     filters={"cid": customer_id, "status": "Open"},
    #     fields=Client_Notices[1],
    # )
    # for notice in chargeable_service_values_n:
    #     notice_data = [notice.get(field) for field in Client_Notices[1]]

    #     service_slug = Client_Notices[0]
    #     notice_data.append(None)
    #     notice_data.append(service_slug)
    #     notice_data.append("Client Notices")
    #     services_values.append(notice_data)

    #     # Insert additional fields as per original logic
    #     # notice_data.insert(5, 1.00)  # Example value, adjust as needed
    #     # notice_data.insert(5, "Y")    # Example value, adjust as needed
    #     # notice_data.insert(5, 1.00)  # Example value, adjust as needed
    #     notice_data.append(1.00)  # Example value, adjust as needed
    #     notice_data.append("Y")    # Example value, adjust as needed
    #     notice_data.append(1.00)  # Example value, adjust as needed
    #     notice_data.append(None)

    # for serv_addon in services_values:
    #     print(len(serv_addon))
    #     print(serv_addon)
    
    return services_values

def sync_sales_orders_customer(customer_id):
    ############################Sales Order############################################################################

    existing_sales_orders=frappe.get_all("Sales Order",
                                filters={"customer":customer_id,
                                            "docstatus":['in', [0,1]]})
    # print(existing_sales_orders)
    so_details={}
    custom_count_of_so_due=0
    custom_total_amount_due_of_so=0.00
    custom_details_of_so_due=[]
    unapproved_due_so=False

    if existing_sales_orders:

        for existing_sales_order in existing_sales_orders:
            # print(existing_sales_order)
            sales_order=frappe.get_doc("Sales Order",existing_sales_order.name)
            payment_status="Unpaid"
            custom_so_balance=sales_order.rounded_total
            advance_paid=0
            pes=frappe.get_all("Payment Entry Reference",filters={"reference_doctype":"Sales Order","reference_name":sales_order.name,"docstatus": 1},fields=["name","parent","allocated_amount"])
            # doc.custom_pe_counts=len(pes)
            for pe in pes:
                custom_so_balance-=pe.allocated_amount
                advance_paid+=pe.allocated_amount

            sales_invoice_exists=None
            if custom_so_balance>0:
                si_list=frappe.get_all("Sales Invoice Item",filters={"sales_order":sales_order.name,"docstatus": 1},fields=["name","parent"])
                if si_list:
                    si_list=list(set([i.parent for i in si_list]))
                    sales_invoice_exists=", ".join(si_list)


            docstatus="Drafted"
            if sales_order.docstatus==1:
                docstatus="Submitted"
            elif sales_order.docstatus==2:
                docstatus="Cancelled"

            if custom_so_balance>0:
                custom_count_of_so_due+=1
                custom_total_amount_due_of_so+=(custom_so_balance)
                custom_details_of_so_due.append(sales_order.name)
                so_details[sales_order.name]=[sales_order.rounded_total,advance_paid,
                                                custom_so_balance,
                                                sales_order.custom_so_from_date,sales_order.custom_so_to_date,
                                                docstatus,sales_order.custom_followup_count,
                                                sales_order.customer_name,sales_order.customer]
                #print(sales_order.docstatus,sales_order.status)
                if custom_so_balance<sales_order.rounded_total:
                    payment_status="Partially Paid"
                so_details[sales_order.name]+=[payment_status]
                so_details[sales_order.name]+=[sales_invoice_exists]
                so_details[sales_order.name]+=[sales_order.custom_approval_status]
                if sales_order.custom_approval_status!="Approved" :
                    unapproved_due_so=True
        custom_details_of_so_due=", ".join(custom_details_of_so_due)


    ##############################################followup button##############################################################
    
    followup_button=False
    open_followup_i=""
    open_followups=[]
    if custom_total_amount_due_of_so>0:
        followups=frappe.get_all("Customer Followup", filters={"customer_id":customer_id},fields=["name","status"])
        open_followups=[i for i in followups if i.status=="Open"]
        if followups and not(open_followups):
            next_followup_date=""
            for followup in followups:
                followup_doc=frappe.get_doc("Customer Followup",followup.name)
                if followup_doc.status == "Closed" and followup_doc.next_followup_date:
                    date_format = "%Y-%m-%d"
                    this_followup_date=datetime.strptime(str(followup_doc.next_followup_date)
                                                            , date_format).date()
                    # print(this_followup_date)
                    if next_followup_date=="" or this_followup_date >=next_followup_date :
                        # print("next",next_followup_date,"this",this_followup_date)
                        next_followup_date = this_followup_date
            if next_followup_date:
                today_date = datetime.now().date()
                if next_followup_date<=today_date:
                    # print("this followup true",next_followup_date,today_date)
                    followup_button=True
            else:
                # print("else followup true")
                followup_button=True
        elif open_followups:
            # open_followups=frappe.get_doc("Customer Followup",open_followups[0]["name"])
            open_followup_i=str(open_followups[0]["name"])
        else:
            # print("outer followup true")
            followup_button=True
        

    ############################Follow up############################################################################
        
    followup_values={"Open":[],"Closed":[],"values":[],}
    if custom_total_amount_due_of_so>0:
        existing_followups=frappe.get_all("Customer Followup",
                                filters={"customer_id":customer_id,
                                        # "status":['in', ["Draft","On Hold","To Deliver and Bill","To Bill","To Deliver"]]
                                        })
        # print(existing_sales_orders)
        if existing_followups:
            last_closed_followup_date="Dummy"
            next_followup_date="Dummy"

            for existing_followup in existing_followups:
                # print(existing_sales_order)
                followup=frappe.get_doc("Customer Followup",existing_followup.name)

                if followup.status == "Open":
                    open_followup=followup.name
                    followup_nature="Open"
                    open_followup_date=followup.followup_date
                    followup_values["Open"]=[open_followup,followup_nature,open_followup_date]
                elif followup.status == "Closed" and not(followup_values["Open"]):
                    # print("next",next_followup_date,"this",followup.next_followup_date)
                    if last_closed_followup_date=="Dummy" or \
                            last_closed_followup_date<followup.followup_date:
                        # print("next update")
                        last_followup=followup.name
                        followup_nature="Closed"
                        next_followup_date=followup.next_followup_date
                        last_closed_followup_date=followup.followup_date
                        last_followup_comment=followup.followup_note
                        followup_values["Closed"]=[last_followup,followup_nature,next_followup_date,last_followup_comment]


                followup_values["values"]+=[[followup.customer_id,followup.name,
                                            followup.status,followup.total_remaining_balance,
                                            followup.followup_date,followup.next_followup_date,
                                            followup.executive_name,followup.followup_note]]
    return followup_button,followup_values,[so_details,custom_count_of_so_due,custom_total_amount_due_of_so,custom_details_of_so_due],open_followups,open_followup_i,unapproved_due_so
                        
    

@frappe.whitelist()
def sync_sales_orders_followup(sales_order_summary=None,customer_id=None,followup_date=None,followup_id=None):
    try:
        sales_order_summary=sales_order_summary.strip()
        existing_sales_orders=sales_order_summary.split(", ")

        if existing_sales_orders:
            p_details=[]
            for existing_sales_order in existing_sales_orders:
                pe_s=frappe.get_all("Payment Entry Reference",
                                           filters={
                                               "reference_doctype":"Sales Order",
                                               "reference_name":existing_sales_order,
                                               "docstatus": 1,
                                               },
                                           fields=["name","parent","allocated_amount"])
                sales_order_p=frappe.get_doc("Sales Order",existing_sales_order)
                for pe in pe_s:
                    existing_payment_entry=frappe.get_doc("Payment Entry",pe.parent)
                    p_details.append([existing_sales_order,existing_payment_entry.reference_date,pe.parent,existing_payment_entry.paid_to,
                                                         sales_order_p.rounded_total,pe.allocated_amount])
                    # if existing_sales_order not in p_details:
                    #     p_details[existing_sales_order]=[existing_payment_entry.reference_date,pe.parent,existing_payment_entry.paid_to,
                    #                                      sales_order_p.rounded_total,pe.allocated_amount]
                    # else:
                    #     p_details[existing_sales_order]+=[existing_payment_entry.reference_date,pe.parent,existing_payment_entry.paid_to,
                    #                                      sales_order_p.rounded_total,pe.allocated_amount]
        
        if existing_sales_orders:
            so_details={}
            for existing_sales_order in existing_sales_orders:
                # print(existing_sales_order)
                sales_order=frappe.get_doc("Sales Order",existing_sales_order)
                payment_status="Unpaid"
                custom_so_balance=sales_order.rounded_total
                advance_paid=0
                pes=frappe.get_all("Payment Entry Reference",filters={"reference_doctype":"Sales Order","reference_name":sales_order.name,"docstatus": 1},fields=["name","parent","allocated_amount"])
                # doc.custom_pe_counts=len(pes)
                for pe in pes:
                    custom_so_balance-=pe.allocated_amount
                    advance_paid+=pe.allocated_amount

                docstatus="Drafted"
                if sales_order.docstatus==1:
                    docstatus="Submitted"
                elif sales_order.docstatus==2:
                    docstatus="Cancelled"
                    
                # custom_details_of_so_due.append(sales_order.name)
                so_details[sales_order.name]=[sales_order.rounded_total,advance_paid,
                                                custom_so_balance,
                                                sales_order.custom_so_from_date,sales_order.custom_so_to_date,
                                                docstatus,sales_order.custom_followup_count,
                                                sales_order.customer_name,sales_order.customer]
                if custom_so_balance<sales_order.rounded_total:
                    payment_status="Partially Paid"
                so_details[sales_order.name]+=[payment_status]
        ##################################################################################################################
        followup_values={"Open":[],"Closed":[],"values":[],}
        date_format = "%Y-%m-%d"
        followup_date=datetime.strptime(followup_date, date_format).date()
        if True:
            existing_followups=frappe.get_all("Customer Followup",
                                    filters={"customer_id":customer_id},
                                    order_by="creation DESC",
                                    limit=5)
            # print(existing_sales_orders)
            if existing_followups:
                last_closed_followup_date="Dummy"
                next_followup_date="Dummy"

                for existing_followup in existing_followups:
                    # print(existing_sales_order)
                    followup=frappe.get_doc("Customer Followup",existing_followup.name)

                    if followup.status == "Open":
                        open_followup=followup.name
                        followup_nature="Open"
                        open_followup_date=followup.followup_date
                        followup_values["Open"]=[open_followup,followup_nature,open_followup_date]
                    elif followup.status == "Closed" and not(followup_values["Open"]):
                        # print("next",next_followup_date,"this",followup.next_followup_date)
                        if last_closed_followup_date=="Dummy" or \
                                last_closed_followup_date<followup.followup_date:
                            # print("next update")
                            last_followup=followup.name
                            followup_nature="Closed"
                            next_followup_date=followup.next_followup_date
                            last_closed_followup_date=followup.followup_date
                            last_followup_comment=followup.followup_note
                            followup_values["Closed"]=[last_followup,followup_nature,next_followup_date,last_followup_comment]
                    
                    if followup.followup_date<=followup_date and followup_id!=followup.name:
                        followup_values["values"]+=[[followup.customer_id,followup.name,
                                                    followup.status,followup.total_remaining_balance,
                                                    followup.followup_date,followup.next_followup_date,
                                                    followup.executive_name,followup.followup_note]]


            return {"status":"Synced successfully.","values":[so_details],"followup_values":followup_values,"p_details":[p_details]}
        # else:
        #     return {"status":"Synced successfully."}
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False

@frappe.whitelist()
def checking_user_authentication(user_email=None):
    try:
        status = False
        wa_status=False
        dis_status=False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["LSA Accounts Manager","LSA Account Executive","Lsa Front Desk CRM Executive(A,B)"]
        doc_wa_perm_roles=["GST Front Desk Team","Lsa Front Desk CRM Executive(A,B)"]
        doc_dis_perm_roles=["Customer Onboarding Officer"]

        for role in roles:
            if role in doc_perm_roles:
                status = True
            if role in doc_wa_perm_roles:
                wa_status = True
            if role in doc_dis_perm_roles:
                dis_status = True
        

        return {"status": status, "value": [roles],"wa_status":wa_status,"dis_status":dis_status}

    except Exception as e:
        #print(e)
        return {"status": "Failed"}


# return followup_button,followup_values,[so_details,custom_count_of_so_due,custom_total_amount_due_of_so,custom_details_of_so_due],open_followups,open_followup_i
     
@frappe.whitelist()
def wa_followup_customer(customer_id,customer_name,new_mobile):
    # new_mobile="9098543046"
    existing_sales_orders=frappe.get_all("Sales Order",
                                filters={"customer":customer_id,
                                            "docstatus":['in', [0,1]]})
    # print(existing_sales_orders)
    message=f'''Dear {customer_name},

You are having due amount to be paid for following Sales Invoices: 
'''
    custom_count_of_so_due=0
    custom_total_amount=0.00
    custom_total_amount_due_of_so=0.00
    custom_details_of_so_due={}
    sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')

    if existing_sales_orders:

        for existing_sales_order in existing_sales_orders:
            # print(existing_sales_order)
            sales_order=frappe.get_doc("Sales Order",existing_sales_order.name)
            
            msg_so_line=""
            custom_so_balance=sales_order.rounded_total
            advance_paid=0
            pes=frappe.get_all("Payment Entry Reference",filters={"reference_doctype":"Sales Order","reference_name":sales_order.name,"docstatus": 1},fields=["name","parent","allocated_amount"])
            # doc.custom_pe_counts=len(pes)
            for pe in pes:
                custom_so_balance-=pe.allocated_amount
                advance_paid+=pe.allocated_amount

            sales_invoice_exists=None
            if custom_so_balance>0:
                si_item_list=frappe.get_all("Sales Invoice Item",filters={"sales_order":sales_order.name,"docstatus": 1},fields=["name","parent"])
                si_list=[ si.parent for si in si_item_list]
                si_list=list(set(si_list))
                if si_list:
                    for si_name in si_list:
                        si_pe=frappe.get_all("Payment Entry Reference",filters={"reference_doctype":"Sales Invoice","reference_name":si_name,"docstatus": 1},fields=["name","parent","allocated_amount"])
                        for pe in si_pe:
                            custom_so_balance-=pe.allocated_amount
                            advance_paid+=pe.allocated_amount

            if custom_so_balance>0:
                custom_count_of_so_due+=1
                
                custom_total_amount+=sales_order.rounded_total
                custom_total_amount_due_of_so+=(custom_so_balance)
                custom_details_of_so_due[sales_order.name]=["Unpaid",sales_order.rounded_total,advance_paid,custom_so_balance,
                                                            sales_order.custom_so_from_date,sales_order.custom_so_to_date,
                                                            sales_order.custom_followup_count]
                #print(sales_order.docstatus,sales_order.status)
                if custom_so_balance<sales_order.rounded_total:
                    custom_details_of_so_due[sales_order.name][0]="Partially Paid"
                message+=f'''\n{custom_count_of_so_due}.{sales_order.name} from {sales_order.custom_so_from_date} to {sales_order.custom_so_to_date} with due amount ₹{custom_so_balance}/-.'''

    message+=f'''\n\nKindly pay the net due amount of ₹{custom_total_amount_due_of_so}/- to below bank details:

Our Bank Account:
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO (fifth character is zero)
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200

Call us immediately in case of query.

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788
'''
                    
    
    # whatsapp_items = []

    sales_invoice_whatsapp_log.message = message
    
    for due_so in custom_details_of_so_due:
        wa_response=due_so_whatsapp(due_so,custom_details_of_so_due[due_so][0],new_mobile,message)
        if wa_response["status"]==True:
            # whatsapp_items.append({"type": "Sales Order",
            #                 "document_id": due_so,
            #                 "mobile_number": new_mobile,
            #                 "customer":customer_id,})
            sales_invoice_whatsapp_log.append("details", {
                                    "type": "Sales Order",
                                    "document_id": due_so,
                                    "mobile_number": new_mobile,
                                    "customer":customer_id,
                                    "message_id":wa_response["message_id"]                 
                                })
            message=""

    sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
    sales_invoice_whatsapp_log.sender = frappe.session.user
    sales_invoice_whatsapp_log.type = "Template"
    sales_invoice_whatsapp_log.insert()




# @frappe.whitelist()
# def so_summary_wa_followup_customer(customer_id, customer_name, new_mobile):
#     try:
#         # Get all relevant sales orders
#         existing_sales_orders = frappe.get_all(
#             "Sales Order",
#             filters={"customer": customer_id, "docstatus": ['in', [0, 1]]}
#         )

#         # Initialize the message template
#         message = f"Dear {customer_name},\n\nYou are having a due amount to be paid for the following Sales Invoices:\n"

#         custom_count_of_so_due = 0
#         custom_total_amount_due_of_so = 0.00
#         custom_details_of_so_due = {}

#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')

#         if existing_sales_orders:
#             for existing_sales_order in existing_sales_orders:
#                 sales_order = frappe.get_doc("Sales Order", existing_sales_order.name)

#                 # Initialize amounts
#                 custom_so_balance = sales_order.rounded_total
#                 advance_paid = 0

#                 # Get payment entries related to the sales order
#                 pes = frappe.get_all(
#                     "Payment Entry Reference",
#                     filters={"reference_doctype": "Sales Order", "reference_name": sales_order.name, "docstatus": 1},
#                     fields=["name", "parent", "allocated_amount"]
#                 )
#                 for pe in pes:
#                     custom_so_balance -= pe.allocated_amount
#                     advance_paid += pe.allocated_amount

#                 # Adjust balance for any related sales invoices
#                 if custom_so_balance > 0:
#                     si_item_list = frappe.get_all(
#                         "Sales Invoice Item",
#                         filters={"sales_order": sales_order.name, "docstatus": 1},
#                         fields=["name", "parent"]
#                     )
#                     si_list = list(set(si.parent for si in si_item_list))
#                     for si_name in si_list:
#                         si_pe = frappe.get_all(
#                             "Payment Entry Reference",
#                             filters={"reference_doctype": "Sales Invoice", "reference_name": si_name, "docstatus": 1},
#                             fields=["name", "parent", "allocated_amount"]
#                         )
#                         for pe in si_pe:
#                             custom_so_balance -= pe.allocated_amount
#                             advance_paid += pe.allocated_amount

#                 # Update message and details if there is a balance due
#                 if custom_so_balance > 0:
#                     custom_count_of_so_due += 1
#                     custom_total_amount_due_of_so += custom_so_balance
#                     custom_details_of_so_due[sales_order.name] = [
#                         "Unpaid" if custom_so_balance == sales_order.rounded_total else "Partially Paid",
#                         sales_order.rounded_total,
#                         advance_paid,
#                         custom_so_balance,
#                         sales_order.custom_so_from_date,
#                         sales_order.custom_so_to_date,
#                         sales_order.custom_followup_count
#                     ]

#                     message += f"\n{custom_count_of_so_due}. {sales_order.name} from {sales_order.custom_so_from_date} to {sales_order.custom_so_to_date} with due amount ₹{custom_so_balance}/-."

#             # Add bank details and final message content
#             message += f"""
#             \n\nKindly pay the net due amount of ₹{custom_total_amount_due_of_so}/- to the below bank details:

# Our Bank Account:
# Lokesh Sankhala and ASSOCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda, JC Road, Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200

# Call us immediately in case of any queries.

# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com
# 8951692788
#             """

#             # Send WhatsApp message for the first sales order
#             if existing_sales_orders:
#                 first_sales_order = existing_sales_orders[0]
#                 wa_response = due_so_whatsapp_so_summary(
#                     first_sales_order.name,
#                     "Partially Paid" if custom_total_amount_due_of_so > 0 else "Paid",
#                     new_mobile,
#                     message
#                 )

#                 if wa_response["status"]:
#                     # Log the WhatsApp message
#                     sales_invoice_whatsapp_log.append("details", {
#                         "type": "Sales Order",
#                         "document_id": first_sales_order.name,
#                         "mobile_number": new_mobile,
#                         "customer": customer_id,
#                         "message_id": wa_response["message_id"]
#                     })
#                     sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#                     sales_invoice_whatsapp_log.sender = frappe.session.user
#                     sales_invoice_whatsapp_log.type = "Template"
#                     sales_invoice_whatsapp_log.insert()

#                     return {"status": True, "msg": "WhatsApp message sent successfully"}
#                 else:
#                     return {"status": False, "msg": wa_response["msg"]}

#         return {"status": True, "msg": "No pending sales orders for the customer."}

#     except Exception as e:
#         frappe.logger().error(f"Error in so_summary_wa_followup_customer: {e}")
#         return {"status": False, "msg": "An unexpected error occurred. Please contact the system administrator."}

# @frappe.whitelist()
# def due_so_whatsapp_so_summary(docname, paymentstatus, new_mobile, template):
#     try:
#         whatsapp_instance = frappe.get_all('WhatsApp Instance', filters={
#             'module': 'Accounts', 
#             'connection_status': 1, 
#             'active': 1
#         })
        
#         if not whatsapp_instance:
#             return {"status": False, "msg": "WhatsApp API instance is not connected."}
        
#         instance = frappe.get_doc('WhatsApp Instance', whatsapp_instance[0].name)
#         ins_id = instance.instance_id

#         # Validate mobile number
#         if len(new_mobile) != 10:
#             return {"status": False, "msg": "Please provide a valid 10-digit mobile number."}

#         # WhatsApp API call
#         url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#         # print("templateeeeeeeeeeeee",template)
#         params = {
#             "token": ins_id,
#             "phone": f"91{new_mobile}",
#             "message": template,
#             # "link": frappe.utils.get_url() + f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Payment%20Pending%20Sales%20Order&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
#             "link": "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00492&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en"
#         }

#         response = requests.post(url, params=params)
#         response.raise_for_status()
#         response_data = response.json()

#         if response_data.get('status') == 'success':
#             message_id = response_data['data']['messageIDs'][0]
#             return {"status": True, "msg": "WhatsApp message sent successfully", "message_id": message_id}
#         else:
#             return {"status": False, "msg": f"Error: {response_data.get('message')}"}

#     except requests.exceptions.RequestException as e:
#         frappe.logger().error(f"Network error: {e}")
#         return {"status": False, "msg": "Network error occurred. Please try again later."}
#     except Exception as e:
#         frappe.logger().error(f"Error: {e}")
#         return {"status": False, "msg": "An unexpected error occurred. Please contact the system administrator."}


@frappe.whitelist()
def due_so_whatsapp(docname,paymentstatus,new_mobile,template):
    # new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Operations','connection_status':1,'active':1})
    if whatsapp_demo:
        
        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id


        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return

            
            
            message = template
            
            ########################### Below commented link is work on Live #######################
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            if paymentstatus=="Partially Paid":
                link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"

            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }

            
            
            response = requests.post(url, params=params_1)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            message_id = response_data['data']['messageIDs'][0]


            # Check if the response status is 'success'
            if response_data.get('status') == 'success':
                # Log the success

                frappe.logger().info("WhatsApp message sent successfully")
                
                return {"status":True,"msg":"WhatsApp message sent successfully","message_id":message_id}
            else:
                return {"status":False,"error":f"{response.json()}","msg":"An error occurred while sending the WhatsApp message."}


        except requests.exceptions.RequestException as e:
            # Log the exception and provide feedback to the user
            frappe.logger().error(f"Network error: {e}")
            return {"status":False,"error":e,"msg":"An error occurred while sending the WhatsApp message. Please try again later."}
        except Exception as er:
            # Log the exception and provide feedback to the user
            frappe.logger().error(f"Error: {er}")
            return {"status":False,"error":er,"msg":"An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator."}
    else:
        return {"status":False,"msg":"Your WhatApp API instance is not connected"}

                    

def update_linked_doctypes(doc, method):
    # Get the new and old status of the customer
    new_status = doc.custom_customer_status_
    old_status = frappe.db.get_value('Customer', doc.name, 'custom_customer_status_')
    # print(new_status,old_status)
    # Check if the status has changed
    if True:
        try:
            linked_doctypes = {
                                "Client Notices":("cid","customer_status"),
                                "DSC Digital Sign":("customer_id","customer_status"), 
                                "ESI File":("customer_id","customer_status"), 
                                "Gst Filling Data":("customer_id","customer_status"),
                                "Gst Yearly Filing Summery":("customer_id","customer_status"), 
                                "Gstfile":("customer_id","customer_status"), 
                                "IT Assessee File":("customer_id","customer_status"), 
                                "IT Assessee Filing Data":("customer_id","customer_status"),
                                "MCA ROC File":("customer_id","customer_status"), 
                                "Provident Fund File":("customer_id","customer_status"), 
                                "Professional Tax File":("customer_id","customer_status"), 
                                "TDS File":("customer_id","customer_status"),
                                "Recurring Service Pricing":("customer_id","customer_status"), 
                                "NTC Payment":("customer_id","customer_status"), 
                                "TDS QTRLY FILING":("customer_id","customer_status"),
                            }

            for doctypei in linked_doctypes:
                linked_docs = frappe.get_all(doctypei, 
                                             filters={linked_doctypes[doctypei][0]: doc.name},
                                             fields=["name",linked_doctypes[doctypei][1]])

                for linked_doc in linked_docs:
                    if new_status==linked_doc[linked_doctypes[doctypei][1]]:
                        continue
                    doc_to_update = frappe.get_doc(doctypei, linked_doc.name)
                    doc_to_update.save()
                    
        except Exception as e:
            frappe.logger().error(f"Error Triggering status Change for Customer {doc.name}: {e}")



@frappe.whitelist()
def disable_customer(customer_id,reason):
    try:
    # if True:
        customer_doc=frappe.get_doc("Customer",customer_id)

        old_status=customer_doc.disabled
        new_status=None
        if old_status==0:
            old_status="Enabled"
            new_status="Disabled"
            customer_doc.disabled=1
        else:
            old_status="Disabled"
            new_status="Enabled"
            customer_doc.disabled=0
        
        new_status_update_record = customer_doc.append('custom_customer_disable_history', {})
        new_status_update_record.modified_by1 = frappe.session.user
        new_status_update_record.previous_status = old_status
        new_status_update_record.status_changed_to = new_status
        new_status_update_record.reason = reason
        new_status_update_record.time_of_change = datetime.now()

        

        master_service_fields = {
            "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        }

        chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
        for chargeable_service in chargeable_services:
            # print(chargeable_service)
            chargeable_service_enable_values=frappe.get_all(chargeable_service.name,
                                            filters={"customer_id":customer_id,
                                                    "enabled":1,
                                                    },
                                                )
            if chargeable_service_enable_values and new_status!="Enabled":
                # continue
                frappe.throw(f"You can't disable customer having active service {chargeable_service.name}: {chargeable_service_enable_values[0].name}")
                # pass



        customer_so=frappe.get_all("Sales Order",
                                   filters={
                                       "docstatus":("not in",[2]),
                                       "customer":customer_id,
                                   })
        for so in customer_so:
            resp=so_payment_status(so.name)
            try:
                if  resp["payment_status"]!="Cleared" and new_status!="Enabled":
                    # continue
                    frappe.throw(f"You can't disable customer having pending payment for Sales Order: {so.name} {resp['payment_status']}")
            except Exception as eso:
                frappe.logger().error(f"Error to fetch payment status for Sales Order {so.name}: {eso} {resp}")
                return {"status":False,"message": f"Error to fetch payment status for Sales Order {so.name}: {eso} {resp}"}
            
        rsp_list=frappe.get_all("Recurring Service Pricing",filters={"customer_id":customer_id,"status":("not in",("Discontinued"))})
        
        if rsp_list and new_status!="Enabled":
            # continue
            frappe.throw(f"You can't disable customer having active Recurring Service Pricing {rsp_list[0].name}")
            # pass
            
        customer_doc.save()


        serv_freq={"M":"Monthly",
                   "Q":"Quarterly",
                   "H":"Half Yearly",
                   "Y":"Yearly",}

        
        body = """
                    <br><table class="table table-bordered" style="border-color: #444444; border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr style="background-color:#3498DB;color:white;text-align: left;">
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">S. No.</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service Type</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service ID</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 35%;">Company Name</th>                                
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Frequency</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
            
        count = 1
        # executive_list={'lokesh.bwr@gmail.com', 'khushboo.r@lsaoffice.com', 'latha.st@lsaoffice.com', 'vinay.m@lsaoffice.com', 'Shriramu.ms@lsaoffice.com',"vatsal.k@360ithub.com"}
        executive_list=[]
        admin_setting_doc = frappe.get_doc("Admin Settings")
        for i in admin_setting_doc.customer_status_change_mail:
            executive_list.append(i.user)
        executive_list = set(executive_list)
        
        for chargeable_service in chargeable_services:
            # print(chargeable_service)
            chargeable_service_values=frappe.get_all(chargeable_service.name,
                                            filters={"customer_id":customer_id,
                                                    # "enabled":1,
                                                    },
                                            fields=["name",master_service_fields[chargeable_service.name][1][1],"executive","frequency"]
                                                )
            # print(chargeable_service_values)
            for chargeable_service_value in chargeable_service_values:
                # print(chargeable_service.name,chargeable_service_value.name)
                # chargeable_service_doc=frappe.get_doc(chargeable_service.name,chargeable_service_value.name)
                # chargeable_service_doc.enabled=0
                # chargeable_service_doc.save()
                executive_list.add(chargeable_service_value["executive"])
                body += f"""
                    <tr>
                        <td style="border: solid 2px #bcb9b4;">{count}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service.name}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service_value.name}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service_value[master_service_fields[chargeable_service.name][1][1]]}</td>                      
                        <td style="border: solid 2px #bcb9b4;">{serv_freq[chargeable_service_value.frequency]}</td>
                    </tr>
                """
                count += 1
            
        body += """
                    </tbody>
                </table><br>
        """
        

        now = datetime.now()
        # Format the datetime in DD-MM-YYYY HH:MM AM/PM
        time_of_change = now.strftime("%d-%m-%Y %I:%M %p")
        user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")

        subject = f"Customer with CID {customer_id} is {new_status}"
        html_message = f"""
            <p>Dear LSA Team,<br><br> There are some changes in following customer. Please make a note of it. </p>
            <table style="border-collapse: collapse; width: 60%;">
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer ID</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{customer_doc.name}">{customer_doc.name}</a></td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Name</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{customer_doc.name}">{customer_doc.customer_name}</a></td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Status</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{new_status}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Modified By</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{user_full_name}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Changed at</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{time_of_change}</td>
                </tr>
            </table>
            <br>
            {body}
            <br><p>Best regards,<br>LSA Office</p>
        """
            
        # frappe.sendmail(
        #         # recipients=recipients,  # Use the list of combined email addresses
        #         recipients=list(executive_list),
        #         subject=subject,
        #         message=message
        #     )
        email_account = frappe.get_doc("Email Account", "LSA Info")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()

        # executive_list=["vatsal.k@360ithub.com","laxmi.s@lsaoffice.com"]
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ",".join(list(executive_list))
        # message['Cc'] = cc_email
        message['Subject'] = subject
        message.attach(MIMEText(html_message, 'html'))


        # Connect to the SMTP server and send the email
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            try:
                # Send email
                server.sendmail(sender_email, list(executive_list) , message.as_string())
                return {"status":True,"message": f"Customer {new_status} successfully","executive_list":list(executive_list)}
            except Exception as er:
                print(f"Failed to send email. Error: {er}")
                return {"status":False,"message": f"Failed to {new_status} customer {er}"}

    except Exception as e:
        frappe.log_error(message=str(e), title=f"Failed to {new_status} customer")
        # print(f"{e}")
        return {"status":False,"message": f"Failed to {new_status} customer {e}"}
    
#######################################Srikanth Code Start#####################################################################

 
@frappe.whitelist()
def send_status_update_notification(cid, new_status, reason):
    try:
        # Fetch the fields from "Recurring Service Pricing"
        rsp_list= frappe.get_all("Recurring Service Pricing", filters={"customer_id": cid,"status":"Approved"})

        ###########modified by Vatsal start############################
        customer_doc= frappe.get_doc("Customer",cid)
        old_status=customer_doc.custom_customer_status_
        customer_doc.custom_customer_status_= new_status
        
        new_status_update_record = customer_doc.append('custom_customer_status_history', {})
        new_status_update_record.modified_by1 = frappe.session.user
        new_status_update_record.previous_status = old_status
        new_status_update_record.status_changed_to = new_status
        new_status_update_record.reason = reason
        new_status_update_record.time_of_change = datetime.now()

        customer_doc.save()
        ###########modified by Vatsal End############################
        if rsp_list:
            rsp_docs= frappe.get_doc("Recurring Service Pricing", rsp_list[0].name)
            # print(rsp_docs)
            # print("Helloowowoowwo")
            # Build the HTML content for the message
            body = """
                    <br><table class="table table-bordered" style="border-color: #444444; border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr style="background-color:#3498DB;color:white;text-align: left;">
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">S. No.</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service Type</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service ID</th>
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 35%;">Company Name</th>                                
                                <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Frequency</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
            
            count = 1
            for service in rsp_docs.recurring_services:
                body += f"""
                    <tr>
                        <td style="border: solid 2px #bcb9b4;">{count}</td>
                        <td style="border: solid 2px #bcb9b4;">{service.service_type}</td>
                        <td style="border: solid 2px #bcb9b4;">{service.service_id}</td>
                        <td style="border: solid 2px #bcb9b4;">{service.company_name}</td>                      
                        <td style="border: solid 2px #bcb9b4;">{service.frequency}</td>
                    </tr>
                """
                count += 1
            
            body += """
                        </tbody>
                    </table><br>
            """
 
            now = datetime.now()
            # Format the datetime in DD-MM-YYYY HH:MM AM/PM
            time_of_change = now.strftime("%d-%m-%Y %I:%M %p")
            user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")
 
            # Define the subject and message of the email
            subject = f"CID {customer_doc.name} Customer Status Changed from {old_status} to {new_status}"
            html_message = f"""
                <p>Dear LSA Team,<br><br> There are some changes in the status of following customer. Please make a note of it, before maving forward with our services.</p>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer ID</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{customer_doc.name}">{customer_doc.name}</a></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Name</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{customer_doc.name}">{customer_doc.customer_name}</a></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Status</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Changed from {old_status} to {new_status}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Modified By</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{user_full_name}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Reason</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{reason}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Changed at</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{time_of_change}</td>
                    </tr>
                </table>
                <br>
                {body}
                <br><p>Best regards,<br>LSA Office</p>
            """
 
            # Collect all executive emails
            executive_emails = set()  # Use a set to handle duplicates
 
            customer_chargeable = frappe.get_all("Customer Chargeable Doctypes")
            for i in customer_chargeable:
                master_list = frappe.get_all(i.name, filters={"customer_id": customer_doc.name}, fields=["executive"])
                for entry in master_list:
                    if entry["executive"]:  # Check if the executive field is not None or empty
                        executive_emails.add(entry["executive"])
 
            # Define hardcoded emails
            status_update_mails=[]
            admin_setting_doc = frappe.get_doc("Admin Settings")
            for i in admin_setting_doc.customer_status_change_mail:
                status_update_mails.append(i.user)
            status_update_mails = set(status_update_mails)

            # Combine executive emails with hardcoded emails, ensuring no duplicates
            all_emails = executive_emails.union(status_update_mails)
            # all_emails.add("vatsal.k@360ithub.com")
            # Convert the set back to a list
            recipients = list(all_emails)
            # print(recipients)
            # test_emails = ['srikanth.p_cse2019@svec.edu.in']
            # print(test_emails)
            # print("Hellooooooo")
 
            # Send the email
            # frappe.sendmail(
            #     # recipients=recipients,  # Use the list of combined email addresses
            #     recipients=recipients,
            #     subject=subject,
            #     message=message
            # )
             ###########modified by Vatsal start############################
            # recipients = ["mohan@360ithub.com", "vatsal.k@360ithub.com"]
            email_account = frappe.get_doc("Email Account", "LSA Info")
            sender_email = email_account.email_id
            sender_password = email_account.get_password()

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = ",".join(recipients)
            # message['Cc'] = cc_email
            message['Subject'] = subject
            message.attach(MIMEText(html_message, 'html'))


            # Connect to the SMTP server and send the email
            smtp_server = 'smtp-mail.outlook.com'
            smtp_port = 587
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                try:
                    # Send email
                    server.sendmail(sender_email, recipients , message.as_string())
                    return {"status":True,"message": "Notification sent successfully!","executive_emails":all_emails}
                except Exception as er:
                    print(f"Failed to send email. Error: {e}")
                    return {"status":False,"message": f"Failed to send notification:{er}"}
             ###########modified by Vatsal end############################
        else:
            frappe.log_error(message=f"No RSP Exist for the customer {customer_doc.name}", title="Failed to send status update notification")
            return {"status":False,"message": f"Failed to send notification:No RSP Exist for the customer {customer_doc.name}"}
    except Exception as e:
        # print(e)
        frappe.log_error(message=str(e), title="Failed to send status update notification")
        return {"status":False,"message": f"Failed to send notification:{e}"}

#######################################Srikanth Code Start#####################################################################

def lead_validation_before_insert(doc,method):
    if not doc.lead_name:
        frappe.throw("You can't create Customer directly! Lead has to be created before Customer creation.")



def get_customer_annual_fees(customer_id):
    annual_fees=0
    chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
    for chargeable_service in chargeable_services:
        # print(chargeable_service)
        chargeable_service_values=frappe.get_all(chargeable_service.name,
                                           filters={"customer_id":customer_id,
                                                   "enabled":1},
                                            fields=["annual_fees"]
                                            )
        # print(chargeable_service_values)
        for chargeable_service in chargeable_service_values:
            annual_fees+=chargeable_service.annual_fees
    
    return annual_fees


############################send Bulk message in Followup############################

# @frappe.whitelist()
# def get_followups(start_date, end_date, status):
#     try:
#         # Fetch the followups based on date range and status
#         followups = frappe.db.get_all(
#             'Customer Followup',
#             filters={
#                 'next_followup_date': ['between', [start_date, end_date]],
#                 'status': status
#             },
#             fields=['name', 'followup_date', 'next_followup_date' ,'customer_id','client_name','mobile_number','sales_order_summary','followup_note','email_id']
#         )
#         return followups
#     except Exception as e:
#         frappe.throw(_("Failed to load followup list: {0}").format(str(e)))


@frappe.whitelist()
def get_followups(start_date, end_date, status):
    try:
        # Fetch the followups based on date range and status
        followups = frappe.db.get_all(
            'Customer Followup',
            filters={
                'next_followup_date': ['between', [start_date, end_date]],
                'status': status
            },
            fields=['name', 'followup_date', 'next_followup_date', 'customer_id', 'client_name', 'mobile_number', 'sales_order_summary', 'followup_note', 'email_id']
        )
        
        # Get a list of customer IDs from the followups
        customer_ids = [followup['customer_id'] for followup in followups]

        if not customer_ids:
            return []

        # Filter customers where disabled is 0
        active_customers = frappe.db.get_all(
            'Customer',
            filters={
                'name': ['in', customer_ids],
                'disabled': 0
            },
            fields=['name']
        )

        # Create a set of active customer IDs for easy lookup
        active_customer_ids = {customer['name'] for customer in active_customers}

        # Filter followups to include only those with active customers
        filtered_followups = [followup for followup in followups if followup['customer_id'] in active_customer_ids]

        return filtered_followups

    except Exception as e:
        frappe.throw(_("Failed to load followup list: {0}").format(str(e)))


# @frappe.whitelist()
# def send_bulk_message(followup_id, send_whatsapp, send_mail):
#     try:
#         # Print the incoming parameters for debugging
#         print('followup_id, send_whatsapp, send_mail', followup_id, send_whatsapp, send_mail)
        
#         # Check if followup_id is provided
#         if not followup_id:
#             frappe.throw(_("No followups selected"))

#         # Make sure followup_id is a list
#         followup_ids = followup_id if isinstance(followup_id, list) else json.loads(followup_id)

#         # Enqueue the background task
#         frappe.enqueue('lsa.custom_customer.process_bulk_messages', followup_ids=followup_ids, send_whatsapp=send_whatsapp, send_mail=send_mail)
        
#         return _("Messages are being sent in the background!")
#     except Exception as e:
#         frappe.throw(_("Failed to send messages: {0}").format(str(e)))

# @frappe.whitelist()
# def process_bulk_messages(followup_ids, send_whatsapp, send_mail):
#     for followup_id in followup_ids:
#         # Get the customer document using the followup ID
#         followup_doc = frappe.get_doc('Customer Followup', followup_id)
#         customer_id = followup_doc.customer_id
#         customer_name = followup_doc.client_name
#         new_mobile = followup_doc.mobile_number

#         # Send WhatsApp message if the flag is true
#         if send_whatsapp == 'true':
#             print('Sending WhatsApp message...', customer_id, customer_name, new_mobile)
#             so_summary_wa_followup_customer(customer_id, customer_name, new_mobile)

#         # Send email if the flag is true
#         if send_mail == 'true':
#             print('Sending email...')
#             send_email_message(customer_id, customer_name)



# def send_email_message(cus_id, cus_name):
#     # Your logic to send email
#     subject = "Follow-up Reminder"
#     message = f"Dear {cus_name}, this is a follow-up reminder."
#     # Implement your actual email sending logic here
#     print(f"Email Sent: Subject: {subject}, Message: {message}")



import frappe
from frappe import _
import json

from lsa.custom_mail import single_mail_with_attachment
from lsa.custom_whatsapp_api import validate_whatsapp_instance, send_custom_whatsapp_message_with_file
import frappe
from datetime import datetime





import frappe
import json
from frappe import _

@frappe.whitelist()
def send_bulk_message(followup_id, send_whatsapp, send_mail):
    errors = []
    success_messages = []

    try:
        if not followup_id:
            frappe.throw(_("No followups selected"))

        # Parse followup IDs, ensuring it's a list
        followup_ids = followup_id if isinstance(followup_id, list) else json.loads(followup_id)

        # Handle WhatsApp message sending
        if send_whatsapp == 'true':
            try:
                whatsapp_instance = "Operations"
                resp_instance_validation = validate_whatsapp_instance(whatsapp_instance)

                if not resp_instance_validation["status"]:
                    error_msg = f"Error in WhatsApp validation: {resp_instance_validation['msg']}"
                    frappe.log_error(error_msg, f"WhatsApp Validation Error for instance {whatsapp_instance}")
                    errors.append(error_msg)
                else:
                    whatsapp_instance_doc = resp_instance_validation["whatsapp_instance_doc"]
                    credits = whatsapp_instance_doc.remaining_credits

                    if len(followup_ids) > int(credits):
                        error_msg = "Not enough WhatsApp credits to process all selected followups."
                        frappe.log_error(error_msg, "WhatsApp Credits Error")
                        errors.append(error_msg)
                    else:
                        # Enqueue the bulk WhatsApp message processing job
                        frappe.enqueue(
                            'lsa.custom_customer.process_bulk_messages_what_app_message',
                            followup_ids=followup_ids,
                            whatsapp_instance_doc=whatsapp_instance_doc,
                            timeout=600
                        )
                        success_messages.append("WhatsApp messages are being processed in the background!")
                        followup_needs_save = True
            except Exception as e:
                error_msg = f"Error in sending WhatsApp messages: {str(e)}"
                frappe.log_error(error_msg, "WhatsApp Bulk Message Error")
                errors.append(error_msg)
        
        # Handle email sending
        if send_mail == 'true':
            try:
                # Enqueue the bulk mail sending job
                frappe.enqueue(
                    'lsa.custom_customer.send_bulk_mail',
                    followup_ids=followup_ids,
                    timeout=600
                )
                success_messages.append("Emails are being sent in the background!")
                followup_needs_save = True

            except Exception as e:
                error_msg = f"Error in sending bulk emails: {str(e)}"
                frappe.log_error(error_msg, "Bulk Mail Error")
                errors.append(error_msg)


        if followup_needs_save:
            for followup_id_int in followup_ids:
                followup_doc = frappe.get_doc('Customer Followup', followup_id_int)
                # Update necessary fields (e.g., WhatsApp sent or email sent)
                if send_whatsapp == 'true':
                    followup_doc.send_whatsapp = 1
                if send_mail == 'true':
                    followup_doc.send_email = 1
                followup_doc.save()

        # Check if there were any errors and display them
        if errors:
            error_message = "Some errors occurred: " + "; ".join(errors)
            if success_messages:
                success_message = "Success: " + "; ".join(success_messages)
                return {"status": False, "msg": f"{success_message}; {error_message}"}
            else:
                return {"status": False, "msg": error_message}

        # If no errors occurred
        if success_messages:
            success_message = "; ".join(success_messages)
            return {"status": True, "msg": success_message}

    except Exception as e:
        # Log unexpected errors and display them to the user
        frappe.log_error(f"Error in sending bulk messages: {str(e)}", "Bulk Message Error")
        frappe.throw(_("Failed to send messages: {0}").format(str(e)))



@frappe.whitelist()
def send_single_whatsapp_message(customer_id, customer_name, new_mobile,followup_id):
    try:
        # print('followup_idddddddddddddddddddddd',followup_id)
        # Create a message template for a single customer
        followup_doc = frappe.get_doc('Customer Followup', followup_id)
        message_template = create_message_template(customer_name, customer_id)
        sales_order_summary = followup_doc.sales_order_summary
        if sales_order_summary:
            # Split the string by comma and take the first value
            first_sales_order = sales_order_summary.split(',')[0].strip()
            # print(f"First Sales Order: {first_sales_order}")
        else:
            first_sales_order = None
        new_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        # Send WhatsApp message
        # pdflink = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2024-00852&format=Payment%20Pending%20Sales%20Order&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
        pdflink = frappe.utils.get_url() + f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={first_sales_order}&format=Payment%20Pending%20Sales%20Order&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
        whatsapp_instance = "Operations"
        resp_instance_validation = validate_whatsapp_instance(whatsapp_instance)
        # print('resp_instance_validationmmmmmmmmmmmmmmmm',resp_instance_validation)
        if not resp_instance_validation["status"]:
            # print("resp_instance_validationnnnnnnnnnnnnnnnnnnnnnnnnnnn",resp_instance_validation)
            frappe.log_error(f"An error occurred while validating Whatsapp instance {whatsapp_instance}.", f"{resp_instance_validation['msg']}")
            return {"status": False, "msg": f"An error occurred while validating Whatsapp instance {whatsapp_instance}."}

        whatsapp_instance_doc = resp_instance_validation["whatsapp_instance_doc"]
        credits = whatsapp_instance_doc.remaining_credits
        # print('creditsssssssssssssssss',credits)
        # if len(followup_id) < int(credits) and len(new_mobile) == 10 and new_mobile.isnumeric():
        if True:
            wa_sent_resp = send_custom_whatsapp_message_with_file(whatsapp_instance_doc, new_mobile, message_template, pdflink)
            # wa_response = due_so_whatsapp_so_summary_custom(customer_id, new_mobile, message_template,followup_id,first_sales_order)
            # print('wa_sent_resppppppppppppppppppppppp',wa_sent_resp)
            if wa_sent_resp["status"]:
                message_id = wa_sent_resp["message_id"]
                new_whatsapp_log.append("details", {
                    "type": "Customer Followup",
                    "document_id": followup_id,
                    "mobile_number": new_mobile,
                    "customer": customer_id,
                    "message_id": message_id,
                    "sent_successfully": 1,
                })
            else:
                new_whatsapp_log.append("details", {
                    "type": "Customer Followup",
                    "document_id": followup_id,
                    "mobile_number": new_mobile,
                    "customer": customer_id
                })

                followup_doc.send_whatsapp = 1
                followup_doc.save()

            # Insert WhatsApp log after processing all followups
            new_whatsapp_log.send_date = frappe.utils.now_datetime()
            new_whatsapp_log.sender = frappe.session.user
            new_whatsapp_log.type = "Custom"
            new_whatsapp_log.message = message_template
            new_whatsapp_log.insert()
            # Log the response for debugging purposes
            frappe.logger().info(f"WhatsApp Response: {wa_sent_resp}")

            if wa_sent_resp["status"]:
                return {"status": True, "msg": _("WhatsApp message sent successfully.")}
            else:
                return {"status": False, "msg": wa_sent_resp.get("msg", _("Failed to send WhatsApp message."))}
        else:
            return {"status": False, "msg": wa_sent_resp.get("msg", _("Failed to send WhatsApp message."))}
    except Exception as e:
        frappe.logger().error(f"Error sending single WhatsApp message: {e}")
        return {"status": False, "msg": _("Failed to send WhatsApp message.")}



@frappe.whitelist()
def process_bulk_messages_what_app_message(followup_ids, whatsapp_instance_doc):
    try:
        new_whatsapp_log = frappe.new_doc('WhatsApp Message Log')

        for followup_id in followup_ids:
            followup_doc = frappe.get_doc('Customer Followup', followup_id)
            customer_id = followup_doc.customer_id
            customer_name = followup_doc.client_name
            new_mobile = followup_doc.mobile_number
            follow_up_id_int = followup_doc.name

            # Get the first sales order from the sales_order_summary field
            sales_order_summary = followup_doc.sales_order_summary
            first_sales_order = sales_order_summary.split(',')[0].strip() if sales_order_summary else None

            # Create WhatsApp message template
            message_template = create_message_template(customer_name, customer_id)

            # Send WhatsApp message with PDF link
            pdflink = frappe.utils.get_url() + f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={first_sales_order}&format=Payment%20Pending%20Sales%20Order&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
            # pdflink = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00492&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
            # if len(new_mobile) == 10 and new_mobile.isnumeric():
            if True:
                wa_sent_resp = send_custom_whatsapp_message_with_file(whatsapp_instance_doc, new_mobile, message_template, pdflink)
                
                if wa_sent_resp["status"]:
                    message_id = wa_sent_resp["message_id"]
                    new_whatsapp_log.append("details", {
                        "type": "Customer Followup",
                        "document_id": follow_up_id_int,
                        "mobile_number": new_mobile,
                        "customer": customer_id,
                        "message_id": message_id,
                        "sent_successfully": 1,
                    })
                    frappe.db.set_value('Customer Followup', follow_up_id_int, 'send_whatapp', 1)
                else:
                    new_whatsapp_log.append("details", {
                        "type": "Customer Followup",
                        "document_id": follow_up_id_int,
                        "mobile_number": new_mobile,
                        "customer": customer_id
                    })
        message_template_tem = """Payment Reminder
Dear {customer_name},

You have a due amount to be paid for the following Sales Invoices:

{payment_period_and_amount}

Kindly pay the net due amount as on {current_datetime} of ₹ {total_amount_due}/- to the below bank details:

Our Bank Account:
Lokesh Sankhala and ASSOCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO (fifth character is zero)
Bank = Bank of Baroda, JC Road, Bangalore-560002
UPI ID = LSABOB@UPI
Gpay / Phonepe no = 9513199200

Call us immediately in case of any queries.

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788"""
        # Insert WhatsApp log after processing all followups
        new_whatsapp_log.send_date = frappe.utils.now_datetime()
        new_whatsapp_log.sender = frappe.session.user
        new_whatsapp_log.type = "Template"
        new_whatsapp_log.message = message_template_tem
        new_whatsapp_log.insert()

        return {"status": True, "msg": "Bulk WhatsApp messages processed successfully."}

    except Exception as e:
        frappe.log_error(f"Error in processing WhatsApp bulk messages: {str(e)}", "WhatsApp Message Processing Error")
        frappe.throw(_("Failed to process WhatsApp messages: {0}").format(str(e)))

        


import re
import requests
from datetime import datetime
import frappe

@frappe.whitelist()
def send_bulk_mail(followup_ids):
    def is_valid_email(email):
        # Regex for validating an email address
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None
    new_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
    for followup_id in followup_ids:
        followup_doc = frappe.get_doc('Customer Followup', followup_id)
        customer_id = followup_doc.customer_id
        customer_name = followup_doc.client_name
        follow_up_id_int = followup_doc.name
        
        # Get the first sales order from the sales_order_summary field
        sales_order_summary = followup_doc.sales_order_summary
        first_sales_order = sales_order_summary.split(',')[0].strip() if sales_order_summary else None

        # Ensure email is valid
        email = [followup_doc.email_id] if followup_doc.email_id and is_valid_email(followup_doc.email_id) else []

        # Fetch CC emails from Admin Settings and filter valid ones
        admin_settings = frappe.get_doc("Admin Settings")
        cc_email = [email.strip() for email in admin_settings.bulk_email_cc_for_customer_followup.split(',') if is_valid_email(email.strip())]

        # Fetch existing sales orders
        existing_sales_orders = frappe.get_all(
            "Sales Order",
            filters={"customer": customer_id, "docstatus": ['in', [0, 1]]}
        )
        current_datetime = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        # Prepare the email message body
        custom_count_of_so_due = 0
        custom_total_amount_due_of_so = 0.00
        message = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; background-color: #f9f9f9; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 5px; background-color: #fff; }}
                h2 {{ color: #4CAF50; text-align: center; }}
                .due-list {{ margin: 20px 0; padding: 0; list-style: none; }}
                .due-list li {{ margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background-color: #f2f2f2; }}
                .footer {{ margin-top: 20px; font-size: 0.9em; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Payment Reminder</h2>
                <p>Dear <strong>{customer_name}</strong>,</p>
                <p>You have a due amount to be paid for the following Sales Invoices:</p>
                <ul class="due-list">
        """
        
        message += """
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background-color:#3498DB;color:white;text-align: center;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">No</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Sales Order Period</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Due Amount (₹)</th>
                    </tr>
                </thead>
                <tbody>
        """

        if existing_sales_orders:
            for existing_sales_order in existing_sales_orders:
                sales_order = frappe.get_doc("Sales Order", existing_sales_order.name)
                custom_so_balance = sales_order.rounded_total
                advance_paid = 0

                # Get payment entries related to the sales order
                pes = frappe.get_all(
                    "Payment Entry Reference",
                    filters={"reference_doctype": "Sales Order", "reference_name": sales_order.name, "docstatus": 1},
                    fields=["name", "parent", "allocated_amount"]
                )
                for pe in pes:
                    custom_so_balance -= pe.allocated_amount
                    advance_paid += pe.allocated_amount

                # Adjust balance for any related sales invoices
                if custom_so_balance > 0:
                    si_item_list = frappe.get_all(
                        "Sales Invoice Item",
                        filters={"sales_order": sales_order.name, "docstatus": 1},
                        fields=["name", "parent"]
                    )
                    si_list = list(set(si.parent for si in si_item_list))
                    for si_name in si_list:
                        si_pe = frappe.get_all(
                            "Payment Entry Reference",
                            filters={"reference_doctype": "Sales Invoice", "reference_name": si_name, "docstatus": 1},
                            fields=["name", "parent", "allocated_amount"]
                        )
                        for pe in si_pe:
                            custom_so_balance -= pe.allocated_amount
                            advance_paid += pe.allocated_amount

                # Update message and details if there is a balance due
                if custom_so_balance > 0:
                    custom_count_of_so_due += 1
                    custom_total_amount_due_of_so += custom_so_balance
                    
                    # Format dates directly using strftime
                    formatted_date_from = sales_order.custom_so_from_date.strftime("%d-%m-%Y")
                    formatted_date_to = sales_order.custom_so_to_date.strftime("%d-%m-%Y")
                    
                    message += f"""
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{custom_count_of_so_due}</td>
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{formatted_date_from} to {formatted_date_to}</td>
                                <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">₹{custom_so_balance}/-</td>
                            </tr>
                        """

        message += """
                </tbody>
            </table>
        """

        # Add bank details and final message content
        message += f"""
                <p>Kindly pay the net due amount as on {current_datetime} of ₹ {custom_total_amount_due_of_so:.2f}/- to the below bank details:</p>
                <p><strong>Our Bank Account:</strong><br>
                Lokesh Sankhala and ASSOCIATES<br>
                Account No = 73830200000526<br>
                IFSC = BARB0VJJCRO (fifth character is zero)<br>
                Bank = Bank of Baroda, JC Road, Bangalore-560002<br>
                UPI ID = LSABOB@UPI<br>
                Gpay / Phonepe no = 9513199200
                </p>
                <p>Call us immediately in case of any queries.</p>
                
                <p>Best Regards,<br>LSA Office Account Team<br><a href="mailto:accounts@lsaoffice.com">accounts@lsaoffice.com</a><br>8951692788</p>
            </div>
        </body>
        </html>
        """

        # Generate PDF URL for the first sales order
        pdf_url = frappe.utils.get_url() + f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Order&name={first_sales_order}&format=Payment Pending Sales Order&no_letterhead=0&letterhead=LSA"
        # pdf_url = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00492&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"

        # Download the PDF content
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_content = response.content  # Binary content of the PDF
            pdf_filename = "Sales_Order_Summary.pdf"
        else:
            pdf_content = None
            pdf_filename = None

        # Prepare attachments only if PDF content is available
        attachments = []
        if pdf_content:
            attachments.append({
                'fname': pdf_filename,
                'fcontent': pdf_content
            })

        subject = f"Follow-Up on Your Sales Orders Dues INR {custom_total_amount_due_of_so}/- from Lokesh Sankhala and Associates"
        
        # Pass only valid emails to single_mail_with_attachment
        if email:  # Proceed only if there's at least one valid email in the list
            response = single_mail_with_attachment('LSA Accounts', email, subject, message, cc_email=cc_email, attachments=attachments)

            if response.get('status') == True:
                # Log successful email send
                # create_whatsapp_message_log_email(customer_id, followup_id, email, subject, message, cc_email=cc_email)
                new_whatsapp_log.append("details", {
                    "type": "Customer Followup",
                    "document_id": follow_up_id_int,
                    "email_id": email[0],
                    "customer": customer_id,
                    # "message_id": message_id,
                    "sent_successfully": 1,
                })
                
                frappe.db.set_value('Customer Followup', follow_up_id_int, 'send_mail', 1)
                # followup_doc.save()
            else:
                frappe.log_error(f"Failed to send email to {email}: {response.get('message')}", "Email Send Error")
        else:
            frappe.log_error(f"No valid email found for follow-up ID {followup_id}", "Email Send Error")
    message_template_tem = """Payment Reminder
Dear {customer_name},

You have a due amount to be paid for the following Sales Invoices:

{payment_period_and_amount}

Kindly pay the net due amount as on {current_datetime} of ₹ {total_amount_due}/- to the below bank details:

Our Bank Account:
Lokesh Sankhala and ASSOCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO (fifth character is zero)
Bank = Bank of Baroda, JC Road, Bangalore-560002
UPI ID = LSABOB@UPI
Gpay / Phonepe no = 9513199200

Call us immediately in case of any queries.

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788"""
    new_whatsapp_log.send_date = frappe.utils.now_datetime()
    new_whatsapp_log.sender = frappe.session.user
    new_whatsapp_log.message_type = "Template"
    new_whatsapp_log.communication_platforms = 'Email'
    if cc_email:
        new_whatsapp_log.cc_mail_id = ",".join(cc_email) if isinstance(cc_email, list) else cc_email
        
    new_whatsapp_log.message = message_template_tem
    new_whatsapp_log.insert()


@frappe.whitelist()
def create_message_template(customer_name, customer_id):
    # Get all relevant sales orders
    existing_sales_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer_id, "docstatus": ['in', [0, 1]]}
    )
    current_datetime = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    # Initialize the message template
    message = f"Dear {customer_name},\n\nYou are having a due amount to be paid for the following Sales Invoices:\n"
    
    custom_count_of_so_due = 0
    custom_total_amount_due_of_so = 0.00
    custom_details_of_so_due = {}

    if existing_sales_orders:
        for existing_sales_order in existing_sales_orders:
            sales_order = frappe.get_doc("Sales Order", existing_sales_order.name)

            # Initialize amounts
            custom_so_balance = sales_order.rounded_total
            advance_paid = 0

            # Get payment entries related to the sales order
            pes = frappe.get_all(
                "Payment Entry Reference",
                filters={"reference_doctype": "Sales Order", "reference_name": sales_order.name, "docstatus": 1},
                fields=["name", "parent", "allocated_amount"]
            )
            for pe in pes:
                custom_so_balance -= pe.allocated_amount
                advance_paid += pe.allocated_amount

            # Adjust balance for any related sales invoices
            if custom_so_balance > 0:
                si_item_list = frappe.get_all(
                    "Sales Invoice Item",
                    filters={"sales_order": sales_order.name, "docstatus": 1},
                    fields=["name", "parent"]
                )
                si_list = list(set(si.parent for si in si_item_list))
                for si_name in si_list:
                    si_pe = frappe.get_all(
                        "Payment Entry Reference",
                        filters={"reference_doctype": "Sales Invoice", "reference_name": si_name, "docstatus": 1},
                        fields=["name", "parent", "allocated_amount"]
                    )
                    for pe in si_pe:
                        custom_so_balance -= pe.allocated_amount
                        advance_paid += pe.allocated_amount

            # Update message and details if there is a balance due
            if custom_so_balance > 0:
                custom_count_of_so_due += 1
                custom_total_amount_due_of_so += custom_so_balance
                custom_details_of_so_due[sales_order.name] = [
                    "Unpaid" if custom_so_balance == sales_order.rounded_total else "Partially Paid",
                    sales_order.rounded_total,
                    advance_paid,
                    custom_so_balance,
                    sales_order.custom_so_from_date,
                    sales_order.custom_so_to_date,
                    sales_order.custom_followup_count
                ]
                formatted_date_from = sales_order.custom_so_from_date.strftime("%d-%m-%Y")
                formatted_date_to = sales_order.custom_so_to_date.strftime("%d-%m-%Y")

                message += f"\n{custom_count_of_so_due}. {formatted_date_from} to {formatted_date_to} with due amount ₹{custom_so_balance}/-. \n"

        # Add bank details and final message content
        message += f"""
        \nKindly pay the net due amount as on {current_datetime} of ₹ {custom_total_amount_due_of_so:.2f}/- to the below bank details::

Our Bank Account:
Lokesh Sankhala and ASSOCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO (fifth character is zero)
Bank = Bank of Baroda, JC Road, Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200

Call us immediately in case of any queries.

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788
        """
    
    return message  # Added return statement to return the message template

# @frappe.whitelist()
# def send_whatsapp_message(customer_id, new_mobile, message,followup_id,first_sales_order):
#     try:
#         wa_response = due_so_whatsapp_so_summary_custom(customer_id, new_mobile, message,followup_id,first_sales_order)

#         if wa_response["status"]:
#             frappe.msgprint(_("WhatsApp message sent successfully."))
#         else:
#             frappe.msgprint(wa_response["msg"])
#     except Exception as e:
#         frappe.logger().error(f"Error sending WhatsApp message: {e}")

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import frappe

# @frappe.whitelist()
# def send_email_message(customer_id, customer_name, message_template, email):
#     # Set up email account
#     email_account = frappe.get_doc("Email Account", "LSA Info")
#     sender_email = email_account.email_id
#     your_password = email_account.get_password()

#     smtp_server = 'smtp-mail.outlook.com'
#     smtp_port = 587

#     # Retrieve CC email addresses from Admin Settings
#     admin_settings = frappe.get_doc("Admin Settings")
#     cc_email_list = [email.strip() for email in admin_settings.bulk_email_cc_for_customer_followup.split(',') if email.strip()]

#     # Create the email message
#     email_message = MIMEMultipart()
#     email_message['From'] = sender_email
#     email_message['To'] = email  # Assuming this is the recipient's email
#     email_message['Cc'] = ", ".join(cc_email_list)  # Add CC recipients
#     email_message['Subject'] = f"Follow Up: {customer_name}"

#     email_message.attach(MIMEText(message_template, 'html'))

#     # Combine recipients for sending
#     recipients = [email] + cc_email_list  # Ensure recipient email is used

#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, your_password)
#             server.sendmail(sender_email, recipients, email_message.as_string())
        
#         frappe.msgprint(f"Reminder email sent to {customer_name}.")
#     except Exception as e:
#         frappe.log_error(f"Error sending email to {customer_name}: {str(e)}")


# @frappe.whitelist()
# def due_so_whatsapp_so_summary_custom(customer_id, new_mobile, template,followup_id,first_sales_order):
#     try:
#         # print('first_sales_orderrrrrrrrrrrrr',first_sales_order)
#         whatsapp_instance = frappe.get_all('WhatsApp Instance', filters={
#             'module': 'Operations', 
#             'connection_status': 1, 
#             'active': 1
#         })
        
#         if not whatsapp_instance:
#             return {"status": False, "msg": "WhatsApp API instance is not connected."}
        
#         instance = frappe.get_doc('WhatsApp Instance', whatsapp_instance[0].name)
#         ins_id = instance.instance_id

#         if len(new_mobile) != 10:
#             return {"status": False, "msg": "Please provide a valid 10-digit mobile number."}

#         url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#         params = {
#             "token": ins_id,
#             "phone": f"91{new_mobile}",
#             "message": template,
#             # "link": "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00492&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
#             "link": frappe.utils.get_url() + f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={first_sales_order}&format=Payment%20Pending%20Sales%20Order&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Pending_Sales_Order.pdf"
#         }

#         response = requests.post(url, params=params)
#         response.raise_for_status()
#         response_data = response.json()

#         if response_data.get('status') == 'success':
            
#             message_id = response_data['data']['messageIDs'][0] 
#             # print(customer_id, new_mobile, template, message_id,followup_id)
#             create_whatsapp_message_log(customer_id, new_mobile, template, message_id,followup_id)
#             return {"status": True, "msg": "WhatsApp message sent successfully", "message_id": message_id}
#         else:
#             return {"status": False, "msg": f"Error: {response_data.get('message')}"}

#     except requests.exceptions.RequestException as e:
#         frappe.logger().error(f"Network error: {e}")
#         return {"status": False, "msg": "Network error occurred. Please try again later."}
#     except Exception as e:
#         frappe.logger().error(f"Error: {e}")
#         return {"status": False, "msg": "An unexpected error occurred. Please contact the system administrator."}

# # Function to create a WhatsApp Message Log for email followup
# def create_whatsapp_message_log_email(customer_id, followup_id, email, subject, message, cc_email=None):
#     """Utility function to create a log entry in the WhatsApp Message Log doctype"""
#     try:
#         # Create a new log entry for WhatsApp Message Log
#         whatsapp_message_log = frappe.new_doc('WhatsApp Message Log')
        
#         # Append the relevant details to the log
#         whatsapp_message_log.append("details", {
#             "type": "Customer Followup",
#             "customer": customer_id,
#             "document_id": followup_id,
#         })
        
#         # Add other log metadata
#         whatsapp_message_log.send_date = frappe.utils.now_datetime()
#         whatsapp_message_log.sender = frappe.session.user
#         whatsapp_message_log.message_type = "Template"  # or another type based on the use case
#         # whatsapp_message_log.message = MIMEText(message, 'html') # Log the actual message content
#         whatsapp_message_log.email_id = ",".join(email)  # Log the recipient email
        
#         # # Handle CC email addresses, if provided
#         if cc_email:
#             whatsapp_message_log.cc_mail_id = ",".join(cc_email) if isinstance(cc_email, list) else cc_email
        
#         whatsapp_message_log.communication_platforms = 'Email'  # Log the communication platform as Email
        
#         # Insert the log entry into the database
#         whatsapp_message_log.insert()
#         frappe.db.commit()
        
#         frappe.logger().info(f"WhatsApp Message Log created for Customer {customer_id}.")
    
#     except Exception as e:
#         frappe.logger().error(f"Failed to create WhatsApp Message Log: {e}")


# def create_whatsapp_message_log(customer_id, new_mobile, template,message_id,followup_id):
#     """Utility function to create a log entry in the WhatsApp Message Log doctype"""
#     try:
#         # print(customer_id, new_mobile, template,message_id,followup_id)
#         # Create a new log entry for WhatsApp Message Log
#         whatsapp_message_log = frappe.new_doc('WhatsApp Message Log')
        
#         # Append the relevant details to the log
#         whatsapp_message_log.append("details", {
#             "type": "Customer Followup",
#             "document_id": followup_id,  # Assuming details contain the necessary document information
#             "mobile_number": new_mobile,
#             "customer": customer_id,
#             "message_id": message_id  # Assuming details have message_id
#         })
        
#         # Add other log metadata
#         whatsapp_message_log.send_date = frappe.utils.now_datetime()
#         whatsapp_message_log.sender = frappe.session.user
#         whatsapp_message_log.message_type = "Template"  # or any other type based on the use case
#         whatsapp_message_log.message = template  # Log the actual message content
        
#         # Insert the log entry into the database
#         whatsapp_message_log.insert()
#         frappe.db.commit()
        
#         frappe.logger().info(f"WhatsApp Message Log created for Customer {customer_id}.")

#     except Exception as e:
#         frappe.logger().error(f"Failed to create WhatsApp Message Log: {e}")



#########  Update GST Type in Customer By Mohan  ##########################

import frappe

@frappe.whitelist()
def update_all_gst_types(customer_name=None, gst_no=None):
    if customer_name and gst_no:
        # For individual update
        gst_record = frappe.db.get_value('Gstfile', {'name': gst_no}, 'gst_type')
        
        if gst_record:
            # Update the custom_gst_type in the Customer doctype
            frappe.db.set_value('Customer', customer_name, 'custom_gst_type', gst_record)
            return True  # Return True to indicate success
        else:
            frappe.msgprint(_('No GST record found for GST No: {0}').format(gst_no))
            return False
    else:
        # For bulk update
        customers = frappe.get_all('Customer', filters={'custom_gst_no': ['!=', '']}, fields=['name', 'custom_gst_no'])
        
        for customer in customers:
            gst_record = frappe.db.get_value('Gstfile', {'name': customer.custom_gst_no}, 'gst_type')
            
            if gst_record:
                # Update the custom_gst_type in the Customer doctype
                frappe.db.set_value('Customer', customer.name, 'custom_gst_type', gst_record)

        return True  # Return True to indicate bulk success



import frappe

@frappe.whitelist()
def get_gst_no_records_for_empty():
    # Get customers with empty custom_gst_no
    customers = frappe.get_all('Customer', filters={'custom_gst_no': ''}, fields=['name'])

    records = []
    for customer in customers:
        # Fetch the gst_no from Gstfile based on some condition
        gst_no = frappe.db.get_value('Gstfile', {'customer_id': customer.name}, 'name')  # Adjust the filter as needed

        if gst_no:
            records.append({
                'name': customer.name,
                'gst_no': gst_no
            })

    # Return both the records and the count
    return {
        'records': records,
        'count': len(records)
    }




@frappe.whitelist()
def update_gst_category():
    # Fetch all customers with a valid custom_gst_no
    customers = frappe.get_all('Customer', filters={'custom_gst_no': ['!=', '']}, fields=['name', 'custom_gst_type', 'custom_custom_gst_category'])

    updated_count = 0
    for customer in customers:
        # Determine the new GST Category based on the GST Type
        new_gst_category = None
        if customer.custom_gst_type == 'Regular' or customer.custom_gst_type == 'QRMP':
            new_gst_category = 'Registered Regular'
        elif customer.custom_gst_type == 'Composition':
            new_gst_category = 'Registered Composition'

        if new_gst_category and customer.custom_custom_gst_category != new_gst_category:
            # Update the customer's GST Category if necessary
            frappe.db.set_value('Customer', customer.name, 'custom_custom_gst_category', new_gst_category)
            updated_count += 1

    frappe.db.commit()
    return f'{updated_count} customers updated'

