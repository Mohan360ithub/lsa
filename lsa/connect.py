######################### Login Instance (connect now button) ###################################

import frappe
import requests
from frappe.model.document import Document
import json

@frappe.whitelist()
def storing_the_qrcode(name=None):
    if True:
        whatsapp_demo = frappe.get_doc("WhatsApp Instance",name)
        instance_id=whatsapp_demo.instance_id
        try:
            
            api_endpoint = 'https://wts.vision360solutions.co.in/api/qrCodeLink?token={{instance_id}}'
            api_endpoint = api_endpoint.replace('{{instance_id}}', instance_id)

            # Make a GET request to the API endpoint
            response = requests.get(api_endpoint)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)

            # Parse the JSON response
            json_data = response.json()
            
            # Extract the URL from the JSON response
            qr_code_url = json_data.get('data')
            # print(qr_code_url)

            return qr_code_url  # Return the URL
        except requests.RequestException as e:
            frappe.log_error(f"Error generating QR code link: {e}")
            return None
        


############################## Logout Instance code (Disconnect Now Button)#######################################



@frappe.whitelist()
def logout_instance(name):
    try:
        whatsapp_demo = frappe.get_doc("WhatsApp Instance",name)
        instance_id=whatsapp_demo.instance_id

        # Attempt to disconnect the instance
        url = "https://wts.vision360solutions.co.in/api/logout"
        params = {"token": instance_id}
        response = requests.post(url, params=params)
        # print(response.status_code)
        
        response.raise_for_status() # Raise an error for HTTP errors (status codes other than 2xx)
        response=response.json()
        # print(response)
        # Check if the instance is already disconnected
        #  {'status': 'success', 'message': 'Instance 609bc2d1392a635870527076 disconnected successfully'}

        if "disconnected successfully" in response["message"]:
            whatsapp_demo.connection_status = 0
            whatsapp_demo.save()
            return {"message": "Instance disconnected successfully."}
        else:
            return {"message": "Error disconnecting."}
    
    except requests.RequestException as e:
        frappe.logger().error(f"Error sending WhatsApp message: {e}")
        raise



# #####################################################################################################
# ########################## Selected SOrder Whatsapp(BULK)  ##################
# ################################## (SO with PDF Button)###########################


# @frappe.whitelist()
# # def send_whatsapp_message(docname, customer, customer_id, from_date, to_date, total,new_mobile):
# def send_so_whatsapp_message(new_mobile):
#     new_mobile_dict = json.loads(new_mobile)
#     count = 0
#     success_number = []
#     success_sales_invoices = []
#     whatsapp_items = []
#     # instance_id=whatsapp_demo.instance_id
#     whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
#     if whatsapp_demo:
#         whatsapp_demo_doc = instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
#         connection_status = whatsapp_demo_doc.connection_status
#         mobile_numbers =[]
        
#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#         for invoice_key in new_mobile_dict:
#                 # Fetch the sales invoice document based on the key
#                 invoice_doc = frappe.get_doc('Sales Order', invoice_key)
                
#                 from_date = invoice_doc.custom_so_from_date
#                 to_date = invoice_doc.custom_so_to_date
#                 customer = invoice_doc.customer
#                 total = invoice_doc.rounded_total
#                 customer_name = invoice_doc.customer_name
#                 docname = invoice_doc.name
                
#                 ins_id = whatsapp_demo_doc.instance_id


#                 try:
#                     # Check if the mobile number has 10 digits
#                     if len(new_mobile_dict[invoice_key]) != 10:
#                         frappe.msgprint("Please provide a valid 10-digit mobile number.")
#                         return
#                     payment_link=""
#                     if (invoice_doc.custom_razorpay_payment_url):
#                         payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
                    
#                     mobile_numbers.append(new_mobile_dict[invoice_key])


                    
            
#                     message = f'''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
        
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
# {payment_link}
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
                    
#                     ########################### Below commented link is work on Live #######################
#                     link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
#                     link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
            
#                     # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
            
