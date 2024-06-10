import frappe
import time,json,requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from frappe.model.document import Document



@frappe.whitelist()
def create_sales_invoice(so_id=None):  
	so_fields=["customer","customer_name","total","total_qty",
				"taxes_and_charges","total_taxes_and_charges","grand_total","rounding_adjustment",
				"rounded_total","in_words","advance_paid","apply_discount_on",
				"additional_discount_percentage","discount_amount"]       
	so_list=frappe.get_all("Sales Order",filters={"name":so_id},fields=so_fields)
	if so_list: 
		# so_doc=frappe.get_doc("Sales Order",so_id)       
		
		
		items_fields=["item_code","item_name","description","gst_hsn_code","qty","uom","rate","amount",
				"gst_treatment","net_rate","taxable_value","net_amount"]

		tax_fields=["charge_type","description","account_head","included_in_print_rate","cost_center",
				"rate","account_currency","base_tax_amount","tax_amount","tax_amount_after_discount_amount",
				"base_total"]

		si_dict={}
		si_dict["doctype"]= "Sales Invoice"
		for so_field in so_fields:
			si_dict[so_field]=so_list[0][so_field] 
		si_dict["outstanding_amount"]=0.00
		
		items_list=[]
		so_items=frappe.get_all("Sales Order Item",filters={"parent":so_id},fields=items_fields)
		for so_item in so_items:
			item_dict={}
			for field in items_fields:
				item_dict[field]=so_item[field]
			item_dict["sales_order"]=so_id
			items_list.append( item_dict)

		tax_items_list=[]
		tax_items=frappe.get_all("Sales Taxes and Charges",filters={"parent":so_id},fields=tax_fields)
		for tax_item in tax_items:
			tax_dict={}
			for field in tax_fields:
				tax_dict[field]=tax_item[field]
			tax_items_list.append(tax_dict)


		
		si_dict["items"]=items_list
		si_dict["taxes"]=tax_items_list

		si_doc = frappe.get_doc(si_dict)
		
		si_doc.insert()


		return "SI created Successfully"
		

 
