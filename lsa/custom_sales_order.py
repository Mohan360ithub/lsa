import frappe
import requests,random,json
from frappe import _
from frappe.utils import today
from datetime import datetime




@frappe.whitelist()
def sync_sales_orders_followup(so_id=None):
    try:
        
        followup_values={"values":[],}
        if so_id:
            existing_followups=frappe.get_all("Customer Followup",
                                    fields=["name","sales_order_summary"])
            existing_so_followups=[i.name for i in existing_followups if so_id in i.sales_order_summary]
            # print(existing_sales_orders)
            if existing_so_followups:
                for existing_so_followup in existing_so_followups:
                    # print(existing_sales_order)
                    followup=frappe.get_doc("Customer Followup",existing_so_followup)


                    followup_values["values"]+=[[followup.customer_id,followup.name,
                                                followup.status,followup.total_remaining_balance,
                                                followup.followup_date,followup.next_followup_date,
                                                followup.executive_name,followup.followup_note]]
            #############################################################################################
            existing_payments=frappe.get_all("Payment Entry Reference",
                                              filters={"reference_name":so_id,"docstatus":1},
                                                fields=["name","creation","parent","total_amount","outstanding_amount",
                                                        "allocated_amount"])

            
            so_doc=frappe.get_doc("Sales Order",so_id)
            so_balance=so_doc.rounded_total
            payment_status = "Unpaid"
            existing_payments_list=[]
            for existing_payment in existing_payments:

                reference_date=''
                mode_of_payment=''
                existing_payment_entry=frappe.get_all("Payment Entry",
                                              filters={"name":existing_payment.parent},
                                                fields=["name","reference_date","paid_to"])
                reference_date=existing_payment_entry[0].reference_date
                mode_of_payment=existing_payment_entry[0].paid_to

                existing_payment_list=[existing_payment.parent,
                                       existing_payment.allocated_amount,reference_date,mode_of_payment]
                so_balance-=existing_payment.allocated_amount
                existing_payments_list.append(existing_payment_list)


            if so_balance == 0:
                payment_status = "Cleared"
            elif so_doc.rounded_total>so_balance > 0:
                payment_status = "Partially Paid"
            # print(existing_payments_list)

            payment_links=[]
            payment_links=frappe.get_all("Payment Link Log",
                                                    filters={"sales_order":so_id},
                                                    fields=["name","sales_order","customer_id","total_amount","date_of_generation","link_short_url","enabled"])
            
            return {"status":"Synced successfully.",
                    "followup_values":followup_values,
                    "payment_values":existing_payments_list,
                    "so_balance":so_balance,
                    "payment_status":payment_status,
                    "payment_links":payment_links}
        # else:
        #     return {"status":"Synced successfully."}
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False


@frappe.whitelist()
def whatsapp_button(user_email=None):
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])
            return {"status": True}

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["LSA Accounts Manager","LSA Account Executive"]

        for role in roles:
            if role in doc_perm_roles:
                status = True
                break

        return {"status": status, "value": [roles]}

    except Exception as e:
        #print(e)
        return {"status": "Failed"}


@frappe.whitelist()
def gst_tax_type(customer_id=None):
    if customer_id:
        try:
            # gst_tax_type=""
            comp_gst_state=frappe.get_all("Company",fields=["custom_state"])
            
            cust_gst_state=frappe.get_all("Customer",fields=["custom_state"],filters={"name":customer_id})

            if comp_gst_state and cust_gst_state:

                comp_gst_state=comp_gst_state[0].custom_state
                cust_gst_state=cust_gst_state[0].custom_state
                if comp_gst_state==cust_gst_state:
                    gst_tax_type="Output GST In-state - IND"
                else:
                    gst_tax_type="Output GST In-state - IND"
        
                return {"status":True,"gst_tax_type":gst_tax_type}
        except Exception as er:
            return {"status":True,"error":er}