#                     url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#                     params_1 = {
#                         "token": ins_id,
#                         "phone": f"91{new_mobile_dict[invoice_key]}",
#                         "message": message,
#                         "link": link
#                     }
#                     # print(new_mobile_dict[invoice_key])
#                     # whatsapp_items.append( {"type": "Sales Invoice",
#                     #                         "document_id": invoice_doc.name,
#                     #                         "mobile_number": new_mobile_dict[invoice_key],
#                     #                         "customer":invoice_doc.customer,})
                    
#                     response = requests.post(url, params=params_1)
#                     response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
#                     response_data = response.json()

#                     message_id = response_data['data']['messageIDs'][0]

#                     # Check if the response status is 'success'
#                     if response_data.get('status') == 'success':
#                         # Log the success

#                         frappe.logger().info("WhatsApp message sent successfully")
#                         # print("send succesfully")
#                         sales_invoice_whatsapp_log.append("details", {
#                                                         "type": "Sales Order",
#                                                         "document_id": invoice_doc.name,
#                                                         "mobile_number": new_mobile_dict[invoice_key],
#                                                         "customer":invoice_doc.customer,
#                                                         "message_id":message_id
                                                                    
#                                                         # Add other fields of the child table row as needed
#                                                     })
#                     else:
#                         frappe.logger().error(f"Failed to send Whatsapp Message for {invoice_doc.name}")
            
            
#                     frappe.logger().info(f"Sales Order response: {response.text}")
            
#                     # Create a new WhatsApp Message Log document
                    
                    
#                     count += 1 
#                     success_number+=[new_mobile_dict[invoice_key]]
#                     success_sales_invoices+=[invoice_key]

                
            
#                 except requests.exceptions.RequestException as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Network error: {e}")
#                     # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
#                 except Exception as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Error: {e}")
#                     # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
#         message = '''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {due_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
            
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
# {payment_link}
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
        
#         # sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
#         # sales_invoice_whatsapp_log.customer = invoice_doc.customer
#         # sales_invoice_whatsapp_log.posting_date = from_date
#         sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#         # sales_invoice_whatsapp_log.total_amount = total
#         # sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
#         sales_invoice_whatsapp_log.sender = frappe.session.user
#         # sales_invoice_whatsapp_log.sales_invoice =  docname
#         sales_invoice_whatsapp_log.type = "Template"
#         sales_invoice_whatsapp_log.message = message
#         # sales_invoice_whatsapp_log.file = link
#         # sales_invoice_whatsapp_log.details = whatsapp_items
#         # print( "Sales Invoice",invoice_salesinvoice,mobile_number,invoice_doc.customer)
#         # print(whatsapp_items)
#         sales_invoice_whatsapp_log.insert()
#         if len(success_number)==len(new_mobile_dict):
#             return {"status":True,"msg":"WhatsApp messages sent successfully"}
#         else:
#             msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
#             return {"status":True,"msg":msg}
       
#     else:
#         return {"status":False,"msg":"Your WhatApp API instance is not connected"}


# ########################################Single SOrder template with PDF###########################################################

# @frappe.whitelist(allow_guest=True)
# def whatsapp_so_template(docname,from_date,to_date,new_mobile):
#     #new_mobile="9098543046"

#     whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
#     if whatsapp_demo:
#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#         whatsapp_items = []

#         invoice_doc = frappe.get_doc('Sales Order', docname)
#         customer = invoice_doc.customer
#         total = invoice_doc.rounded_total
#         customer_name = invoice_doc.customer_name
#         docname = invoice_doc.name

#         instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
#         ins_id = instance.instance_id


#         try:
#             # Check if the mobile number has 10 digits
#             if len(new_mobile) != 10:
#                 frappe.msgprint("Please provide a valid 10-digit mobile number.")
#                 return
#             payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
            
#             message = f'''Dear {customer_name},

# Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details

# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
# {payment_link}

# Call us immediately in case of query.

# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
            
#             ########################### Below commented link is work on Live #######################
#             link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
#             link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20with%20payment%20details&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
#             # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"

#             url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#             params_1 = {
#                 "token": ins_id,
#                 "phone": f"91{new_mobile}",
#                 "message": message,
#                 "link": link
#             }

#             whatsapp_items.append( {"type": "Sales Order",
#                                     "document_id": invoice_doc.name,
#                                     "mobile_number": new_mobile,
#                                     "customer":invoice_doc.customer,})
            