@frappe.whitelist()
def send_whatsapp_message(sales_invoice,new_mobile):
    try:
        resp={}
        # Check if the mobile number has 10 digits
        if len(new_mobile) != 10:
            frappe.msgprint("Please provide a valid 10-digit mobile number.")
            return
        
        instance_id="609bc2d1392a635870527076"
 
        message = f'''Dear Test,
 
Your Sale Order for [from_date] to [to_date] period is due for amount of Rs [total]/- Kindly pay on below bank amount details
 
Our Bank Account
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200
 
Call us immediately in case of query.
 
Best Regards,
LSA Office Account Team
accounts@lsaoffice.com'''
        
        kvp={"doctype":"Custom DocPerm","parent":"Sales Invoice","parentfield":"permissions","parenttype":"DocType",
             "idx":0,"permlevel":0,"role":"Guest","read":0,"write":0,"submit":0,"cancel":0,
             "delete":0,"amend":0,"create":0,"report":0,"export":0,"import":0,"share":0,"print":1,"email":0,
             "if_owner":0,"select":0,}
        # guest_doc_perm = frappe.get_doc(kvp)
        # guest_doc_perm.insert()
        # time.sleep(5)
        
        if (instance_status(instance_id) ):
            try:
                link = frappe.utils.get_url(f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={sales_invoice}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{sales_invoice}.pdf")
                # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name=LSA%2F23-24%2F000060&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
    
                url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
                params = {
                    "token": instance_id,
                    "phone": f"91{new_mobile}",
                    "message": message,
                    "link": link
                }
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
                response_data = response.json()
                if(True):

                    # print(response_data)
                    frappe.logger().info(f"Sales Invoice response: {response.text}")

                    resp["msg"]="WhatsApp message sent successfully"
                else:
                    resp["msg"]=("API Error sending WhatsApp message")
            except Exception as er:
                 resp["msg"]=str(er)
            # time.sleep(10)
            # per_name=guest_doc_perm.name
            # resp["perm"]=per_name
            # frappe.delete_doc('Custom DocPerm', per_name)
        else:
            resp["msg"]=("WhatsApp API Instance not active")
        return resp
 
 
    except requests.exceptions.RequestException as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Network error: {e}")
        frappe.msgprint(f"Error: {e}")
 
    except Exception as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Error: {e}")
        frappe.msgprint(f"Error: {e}")
 
 
 
 
def instance_status(instance_id):
    try:
        # Define the API endpoint URL with the token placeholder
        api_endpoint = 'https://wts.vision360solutions.co.in/api/qrCodeLink?token={{instance_id}}'
 
        # Replace {{instance_id}} with the actual token
        api_endpoint = api_endpoint.replace('{{instance_id}}', instance_id)
 
        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
 
        # Parse the JSON response
        json_data = response.json()
 
        # Extract data from JSON
        instance_data = json_data.get('data')  # Use .get() to safely get the 'data' key
 
        # Check if instance_data is a dictionary
        return isinstance(instance_data, dict)
 
    except requests.RequestException as e:
        frappe.log_error(f"Error in storing data: {e}")
        return False  # Return False if there's an error

    

@frappe.whitelist()
def sales_invoice_mail(si_id=None, recipient=None, subject=None, customer_name=None):
    if si_id and recipient and subject and customer_name :
        si_doc = frappe.get_doc("Sales Invoice", si_id)
        if si_doc.outstanding_amount > 1:
            return f"Sales Invoice payment is pending for balance amount of ₹ {si_doc.outstanding_amount}"
        
        gstin=""
        if si_doc.billing_address_gstin:
            gstin =f"GSTIN - {si_doc.billing_address_gstin}"

        email_account = frappe.get_doc("Email Account", "LSA Accounts")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()
                
        
        
        body=f'''<pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">Greetings from LSA Office!!! Thanks for providing us the opportunity to serve you.

Kindly find attached Invoice No. {si_doc.name} for amount {si_doc.rounded_total} in INR dated {si_doc.posting_date} for services availed from LSA Office(India)Limited.</pre>'''
        

        body += """
                <br><table class="table table-bordered" style="border-color: #444444; border-collapse: collapse; width: 80%;">
                    <thead>
                        <tr style="background-color:#3498DB;color:white;text-align: left;">
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">S. No.</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 20%;">Item</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 40%;">Description</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Quantity</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Rate(INR)</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Amount(INR)</th>
                            
                        </tr>
                    </thead>
                    <tbody>
                """
        count=1
        for item in si_doc.items:
            body += f"""
                <tr>
                    <td style="border: solid 2px #bcb9b4;">{count}</td>
                    <td style="border: solid 2px #bcb9b4;">{item.item_code}</td>
                    <td style="border: solid 2px #bcb9b4;">{item.description}</td>
                    <td style="border: solid 2px #bcb9b4;">{item.qty}</td>
                    <td style="border: solid 2px #bcb9b4;">₹ {item.rate}</td>
                    <td style="border: solid 2px #bcb9b4;">₹ {item.amount}</td>
                    
                </tr>
            """
            count+=1

        body += """
                    </tbody>
                </table><br>

        """
        body+=f'''<pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">As per our records your GST registration status is - {si_doc.gst_category} {gstin}.

In case of any discrepancy w.r.t. GST registration, please revert within 7 days on the email id mentioned below or else, details shall be presumed to be correct and will be used for return filing.
Kindly share this invoice with the concerned person.
Please feel free to contact us at accounts@lsaoffice.com if you have any queries or concerns about this invoice.

Best Regards,

Account Team
LSA Office
M.No.: 8951692788 </pre>'''

        # print(body)
        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Attach the PDF file
        pdf_link = frappe.utils.get_url(f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={si_id}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{si_id}.pdf")
                
        pdf_filename = f"SalesInvoice_{si_id}.pdf"
        attachment = get_file_from_link(pdf_link)
        if attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {pdf_filename}",
            )
            message.attach(part)

        # Connect to the SMTP server and send the email
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            try:
                # Send email
                server.sendmail(sender_email, recipient.split(','), message.as_string())
                return "Email sent successfully!"
            except Exception as e:
                print(f"Failed to send email. Error: {e}")
                return "Failed to send email."
    else:
        return "Invalid parameters passed."


    
def get_file_from_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch file from link. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching file from link: {e}")
        return None







########################################Single SInvoice template with PDF###########################################################

@frappe.whitelist(allow_guest=True)
def whatsapp_si_template(docname,from_date,to_date,new_mobile):
    #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Sales Invoice', docname)
        if invoice_doc.outstanding_amount > 1:
            return {"status":False,"msg":f"Sales Invoice payment is pending for balance amount of ₹ {invoice_doc.outstanding_amount}"}

        
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
            
            # payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
            
#             message = f'''Dear {customer_name},

# Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details

# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200

# Call us immediately in case of query.

# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
#             message=f'''Dear {customer_name},
 
# We hope you’re well.
# Please find Attached, the Invoice {invoice_doc.name} for your recent subscription of our services from {from_date} to {to_date} with total bill amount of ₹ {total}.
# We deeply value your business and your trust in our services. If you need any assistance, please feel free to reach out to us.
 
# Thank you for choosing LSA. We look forward to serving you in future as well.
 
# Best Regards,
# LSA Office 
# Account Team
# accounts@lsaoffice.com
# '''
            message=f'''Dear {customer_name},
We hope you’re well.
Please find Attached, the Invoice {invoice_doc.name}
Thank you for choosing LSA.

Best Regards,
LSA Office
Account Team
8951692788
accounts@lsaoffice.com'''
            
            ########################### Below commented link is work on Live #######################
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={invoice_doc.name}&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_doc.name}.pdf"
            
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
                                                "type": "Sales Invoice",
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