@frappe.whitelist()
def create_razorpay_payment_link_sales_order(amount, invoice_name,customer,customer_name,from_date,to_date,actual_amount):
    payment_links = frappe.get_all("Payment Link Log",
                                   filters={"sales_order":invoice_name,"enabled":1})
    if payment_links:
        return
    
    # Your Razorpay API key and secret
    razorpay_api = frappe.get_doc('Razorpay Api')
    razorpay_api_url = razorpay_api.razorpay_api_url
    razorpay_key_id = razorpay_api.razorpay_api_key
    razorpay_key_secret = razorpay_api.get_password('razorpay_secret')


    # Convert the amount to an integer (representing paise)
    amount_in_paise = int(float(amount) * 100)
    # print("Testing==============")
    # Create a Razorpay order
    order_params = {
        "amount": amount_in_paise,
        "currency": "INR",
        # "accept_partial": "0",
        # "first_min_partial_amount": 100,
        "description": f"Sales order for the period from {from_date} to {to_date}",
        "notes": {
            "invoice_name": invoice_name
        },
        # "accept_partial": False,
        # "expire_by": 1691097057,
        "reference_id": invoice_name,
        "callback_url": f"https://online.lsaoffice.com/api/method/lsa.pankaj1.get_razorpay_payment_details?razorpay_payment_link_reference_id={invoice_name}&customer={customer}&actual_amount={actual_amount}",
        "callback_method": "get"
    }
 
    try:
        # Use the requests library to send a POST request
        # order = requests.post(
        #     custom_razorpay_api_url,
        #     json=order_params,
        #     auth=(razorpay_key_id, razorpay_key_secret)  # Add authentication here
        # )

        # # Check if the request was successful (status code 2xx)
        # order.raise_for_status()

        def generate_pl(custom_razorpay_api_url,customer,actual_amount,order_params,auth,reference_id,link_js=None,status=400):
            if status!=200:

                random_number = random.randint(100, 999)

                reference_id_with_rn=reference_id+'-'+str(random_number)

                order_params["reference_id"]=reference_id_with_rn
                order_params["callback_url"]=f"https://online.lsaoffice.com/api/method/lsa.pankaj1.get_razorpay_payment_details?razorpay_payment_link_reference_id={reference_id_with_rn}&customer={customer}&actual_amount={actual_amount}"

                link_json = requests.post(
                    custom_razorpay_api_url,
                    json=order_params,
                    auth=(razorpay_key_id, razorpay_key_secret)  # Add authentication here
                )
                status=link_json.status_code

                return generate_pl(custom_razorpay_api_url,customer,actual_amount,order_params,auth,reference_id,link_json,status)
            else:
                return link_js
            
        auth=(razorpay_key_id, razorpay_key_secret)
        order=generate_pl(razorpay_api_url,customer,actual_amount,order_params,auth,invoice_name)

        # Get the JSON response
        response_json = order.json()
        link_id=response_json.get('id')

        # Extract short_url from the response
        short_url = response_json.get('short_url')

        # Optionally, you can store custom_payment_link in a database or use it as needed

        # Update the Sales Invoice document with the short_url
        doc = frappe.get_doc('Sales Order', invoice_name)
        doc.custom_razorpay_payment_url = short_url
        doc.save()

        new_payment_link = frappe.get_doc({
            "doctype": "Payment Link Log",
            "customer_id": customer,
            "sales_order":invoice_name,
            "total_amount":amount,
            "link_short_url":short_url,
            "link_id":link_id,
            "live_link":1,

        })
        new_payment_link.insert()

        return {"status":True,"msg":(f'Successfully created Razorpay order. Short URL: {short_url}')}
       

    except requests.exceptions.HTTPError as errh:
        #frappe.msgprint(f'HTTP Error: {errh}')
        return {"status":False,"msg":(f'Failed to generate the Razorpay payment link:{errh}')}
    except requests.exceptions.ConnectionError as errc:
        #frappe.msgprint(f'Error Connecting: {errc}')
        return {"status":False,"msg":(f'Failed to generate the Razorpay payment link:{errc}')}
    except requests.exceptions.Timeout as errt:
        #frappe.msgprint(f'Timeout Error: {errt}')
        return {"status":False,"msg":(f'Failed to generate the Razorpay payment link:{errt}')}
    except requests.exceptions.RequestException as err:
        #frappe.msgprint(f'Request Exception: {err}')
        return {"status":False,"msg":(f'Failed to generate the Razorpay payment link:{err}')}