#             response = requests.post(url, params=params_1)
#             response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
#             response_data = response.json()
#             message_id = response_data['data']['messageIDs'][0]


#             # Check if the response status is 'success'
#             if response_data.get('status') == 'success':
#                 # Log the success

#                 frappe.logger().info("WhatsApp message sent successfully")
#                 sales_invoice_whatsapp_log.append("details", {
#                                                 "type": "Sales Order",
#                                                 "document_id": invoice_doc.name,
#                                                 "mobile_number": new_mobile,
#                                                 "customer":invoice_doc.customer,
#                                                 "message_id":message_id
                                                            
#                                                 # Add other fields of the child table row as needed
#                                             })
#                 sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#                 sales_invoice_whatsapp_log.sender = frappe.session.user
#                 sales_invoice_whatsapp_log.type = "Template"
#                 sales_invoice_whatsapp_log.message = message
#                 sales_invoice_whatsapp_log.insert()
#                 return {"status":True,"msg":"WhatsApp message sent successfully"}
#             else:
#                 return {"status":False,"error":f"{response.json()}","msg":"An error occurred while sending the WhatsApp message."}


#         except requests.exceptions.RequestException as e:
#             # Log the exception and provide feedback to the user
#             frappe.logger().error(f"Network error: {e}")
#             return {"status":False,"error":e,"msg":"An error occurred while sending the WhatsApp message. Please try again later."}
#         except Exception as er:
#             # Log the exception and provide feedback to the user
#             frappe.logger().error(f"Error: {er}")
#             return {"status":False,"error":er,"msg":"An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator."}
#     else:
#         return {"status":False,"msg":"Your WhatApp API instance is not connected"}



# ########################################Single SInvoice template with PDF###########################################################

# @frappe.whitelist(allow_guest=True)
# def whatsapp_si_template(docname,from_date,to_date,new_mobile):
#     #new_mobile="9098543046"

#     whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
#     if whatsapp_demo:
#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#         whatsapp_items = []

#         invoice_doc = frappe.get_doc('Sales Invoice', docname)
#         customer = invoice_doc.customer
#         total = invoice_doc.rounded_total
#         customer_name = invoice_doc.customer_name
#         docname = invoice_doc.name

#         instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
#         ins_id = instance.instance_id


#         try:
#             # Check if the mobile number has 10 digits
#             if len(new_mobile) != 10:
#                 frappe.msgprint("Please provide a valid 10-digit mobile number.")
#                 return
            
#             # payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
            
# #             message = f'''Dear {customer_name},

# # Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details

# # Our Bank Account
# # Lokesh Sankhala and ASSOSCIATES
# # Account No = 73830200000526
# # IFSC = BARB0VJJCRO
# # Bank = Bank of Baroda,JC Road,Bangalore-560002
# # UPI id = LSABOB@UPI
# # Gpay / Phonepe no = 9513199200

# # Call us immediately in case of query.

# # Best Regards,
# # LSA Office Account Team
# # accounts@lsaoffice.com'''
# #             message=f'''Dear {customer_name},
 
# # We hope you’re well.
# # Please find Attached, the Invoice {invoice_doc.name} for your recent subscription of our services from {from_date} to {to_date} with total bill amount of ₹ {total}.
# # We deeply value your business and your trust in our services. If you need any assistance, please feel free to reach out to us.
 
# # Thank you for choosing LSA. We look forward to serving you in future as well.
 
# # Best Regards,
# # LSA Office 
# # Account Team
# # accounts@lsaoffice.com
# # '''
#             message=f'''Dear {customer_name},
# We hope you’re well.
# Please find Attached, the Invoice {invoice_doc.name}
# Thank you for choosing LSA.

# Best Regards,
# LSA Office
# Account Team
# 8951692788
# accounts@lsaoffice.com'''
            
#             ########################### Below commented link is work on Live #######################
#             link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={invoice_doc.name}&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_doc.name}.pdf"
            
#             url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#             params_1 = {
#                 "token": ins_id,
#                 "phone": f"91{new_mobile}",
#                 "message": message,
#                 "link": link
#             }

#             whatsapp_items.append( {"type": "Sales Order",
#                                     "document_id": invoice_doc.name,
#                                     "mobile_number": new_mobile,
#                                     "customer":invoice_doc.customer,})
            
