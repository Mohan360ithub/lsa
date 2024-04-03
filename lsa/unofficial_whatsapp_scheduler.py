import frappe
from frappe.model.document import Document
import requests
from datetime import datetime
 
 
 
 
 
@frappe.whitelist()
def send_scheduled_whatsapp_message():
    try:
        # Check if the mobile number has 10 digits
        
        
        instance_id="609bc2d1392a635870527076"
 
        message = f'''Dear {"Vatsal"},
 
Your Sale Order for { datetime.now().date()} reminder on {datetime.now().time()} period is due for amount of Rs {0000.00}/- Kindly pay on below bank amount details
 
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
        
        if (instance_status(instance_id) ):
            # link = frappe.utils.get_url(f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf")
            link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
 
            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params = {
                "token": instance_id,
                "phone": f"919098543046",
                "message": message,
                "link": link
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            if(True):
                # # Check if the response status is 'success'
                # if response_data.get('status') == 'success':
                #     # Log the success
                #     frappe.logger().info("WhatsApp message sent successfully")
 
                # print(response_data)
                frappe.logger().info(f"Sales Invoice response: {response.text}")
 
                # Create a new WhatsApp Message Log document
                sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
                sales_invoice_whatsapp_log.sales_invoice = "SAL-ORD-2023-00628"
                sales_invoice_whatsapp_log.customer = "20130001"
                # sales_invoice_whatsapp_log.posting_date = "02-03-2024 15:54:31"
                sales_invoice_whatsapp_log.send_date = frappe.utils.nowdate()
                sales_invoice_whatsapp_log.total_amount = 0000.00
                sales_invoice_whatsapp_log.mobile_no = "9098543046"
                sales_invoice_whatsapp_log.sender = "scheduler"
                sales_invoice_whatsapp_log.message = message
                sales_invoice_whatsapp_log.insert(ignore_permissions=True)
                # frappe.msgprint("WhatsApp message sent successfully")
                print("Success")
        else:
            print("Failed 1")
            return "WhatsApp API Instance not active"
 
 
    except requests.exceptions.RequestException as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Network error: {e}")
        print("Failed 2")
        return f"Error: {e}"
 
    except Exception as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Error: {e}")
        print("Failed 3")
        return f"Error: {e}"
 
 
 
 
def instance_status(instance_id):
    try:
        # print(instance_id)
        # Define the API endpoint URL with the token placeholder
        api_endpoint = 'https://wts.vision360solutions.co.in/api/qrCodeLink?token={{instance_id}}'
 
        # Replace {{instance_id}} with the actual token
        api_endpoint = api_endpoint.replace('{{instance_id}}', instance_id)
 
        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
        # Parse the JSON response
        json_data = response.json()
        # print(json_data)
 
        # Extract data from JSON
        instance_data = json_data['data']
 
 
        # Convert the datetime string to the correct format
        if (type(instance_data) == dict):
            return True
        else:
            return False
 
    except requests.RequestException as e:
        frappe.log_error(f"Error in a storing data: {e}")
        return {"message": "Failed to store  data."}