#####################################################################################################
########################## Selected Sales Order Whatsapp(BULK)  ##################
################################## (SO with PDF Button)###########################


@frappe.whitelist()
# def send_whatsapp_message(docname, customer, customer_id, from_date, to_date, total,new_mobile):
def send_so_whatsapp_message(new_mobile):
    new_mobile_dict = json.loads(new_mobile)
    count = 0
    success_number = []
    success_sales_invoices = []
    whatsapp_items = []
    # instance_id=whatsapp_demo.instance_id
    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        whatsapp_demo_doc = instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        connection_status = whatsapp_demo_doc.connection_status
        mobile_numbers =[]
        
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        for invoice_key in new_mobile_dict:
                # Fetch the sales invoice document based on the key
                invoice_doc = frappe.get_doc('Sales Order', invoice_key)
                
                from_date = invoice_doc.custom_so_from_date
                to_date = invoice_doc.custom_so_to_date
                customer = invoice_doc.customer
                total = invoice_doc.rounded_total
                customer_name = invoice_doc.customer_name
                docname = invoice_doc.name
                
                ins_id = whatsapp_demo_doc.instance_id


                try:
                    # Check if the mobile number has 10 digits
                    if len(new_mobile_dict[invoice_key]) != 10:
                        frappe.msgprint("Please provide a valid 10-digit mobile number.")
                        return
                    
                    sales_invoice = frappe.get_all('Sales Invoice Item',filters={'sales_order':invoice_doc.name,'docstatus':("in",[0,1])},fields=["parent"])
                    if sales_invoice:
                        frappe.logger().error(f"A Sales Invoice {sales_invoice[0].parent} already exist for the Sales Order")
                        continue
                        # return {"status":False,"msg":f"A Sales Invoice <a href='https://online.lsaoffice.com/app/sales-invoice/{sales_invoice[0].parent}'>{sales_invoice[0].parent}</a> already exist for the Sales Order"}
                    
                    
                    payment_link=""
                    if invoice_doc.custom_razorpay_payment_url:
                        payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"

                    due_amount_message=f"due for amount of Rs {total}/-"

                    pe_list = frappe.get_all('Payment Entry Reference',filters={"reference_doctype":"Sales Order",'reference_name':invoice_doc.name,'docstatus':1},fields=["name","allocated_amount","parent"])
                    if pe_list:
                        advance_paid_amount=0
                        balance_amount=invoice_doc.rounded_total
                        for pe in pe_list:
                            advance_paid_amount+=pe.allocated_amount
                            balance_amount-=pe.allocated_amount
                        due_amount_message=f"partially paid. You have paid Rs {advance_paid_amount}/- out of net total of Rs {total}/-"
                        payment_link=""


                    payment_link=""
                    if invoice_doc.custom_razorpay_payment_url:
                        payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
                    
                    mobile_numbers.append(new_mobile_dict[invoice_key])


                    
            
                    message = f'''Dear {customer_name},
            
Your Sale Invoice for {from_date} to {to_date} period is {due_amount_message}. Kindly pay on below bank amount details
        
Our Bank Account
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200
{payment_link}
        
Call us immediately in case of query.
        
Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788'''
                    
                    ########################### Below commented link is work on Live #######################
                    link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
                    if pe_list:
                        link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
            
                    # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
            
                    url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
                    params_1 = {
                        "token": ins_id,
                        "phone": f"91{new_mobile_dict[invoice_key]}",
                        "message": message,
                        "link": link
                    }
                    # print(new_mobile_dict[invoice_key])
                    # whatsapp_items.append( {"type": "Sales Invoice",
                    #                         "document_id": invoice_doc.name,
                    #                         "mobile_number": new_mobile_dict[invoice_key],
                    #                         "customer":invoice_doc.customer,})
                    
                    response = requests.post(url, params=params_1)
                    response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
                    response_data = response.json()

                    message_id = response_data['data']['messageIDs'][0]

                    # Check if the response status is 'success'
                    if response_data.get('status') == 'success':
                        # Log the success

                        frappe.logger().info("WhatsApp message sent successfully")
                        # print("send succesfully")
                        sales_invoice_whatsapp_log.append("details", {
                                                        "type": "Sales Order",
                                                        "document_id": invoice_doc.name,
                                                        "mobile_number": new_mobile_dict[invoice_key],
                                                        "customer":invoice_doc.customer,
                                                        "message_id":message_id
                                                                    
                                                        # Add other fields of the child table row as needed
                                                    })
                    else:
                        frappe.logger().error(f"Failed to send Whatsapp Message for {invoice_doc.name}")
            
            
                    frappe.logger().info(f"Sales Order response: {response.text}")
            
                    # Create a new WhatsApp Message Log document
                    
                    
                    count += 1 
                    success_number+=[new_mobile_dict[invoice_key]]
                    success_sales_invoices+=[invoice_key]

                
            
                except requests.exceptions.RequestException as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Network error: {e}")
                    # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
                except Exception as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Error: {e}")
                    # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
        message = '''Dear {customer_name},
            
Your Sale Invoice for {from_date} to {due_date} period is [due for amount of Rs {total}/-] OR [partially paid. You have paid Rs {advance_paid_amount}/- out of net total of Rs {total}/-]. Kindly pay on below bank amount details
            
Our Bank Account
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200
{payment_link}
        
Call us immediately in case of query.
        
Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788'''
        
        # sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
        # sales_invoice_whatsapp_log.customer = invoice_doc.customer
        # sales_invoice_whatsapp_log.posting_date = from_date
        sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
        # sales_invoice_whatsapp_log.total_amount = total
        # sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
        sales_invoice_whatsapp_log.sender = frappe.session.user
        # sales_invoice_whatsapp_log.sales_invoice =  docname
        sales_invoice_whatsapp_log.type = "Template"
        sales_invoice_whatsapp_log.message = message
        # sales_invoice_whatsapp_log.file = link
        # sales_invoice_whatsapp_log.details = whatsapp_items
        # print( "Sales Invoice",invoice_salesinvoice,mobile_number,invoice_doc.customer)
        # print(whatsapp_items)
        sales_invoice_whatsapp_log.insert()
        if len(success_number)==len(new_mobile_dict):
            return {"status":True,"msg":"WhatsApp messages sent successfully"}
        else:
            msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
            return {"status":True,"msg":msg}
       
    else:
        return {"status":False,"msg":"Your WhatApp API instance is not connected"}