#             response = requests.post(url, params=params_1)
#             response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
#             response_data = response.json()
#             message_id = response_data['data']['messageIDs'][0]


#             # Check if the response status is 'success'
#             if response_data.get('status') == 'success':
#                 # Log the success

#                 frappe.logger().info("WhatsApp message sent successfully")
#                 sales_invoice_whatsapp_log.append("details", {
#                                                 "type": "Sales Invoice",
#                                                 "document_id": invoice_doc.name,
#                                                 "mobile_number": new_mobile,
#                                                 "customer":invoice_doc.customer,
#                                                 "message_id":message_id
                                                            
#                                                 # Add other fields of the child table row as needed
#                                             })
#                 sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#                 sales_invoice_whatsapp_log.sender = frappe.session.user
#                 sales_invoice_whatsapp_log.type = "Template"
#                 sales_invoice_whatsapp_log.message = message
#                 sales_invoice_whatsapp_log.insert()
#                 return {"status":True,"msg":"WhatsApp message sent successfully"}
#             else:
#                 return {"status":False,"error":f"{response.json()}","msg":"An error occurred while sending the WhatsApp message."}


#         except requests.exceptions.RequestException as e:
#             # Log the exception and provide feedback to the user
#             frappe.logger().error(f"Network error: {e}")
#             return {"status":False,"error":e,"msg":"An error occurred while sending the WhatsApp message. Please try again later."}
#         except Exception as er:
#             # Log the exception and provide feedback to the user
#             frappe.logger().error(f"Error: {er}")
#             return {"status":False,"error":er,"msg":"An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator."}
#     else:
#         return {"status":False,"msg":"Your WhatApp API instance is not connected"}



# #####################################################################################################
# ########################## Selected SInvoice Whatsapp(BULK)  ##################
# ################################## (SI with PDF Button)###########################
# import frappe
# from frappe.model.document import Document
# import requests
# import json

# @frappe.whitelist()
# # def send_whatsapp_message(docname, customer, customer_id, from_date, to_date, total,new_mobile):
# def send_whatsapp_message(new_mobile):
#     new_mobile_dict = json.loads(new_mobile)
#     count = 0
#     success_number = []
#     success_sales_invoices = []
#     whatsapp_items = []
#     # instance_id=whatsapp_demo.instance_id
#     whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
#     if whatsapp_demo:
#         whatsapp_demo_doc = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
#         # connection_status = whatsapp_demo_doc.connection_status
        
#         mobile_numbers =[]
        
#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#         for invoice_key in new_mobile_dict:
#                 # Fetch the sales invoice document based on the key
#                 invoice_doc = frappe.get_doc('Sales Invoice', invoice_key)
                
#                 from_date = invoice_doc.from_date
#                 to_date = invoice_doc.to_date
#                 customer = invoice_doc.customer
#                 total = invoice_doc.rounded_total
#                 customer_name = invoice_doc.customer_name
#                 docname = invoice_doc.name
                
#                 ins_id = whatsapp_demo_doc.instance_id


#                 try:
#                     # Check if the mobile number has 10 digits
#                     if len(new_mobile_dict[invoice_key]) != 10:
#                         frappe.msgprint("Please provide a valid 10-digit mobile number.")
#                         return
                    
#                     mobile_numbers.append(new_mobile_dict[invoice_key])


                    
            
# #                     message = f'''Dear {customer_name},
            
# # Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
        
# # Our Bank Account
# # Lokesh Sankhala and ASSOSCIATES
# # Account No = 73830200000526
# # IFSC = BARB0VJJCRO
# # Bank = Bank of Baroda,JC Road,Bangalore-560002
# # UPI id = LSABOB@UPI
# # Gpay / Phonepe no = 9513199200
        
# # Call us immediately in case of query.
        
# # Best Regards,
# # LSA Office Account Team
# # accounts@lsaoffice.com'''
#                     message=f'''Dear {customer_name},
# We hope you’re well.
# Please find Attached, the Invoice {invoice_doc.name}
# Thank you for choosing LSA.

# Best Regards,
# LSA Office
# Account Team
# 8951692788
# accounts@lsaoffice.com'''
                    
#                     ########################### Below commented link is work on Live #######################
#                     link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={invoice_key}&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
#                     # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
            
