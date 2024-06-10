import frappe
import requests
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

		

########################################Single Quotation template with PDF###########################################################

@frappe.whitelist(allow_guest=True)
def whatsapp_so_template(docname,transaction_date,valid_till,new_mobile):
    #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Quotation', docname)
        
        total = invoice_doc.rounded_total
        customer_name = invoice_doc.customer_name
        

        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id

        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return
            


            
            
            message = f'''Hello {customer_name},

I hope you're doing well. 
I've just sent you the new quotation via WhatsApp and as well as email, with net total of ₹ {total}/-,dated {transaction_date} valid till {valid_till}. 

Please check the attachment and let me know if you have any questions.
Thank you!

Best Regards,
LSA Account Team
accounts@lsaoffice.com
8951692788'''
            
            
            ########################### Below commented link is work on Live #######################
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Quotation&name={docname}&format=Quotation%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }
            customer=None
            if invoice_doc.quotation_to=="Customer":
                customer=invoice_doc.party_name
            whatsapp_items.append( {"type": "Sales Order",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile,
                                    "customer":customer,})
            
            response = requests.post(url, params=params_1)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            message_id = response_data['data']['messageIDs'][0]


            # Check if the response status is 'success'
            if response_data.get('status') == 'success':
                # Log the success

                frappe.logger().info("WhatsApp message sent successfully")
                sales_invoice_whatsapp_log.append("details", {
                                                "type": "Quotation",
                                                "document_id": invoice_doc.name,
                                                "mobile_number": new_mobile,
                                                "customer":customer,
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
  
 



@frappe.whitelist()
def quotation_mail(qo_id=None, recipient=None, subject=None, customer_name=None):
    if qo_id and recipient and subject and customer_name :
        qo_doc = frappe.get_doc('Quotation', qo_id)

        email_account = frappe.get_doc("Email Account", "LSA Accounts")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()
        
        balance_amount=qo_doc.rounded_total
        
                
        
        
        body=f'''<pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">Dear {customer_name},
 
I hope this email finds you well.
Please find attached the quotation for the requested services.</pre>'''
 
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
        for item in qo_doc.items:
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
                </table>
        """

        body+=f'''<br><pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">The Quotation includes a detailed breakdown of the scope of services and associated costs.
If you have any questions or need further clarification, feel free to reach out.

Thank you for considering our services. We look forward to working with you.

Best regards,

Latha ST
Sales Team
Lokesh Sankhala and Associates
+918951692788</pre>'''

        # print(body)
        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Attach the PDF file
        pdf_link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Quotation&name={qo_id}&format=Quotation%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{qo_id}.pdf"
            
        
        pdf_filename = f"Quotation_{qo_id}.pdf"
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