########################################Single Sales Order template with PDF###########################################################

@frappe.whitelist(allow_guest=True)
def whatsapp_so_template(docname,from_date,to_date,new_mobile):
    #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Sales Order', docname)
        customer = invoice_doc.customer
        total = invoice_doc.rounded_total
        customer_name = invoice_doc.customer_name
        docname = invoice_doc.name

        sales_invoice = frappe.get_all('Sales Invoice Item',filters={'sales_order':invoice_doc.name,'docstatus':("in",[0,1])},fields=["parent"])
        if sales_invoice:
            return {"status":False,"msg":f"A Sales Invoice <a href='https://online.lsaoffice.com/app/sales-invoice/{sales_invoice[0].parent}'>{sales_invoice[0].parent}</a> already exist for the Sales Order"}
        
        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id


        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return
            
            payment_link=""
            if invoice_doc.custom_razorpay_payment_url:
                payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
            
            due_amount_message=f"due for amount of Rs {total}/-"

            pe_list = frappe.get_all('Payment Entry Reference',filters={"reference_doctype":"Sales Order",'reference_name':invoice_doc.name,'docstatus':1},fields=["name","allocated_amount","parent"])
            if pe_list:
                advance_paid_amount=0
                balance_amount=invoice_doc.rounded_total
                for pe in pe_list:
                    advance_paid_amount+=pe.allocated_amount
                    balance_amount-=pe.allocated_amount
                due_amount_message=f"partially paid. You have paid Rs {advance_paid_amount}/- out of net total of Rs {total}/-"
                payment_link=""
            


            
            
            message = f'''Dear {customer_name},

Your Sale Invoice for {from_date} to {to_date} period is {due_amount_message}. Kindly pay on below bank amount details

Our Bank Account
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200
{payment_link}

Call us immediately in case of query.

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788'''
            
            ########################### Below commented link is work on Live #######################
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            if pe_list:
                link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"

            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }

            whatsapp_items.append( {"type": "Sales Order",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile,
                                    "customer":invoice_doc.customer,})
            
            response = requests.post(url, params=params_1)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            message_id = response_data['data']['messageIDs'][0]


            # Check if the response status is 'success'
            if response_data.get('status') == 'success':
                # Log the success

                frappe.logger().info("WhatsApp message sent successfully")
                sales_invoice_whatsapp_log.append("details", {
                                                "type": "Sales Order",
                                                "document_id": invoice_doc.name,
                                                "mobile_number": new_mobile,
                                                "customer":invoice_doc.customer,
                                                "message_id":message_id
                                                            
                                                # Add other fields of the child table row as needed
                                            })
                sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
                sales_invoice_whatsapp_log.sender = frappe.session.user
                sales_invoice_whatsapp_log.type = "Template"
                sales_invoice_whatsapp_log.message = message
                sales_invoice_whatsapp_log.insert()
                return {"status":True,"msg":"WhatsApp message sent successfully"}
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
    