#####################################################################################################
########################## Selected SInvoice Whatsapp(BULK)  ##################
################################## (SI with PDF Button)###########################


@frappe.whitelist()
# def send_whatsapp_message(docname, customer, customer_id, from_date, to_date, total,new_mobile):
def send_whatsapp_message(new_mobile):
    new_mobile_dict = json.loads(new_mobile)
    count = 0
    success_number = []
    success_sales_invoices = []
    whatsapp_items = []
    # instance_id=whatsapp_demo.instance_id
    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        whatsapp_demo_doc = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        # connection_status = whatsapp_demo_doc.connection_status
        
        mobile_numbers =[]
        
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        for invoice_key in new_mobile_dict:
                # Fetch the sales invoice document based on the key
                invoice_doc = frappe.get_doc('Sales Invoice', invoice_key)
                
                from_date = invoice_doc.from_date
                to_date = invoice_doc.to_date
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
                    
                    mobile_numbers.append(new_mobile_dict[invoice_key])


                    
            
#                     message = f'''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
        
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
                    message=f'''Dear {customer_name},
We hope you’re well.
Please find Attached, the Invoice {invoice_doc.name}
Thank you for choosing LSA.

Best Regards,
LSA Office
Account Team
8951692788
accounts@lsaoffice.com'''
                    
                    ########################### Below commented link is work on Live #######################
                    link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={invoice_key}&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
                    # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
            
                    url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
                    params_1 = {
                        "token": ins_id,
                        "phone": f"91{new_mobile_dict[invoice_key]}",
                        "message": message,
                        "link": link
                    }
                    
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
                        
                        sales_invoice_whatsapp_log.append("details", {
                                                        "type": "Sales Invoice",
                                                        "document_id": invoice_doc.name,
                                                        "mobile_number": new_mobile_dict[invoice_key],
                                                        "customer":invoice_doc.customer,
                                                        "message_id":message_id
                                                                    
                                                        # Add other fields of the child table row as needed
                                                    })
                    else:
                        frappe.logger().error(f"Failed to send Whatsapp Message for {invoice_doc.name}")
            
            
                    frappe.logger().info(f"Sales Invoice response: {response.text}")
            
                    # Create a new WhatsApp Message Log document
                    
                    
                    count += 1 
                    success_number+=[new_mobile_dict[invoice_key]]
                    success_sales_invoices+=[invoice_key]

                
            
                except requests.exceptions.RequestException as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Network error: {e}")
                    # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
                    # print(e)
                except Exception as e:
                    # Log the exception and provide feedback to the user
                    frappe.logger().error(f"Error: {e}")
                    # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
                    # print(e)
#         message = '''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {due_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
            
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''

#         message='''Dear {customer_name},
 
# We hope you’re well.
# Please find Attached, the Invoice {invoice_doc.name} for your recent subscription of our services from {from_date} to {to_date} with total bill amount of ₹ {total}.
# We deeply value your business and your trust in our services. If you need any assistance, please feel free to reach out to us.
 
# Thank you for choosing LSA. We look forward to serving you in future as well.
 
# Best Regards,
# LSA Office 
# Account Team
# accounts@lsaoffice.com
# '''
        message='''Dear {customer_name},
We hope you’re well.
Please find Attached, the Invoice {invoice_doc.name}
Thank you for choosing LSA.

Best Regards,
LSA Office
Account Team
8951692788
accounts@lsaoffice.com'''
        
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
        
        sales_invoice_whatsapp_log.insert()
        if len(success_number)==len(new_mobile_dict):
            return {"status":True,"msg":"WhatsApp messages sent successfully"}
        else:
            msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
            return {"status":True,"msg":msg}
       
    else:
        return {"status":False,"msg":"Your WhatApp API instance is not connected"}


