########################################(Sales Invoice Custom Message Button)###########################################

import frappe
import json
import requests

@frappe.whitelist()
def send_whatsapp_message(values_prompt):
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
        whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
        if whatsapp_demo:
            whatsapp_demo_doc = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
            connection_status = whatsapp_demo_doc.connection_status
            sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
            for invoice_key in new_mobile_dict:
                # Fetch the sales invoice document based on the key
                invoice_doc = frappe.get_doc('Sales Invoice', invoice_key)               
                # Now you can access details from the invoice document
                from_date = invoice_doc.posting_date
                total = invoice_doc.total
                
                ins_id = whatsapp_demo_doc.instance_id

                try:
                    # Check if the mobile number has 10 digits
                    if len(new_mobile_dict[invoice_key]) != 10:
                        frappe.msgprint("Please provide a valid 10-digit mobile number.")
                                                   
                    url = "https://wts.vision360solutions.co.in/api/sendText"
                    params_1 = {
                        "token": ins_id,
                        "phone": f"91{new_mobile_dict[invoice_key]}",
                        "message": message,
                    }

                    response = requests.post(url, params=params_1)
                    response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
                    response_data = response.json()
                    message_id = response_data['data']['messageIDs'][0]

                    # Check if the response status is 'success'
                    if response_data.get('status') == 'success':
                        sales_invoice_whatsapp_log.append("details", {
                                    "type": "Sales Invoice",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile_dict[invoice_key],
                                    "customer":invoice_doc.customer,
                                    "message_id":message_id                                                
                                    # Add other fields of the child table row as needed
                                })


                    else:
                        return {"status":False,"msg":"Your WhatApp API instance is not connected"}       
            
                    frappe.logger().info(f"Sales Invoice response: {response.text}")
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
            sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
            sales_invoice_whatsapp_log.customer = invoice_doc.customer
            sales_invoice_whatsapp_log.posting_date = from_date
            sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
            # sales_invoice_whatsapp_log.total_amount = total
            sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
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



#######################################(Sales Order Custom Message Button)###########################################


@frappe.whitelist()
def send_so_whatsapp_message(values_prompt):
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

                try:
                    # Check if the mobile number has 10 digits
                    if len(new_mobile_dict[invoice_key]) != 10:
                        frappe.msgprint("Please provide a valid 10-digit mobile number.")
                                                   
                    url = "https://wts.vision360solutions.co.in/api/sendText"
                    params_1 = {
                        "token": ins_id,
                        "phone": f"91{new_mobile_dict[invoice_key]}",
                        "message": message,
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