########################################Single Sales Order Custom with PDF###########################################################

@frappe.whitelist(allow_guest=True)
def whatsapp_so_custom(docname,new_mobile,cust_message):
    #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Sales Order', docname)
        customer = invoice_doc.customer
        total = invoice_doc.rounded_total
        customer_name = invoice_doc.customer_name
        docname = invoice_doc.name

        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id


        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return
            
            message = cust_message

            pe_list = frappe.get_all('Payment Entry Reference',filters={"reference_doctype":"Sales Order",'reference_name':invoice_doc.name,'docstatus':1},fields=["name","allocated_amount","parent"])
            if pe_list:
                advance_paid_amount=0
                balance_amount=invoice_doc.rounded_total
                for pe in pe_list:
                    advance_paid_amount+=pe.allocated_amount
                    balance_amount-=pe.allocated_amount
            
            
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            if pe_list:
                link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"

            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }

            whatsapp_items.append( {"type": "Sales Order",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile,
                                    "customer":invoice_doc.customer,})
            
            response = requests.post(url, params=params_1)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            message_id = response_data['data']['messageIDs'][0]


            # Check if the response status is 'success'
            if response_data.get('status') == 'success':
                # Log the success

                frappe.logger().info("WhatsApp message sent successfully")
                sales_invoice_whatsapp_log.append("details", {
                                                "type": "Sales Order",
                                                "document_id": invoice_doc.name,
                                                "mobile_number": new_mobile,
                                                "customer":invoice_doc.customer,
                                                "message_id":message_id
                                                            
                                                # Add other fields of the child table row as needed
                                            })
                sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
                sales_invoice_whatsapp_log.sender = frappe.session.user
                sales_invoice_whatsapp_log.type = "Custom"
                sales_invoice_whatsapp_log.message = message
                sales_invoice_whatsapp_log.insert()
                return {"status":True,"msg":"WhatsApp message sent successfully"}
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
    