#                     url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#                     params_1 = {
#                         "token": ins_id,
#                         "phone": f"91{new_mobile_dict[invoice_key]}",
#                         "message": message,
#                         "link": link
#                     }
                    
#                     # whatsapp_items.append( {"type": "Sales Invoice",
#                     #                         "document_id": invoice_doc.name,
#                     #                         "mobile_number": new_mobile_dict[invoice_key],
#                     #                         "customer":invoice_doc.customer,})
                    
#                     response = requests.post(url, params=params_1)
#                     response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
#                     response_data = response.json()
                    
#                     message_id = response_data['data']['messageIDs'][0]
                    

#                     # Check if the response status is 'success'
#                     if response_data.get('status') == 'success':
#                         # Log the success

#                         frappe.logger().info("WhatsApp message sent successfully")
                        
#                         sales_invoice_whatsapp_log.append("details", {
#                                                         "type": "Sales Invoice",
#                                                         "document_id": invoice_doc.name,
#                                                         "mobile_number": new_mobile_dict[invoice_key],
#                                                         "customer":invoice_doc.customer,
#                                                         "message_id":message_id
                                                                    
#                                                         # Add other fields of the child table row as needed
#                                                     })
#                     else:
#                         frappe.logger().error(f"Failed to send Whatsapp Message for {invoice_doc.name}")
            
            
#                     frappe.logger().info(f"Sales Invoice response: {response.text}")
            
#                     # Create a new WhatsApp Message Log document
                    
                    
#                     count += 1 
#                     success_number+=[new_mobile_dict[invoice_key]]
#                     success_sales_invoices+=[invoice_key]

                
            
#                 except requests.exceptions.RequestException as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Network error: {e}")
#                     # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
#                     # print(e)
#                 except Exception as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Error: {e}")
#                     # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
#                     # print(e)
# #         message = '''Dear {customer_name},
            
# # Your Sale Invoice for {from_date} to {due_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
            
# # Our Bank Account
# # Lokesh Sankhala and ASSOSCIATES
# # Account No = 73830200000526
# # IFSC = BARB0VJJCRO
# # Bank = Bank of Baroda,JC Road,Bangalore-560002
# # UPI id = LSABOB@UPI
# # Gpay / Phonepe no = 9513199200
        
# # Call us immediately in case of query.
        
# # Best Regards,
# # LSA Office Account Team
# # accounts@lsaoffice.com'''

# #         message='''Dear {customer_name},
 
# # We hope you’re well.
# # Please find Attached, the Invoice {invoice_doc.name} for your recent subscription of our services from {from_date} to {to_date} with total bill amount of ₹ {total}.
# # We deeply value your business and your trust in our services. If you need any assistance, please feel free to reach out to us.
 
# # Thank you for choosing LSA. We look forward to serving you in future as well.
 
# # Best Regards,
# # LSA Office 
# # Account Team
# # accounts@lsaoffice.com
# # '''
#         message='''Dear {customer_name},
# We hope you’re well.
# Please find Attached, the Invoice {invoice_doc.name}
# Thank you for choosing LSA.

# Best Regards,
# LSA Office
# Account Team
# 8951692788
# accounts@lsaoffice.com'''
        
#         # sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
#         # sales_invoice_whatsapp_log.customer = invoice_doc.customer
#         # sales_invoice_whatsapp_log.posting_date = from_date
#         sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#         # sales_invoice_whatsapp_log.total_amount = total
#         # sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
#         sales_invoice_whatsapp_log.sender = frappe.session.user
#         # sales_invoice_whatsapp_log.sales_invoice =  docname
#         sales_invoice_whatsapp_log.type = "Template"
#         sales_invoice_whatsapp_log.message = message
#         # sales_invoice_whatsapp_log.file = link
#         # sales_invoice_whatsapp_log.details = whatsapp_items
        
#         sales_invoice_whatsapp_log.insert()
#         if len(success_number)==len(new_mobile_dict):
#             return {"status":True,"msg":"WhatsApp messages sent successfully"}
#         else:
#             msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
#             return {"status":True,"msg":msg}
       
#     else:
#         return {"status":False,"msg":"Your WhatApp API instance is not connected"}



