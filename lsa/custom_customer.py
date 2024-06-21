import frappe
import requests
from frappe import _
from frappe.utils import today
from datetime import datetime


@frappe.whitelist()
def sync_customer(customer_id=None):
    try:
        followup_button,followup_values,values,open_followup,open_followup_i=sync_sales_orders_customer(customer_id)
        services_values=sync_services_customer(customer_id)
        pricing_value=sync_services_pricing(customer_id)
        turnover_list=sync_turnover_gst(customer_id)
        disabled_services_values= sync_disabled_services_customer(customer_id)
        if [followup_button,followup_values,values,open_followup,open_followup_i] or services_values or pricing_value:

            return {"status":"Synced successfully.","followup_button":followup_button,"values":values,
                        "followup_values":followup_values,"services_values":services_values,"open_followup":open_followup,
                        "open_followup_i":open_followup_i,"pricing_value":pricing_value,"turnover_list":turnover_list,
                        'disabled_services_values':disabled_services_values}
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

def sync_services_customer(customer_id=None):

    master_service_fields = {
        "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
    }

    services_values=[]
    chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
    for chargeable_service in chargeable_services:
        # print(chargeable_service)
        chargeable_service_values=frappe.get_all(chargeable_service.name,
                                           filters={"customer_id":customer_id,
                                                   "enabled":1},
                                            fields=master_service_fields[chargeable_service.name][1]
                                            )
        # print(chargeable_service_values)
        for chargeable_service_value in chargeable_service_values:
            chargeable_service_value=[chargeable_service_value[i] for i in master_service_fields[chargeable_service.name][1] ]
            # print(chargeable_service_value)
            service_slug="-".join([i.lower() for i in ((chargeable_service.name).split(" "))])
            chargeable_service_value.append(service_slug)
            chargeable_service_value.append(chargeable_service.name)
            services_values.append(chargeable_service_value)
    # print(services_values)
            
    Client_Notices=["client-notices",["name","assessee_name", "notices_type","registration_number", "financial_year","executive_name"]]
    chargeable_service_values_n=frappe.get_all("Client Notices",
                                           filters={"cid":customer_id,
                                                #    "enabled":1
                                                   },
                                            fields=Client_Notices[1],
                                            )
    for chargeable_service_value_n in chargeable_service_values_n:
            chargeable_service_value_n=[chargeable_service_value_n[i] for i in Client_Notices[1] ]
            # print(chargeable_service_value)
            chargeable_service_value_n.insert(5, 1.00)
            chargeable_service_value_n.insert(5, "Y")
            chargeable_service_value_n.insert(5, 1.00)
            chargeable_service_value_n.append(None)
            
            
            service_slug=Client_Notices[0]
            chargeable_service_value_n.append(service_slug)
            chargeable_service_value_n.append("Client Notices")
            services_values.append(chargeable_service_value_n)
    return services_values


##################Srikanth's Code Start#########################################################################################



def sync_disabled_services_customer(customer_id=None):

    master_service_fields = {
        "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
    }

    services_values=[]
    chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
    for chargeable_service in chargeable_services:
        # print(chargeable_service)
        chargeable_service_values=frappe.get_all(chargeable_service.name,
                                           filters={"customer_id":customer_id,
                                                   "enabled":0},
                                            fields=master_service_fields[chargeable_service.name][1]
                                            )
        # print(chargeable_service_values)
        for chargeable_service_value in chargeable_service_values:
            chargeable_service_value=[chargeable_service_value[i] for i in master_service_fields[chargeable_service.name][1] ]
            # print(chargeable_service_value)
            service_slug="-".join([i.lower() for i in ((chargeable_service.name).split(" "))])
            chargeable_service_value.append(service_slug)
            chargeable_service_value.append(chargeable_service.name)
            services_values.append(chargeable_service_value)
    # print(services_values)
            
    
    return services_values


##################Srikanth's Code End#########################################################################################


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
    return followup_button,followup_values,[so_details,custom_count_of_so_due,custom_total_amount_due_of_so,custom_details_of_so_due],open_followups,open_followup_i
                        
    

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
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["LSA Accounts Manager","LSA Account Executive"]
        doc_wa_perm_roles=["GST Front Desk Team","Lsa Front Desk CRM Executive(A,B)"]

        for role in roles:
            if role in doc_perm_roles:
                status = True
            if role in doc_wa_perm_roles:
                wa_status = True
        

        return {"status": status, "value": [roles],"wa_status":wa_status}

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
IFSC = BARB0VJJCRO
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