#######################################(Bulk Sales Order Custom Message Button)###########################################


@frappe.whitelist()
def send_bulk_custom_so_whatsapp_message(values_prompt):
    try:
        # Parse the values_prompt string into a dictionary
        values_dict = json.loads(values_prompt)
        count = 0
        success_number = []
        success_sales_invoices = []

        # Extract the custom message from the dictionary
        message = values_dict['custom_message']
        del values_dict['custom_message']

        # Extract the mobile numbers from the dictionary
        new_mobile_dict = values_dict
        whatsapp_demo =  frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
        if whatsapp_demo:
            whatsapp_demo_doc = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
            connection_status = whatsapp_demo_doc.connection_status
            
            sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
            for invoice_key in new_mobile_dict:
                
                # Fetch the sales invoice document based on the key
                invoice_doc = frappe.get_doc('Sales Order', invoice_key)               
                # Now you can access details from the invoice document
                
                from_date = invoice_doc.transaction_date
                total = invoice_doc.total
                ins_id = whatsapp_demo_doc.instance_id

                pe_list = frappe.get_all('Payment Entry Reference',filters={"reference_doctype":"Sales Order",'reference_name':invoice_doc.name,'docstatus':1},fields=["name","allocated_amount","parent"])
                if pe_list:
                    advance_paid_amount=0
                    balance_amount=invoice_doc.rounded_total
                    for pe in pe_list:
                        advance_paid_amount+=pe.allocated_amount
                        balance_amount-=pe.allocated_amount
                
                
                link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
                if pe_list:
                    link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
                # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"


                try:
                    # Check if the mobile number has 10 digits
                    if len(new_mobile_dict[invoice_key]) != 10:
                        frappe.msgprint("Please provide a valid 10-digit mobile number.")
                                                   
                    url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
                    params_1 = {
                        "token": ins_id,
                        "phone": f"91{new_mobile_dict[invoice_key]}",
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
                        # frappe.msgprint("Whatsapp Message Sent successfully")
                        # frappe.logger().info("WhatsApp message sent successfully")
                        # print("send succesfully")
                        sales_invoice_whatsapp_log.append("details", {
                                    "type": "Sales Order",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile_dict[invoice_key],
                                    "customer":invoice_doc.customer,
                                    "message_id":message_id                                                
                                    # Add other fields of the child table row as needed
                                })


                    else:
                        return {"status":False,"msg":"Your WhatApp API instance is not connected"}        
            
                    frappe.logger().info(f"Sales Order response: {response.text}")
                    success_number+=[new_mobile_dict[invoice_key]]
                    success_sales_invoices+=[invoice_key]
            
                                   
                    count += 1 
                                
                except requests.exceptions.RequestException as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Network error: {e}")
                    # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
                    
                    
                except Exception as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Error: {e}")
                    # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
  
        # Create a new WhatsApp Message Log document
            # sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
            # sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
            # sales_invoice_whatsapp_log.customer = invoice_doc.customer
            # sales_invoice_whatsapp_log.posting_date = from_date
            sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
            # sales_invoice_whatsapp_log.total_amount = total
            # sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
            sales_invoice_whatsapp_log.sender = frappe.session.user
            # sales_invoice_whatsapp_log.sales_invoice =  docname
            sales_invoice_whatsapp_log.message = message
            sales_invoice_whatsapp_log.message_type = "Custom"
            sales_invoice_whatsapp_log.insert(ignore_permissions=True)

            if len(success_number)==len(new_mobile_dict):
                return {"status":True,"msg":"WhatsApp messages sent successfully"}
            else:
                msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
                return {"status":True,"msg":msg}      

        else:
            return {"status":False,"msg":"Your WhatApp API instance is not connected"}
    except Exception as er:
        return {"status":False,"msg":f"Error: {er}"}