@frappe.whitelist()
def due_so_whatsapp(docname,paymentstatus,new_mobile,template):
    # new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
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
    print(new_status,old_status)
    # Check if the status has changed
    if True:
        try:
            linked_doctypes = {
                                "Client Notices":("cid","customer_status"),
                                "DSC Digital Sign":("customer_id","customer_status"), 
                                "ESI File":("customer_id","customer_status"), 
                                "Gst Filling Data":("cid","customer_status"),
                                "Gst Yearly Filing Summery":("cid","customer_status"), 
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
def disable_customer(customer_id):
    try:
        customer_doc=frappe.get_doc("Customer",customer_id)
        master_service_fields = {
            "Gstfile": ["gst_file", ["name", "company_name", "gst_number", "gst_user_name", "gst_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "IT Assessee File": ["it_assessee_file", ["name", "assessee_name", "pan", "pan", "it_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "MCA ROC File": ["mca_roc_file", ["name", "company_name", "cin", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "Professional Tax File": ["professional_tax_file", ["name", "assessee_name", "registration_no", "user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "TDS File": ["tds_file", ["name", "deductor_name", "tan_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "ESI File": ["esi_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
            "Provident Fund File": ["provident_fund_file", ["name", "assessee_name", "registartion_no", "trace_user_id", "trace_password","current_recurring_fees","frequency","annual_fees","executive_name","last_filed"]],
        }
        serv_freq={"M":"Monthly",
                   "Q":"Quarterly",
                   "H":"Half Yearly",
                   "Y":"Yearly",}

        chargeable_services=frappe.get_all("Customer Chargeable Doctypes")
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
        executive_list={'lokesh.bwr@gmail.com', 'khushboo.r@lsaoffice.com', 'latha.st@lsaoffice.com', 'vinay.m@lsaoffice.com', 'Shriramu.ms@lsaoffice.com',"vatsal.k@360ithub.com"}
        executive_list=[]
        admin_setting_doc = frappe.get_doc("Admin Settings")
        for i in admin_setting_doc.customer_status_change_mail:
            executive_list.append(i.user)
        executive_list = set(executive_list)
        
        for chargeable_service in chargeable_services:
            # print(chargeable_service)
            chargeable_service_values=frappe.get_all(chargeable_service.name,
                                            filters={"customer_id":customer_id,
                                                    "enabled":1},
                                            fields=["name",master_service_fields[chargeable_service.name][1][1],"executive"]
                                                )
            # print(chargeable_service_values)
            for chargeable_service_value in chargeable_service_values:
                # print(chargeable_service.name,chargeable_service_value.name)
                chargeable_service_doc=frappe.get_doc(chargeable_service.name,chargeable_service_value.name)
                chargeable_service_doc.enabled=0
                chargeable_service_doc.save()
                executive_list.add(chargeable_service_value["executive"])
                body += f"""
                    <tr>
                        <td style="border: solid 2px #bcb9b4;">{count}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service.name}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service_doc.name}</td>
                        <td style="border: solid 2px #bcb9b4;">{chargeable_service_value[master_service_fields[chargeable_service.name][1][1]]}</td>                      
                        <td style="border: solid 2px #bcb9b4;">{serv_freq[chargeable_service_doc.frequency]}</td>
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

        subject = f"Customer with CID {customer_id} is disabled"
        message = f"""
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
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Disabled</td>
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
            
        frappe.sendmail(
                # recipients=recipients,  # Use the list of combined email addresses
                recipients=list(executive_list),
                subject=subject,
                message=message
            )
        # print(list(executive_list),subject,message)
        return {"status":True,"message": "Customer disabled successfully","executive_list":list(executive_list)}
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to disable customer")
        # print(f"{e}")
        return {"status":False,"message": f"Failed to disable customer {e}"}
    
#######################################Srikanth Code Start#####################################################################

 
@frappe.whitelist()
def send_status_update_notification(name, new_status, previous_status, reason, customer_email, modified_by, time_of_change, cust_name):
    try:
        # Fetch the fields from "Recurring Service Pricing"
        rsp_list= frappe.get_all("Recurring Service Pricing", filters={"customer_id": name,"status":"Approved"})
        
 
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
            subject = f"CID {name} Customer Status Changed from {previous_status} to {new_status}"
            message = f"""
                <p>Dear LSA Team,<br><br> There are some changes in the status of following customer. Please make a note of it, before maving forward with our services.</p>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer ID</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{name}">{name}</a></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Name</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/customer/{name}">{cust_name}</a></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Customer Status</td>
                        <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Changed from {previous_status} to {new_status}</td>
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
                master_list = frappe.get_all(i.name, filters={"customer_id": name}, fields=["executive"])
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
 
            # Convert the set back to a list
            # recipients = list(all_emails)
            recipients = list(all_emails)
            # print(recipients)
            # test_emails = ['srikanth.p_cse2019@svec.edu.in']
            # print(test_emails)
            # print("Hellooooooo")
 
            # Send the email
            frappe.sendmail(
                # recipients=recipients,  # Use the list of combined email addresses
                recipients=recipients,
                subject=subject,
                message=message
            )
 
            return {"message": "Notification sent successfully!","executive_emails":all_emails}
        else:
            frappe.log_error(message=f"No RSP Exist for the customer {name}", title="Failed to send status update notification")
    except Exception as e:
        # print(e)
        frappe.log_error(message=str(e), title="Failed to send status update notification")
        return {"message": "Failed to send notification"}

#######################################Srikanth Code Start#####################################################################



