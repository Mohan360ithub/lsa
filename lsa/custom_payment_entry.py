
import frappe
import requests,random,json
from frappe import _
from frappe.utils import today
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


########################################Single PE template with PDF###########################################################

@frappe.whitelist(allow_guest=True)
def whatsapp_pe_template(docname,ref_date,customer,new_mobile=None):
    
    if not new_mobile:
        customer_doc = frappe.get_doc('Customer', customer)
        new_mobile = customer_doc.custom_primary_mobile_no
        #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Payment Entry', docname)

        wa_status=False
        for item in invoice_doc.references:
            if item.reference_doctype in ["Sales Invoice","Sales Order"]:
                wa_status=True
                break
        if not wa_status:
            frappe.msgprint("Can only send WhatsApp for the Payment done against Sales Invoice or Sales Order")
            return

        customer = invoice_doc.party
        paid_amount = invoice_doc.paid_amount
        customer_name = invoice_doc.party_name
        docname = invoice_doc.name


        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id


        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return

            message = f'''Dear {customer_name},

Your Payment Receipt for transaction done on {ref_date} for the amount of {paid_amount} is attached. 
Call us in case of query

Thank you for choosing LSA

Best Regards,
LSA Office Account Team
accounts@lsaoffice.com
8951692788'''
            
            
            ########################### Below commented link is work on Live #######################
            link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Payment%20Entry&name={docname}&format=Payment%20receipt%20format%20for%20Payment%20Entry&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            
            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }

            whatsapp_items.append( {"type": "Payment Entry",
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
                                                "type": "Payment Entry",
                                                "document_id": docname,
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
def pe_mail(pe_id, customer, customer_name=None, recipient=None, subject=None):
    

    if not recipient:
        customer_doc = frappe.get_doc('Customer', customer)
        recipient = customer_doc.custom_primary_email
        #recipient="vatsal.k@360ithub.com"
        customer_name = customer_doc.customer_name

    if not subject:
        subject = f"Payment Notification {pe_id}"

    if pe_id and recipient and customer and customer_name:

        pe_doc = frappe.get_doc('Payment Entry', pe_id)

        wa_status=False
        for item in pe_doc.references:
            if item.reference_doctype in ["Sales Invoice","Sales Order"]:
                wa_status=True
                break
        if not wa_status:
            frappe.msgprint("Can only send Mail for the Payment done against Sales Invoice or Sales Order")
            return


        email_account = frappe.get_doc("Email Account", "LSA Accounts")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()
                
        
        
        body=f'''<pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">Dear {customer_name},

Kindly find attached Payment Receipt {pe_doc.name} for amount {pe_doc.paid_amount} in INR dated {pe_doc.reference_date} for services availed from LSA Office(India)Limited.</pre>'''
        

        body += """
                <br><table class="table table-bordered" style="border-color: #444444; border-collapse: collapse; width: 80%;">
                    <thead>
                        <tr style="background-color:#3498DB;color:white;text-align: left;">
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 5%;">S. No.</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 40%;">Invoice</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">From Date</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">To Date</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Net Amount(INR)</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Paid Amount(INR)</th>
                            
                        </tr>
                    </thead>
                    <tbody>
                """
        count=1
        for item in pe_doc.references:
            from_date=None
            to_date=None
            if item.reference_doctype=="Sales Order":
                so_doc = frappe.get_doc("Sales Order", item.reference_name)
                from_date=so_doc.custom_so_from_date
                to_date=so_doc.custom_so_to_date
            elif item.reference_doctype=="Sales Invoice":
                si_doc = frappe.get_doc("Sales Invoice", item.reference_name)
                from_date=si_doc.from_dates
                to_date=si_doc.to_dates

            body += f"""
                <tr>
                    <td style="border: solid 2px #bcb9b4;">{count}</td>
                    <td style="border: solid 2px #bcb9b4;">{item.reference_name}</td>
                    <td style="border: solid 2px #bcb9b4;">{from_date}</td>
                    <td style="border: solid 2px #bcb9b4;">{to_date}</td>
                    <td style="border: solid 2px #bcb9b4;">₹ {item.total_amount}</td>
                    <td style="border: solid 2px #bcb9b4;">₹ {item.allocated_amount}</td>
                    
                </tr>
            """
            count+=1

        body += """
                    </tbody>
                </table><br>

        """
        body+=f'''<pre style="font-family: Arial, sans-serif; font-size: 14px; color: #000000;">Please feel free to contact us at accounts@lsaoffice.com if you have any queries or concerns about this invoice.

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
        pdf_link = frappe.utils.get_url(f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Payment%20Entry&name={pe_id}&format=Payment%20receipt%20format%20for%20Payment%20Entry&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{pe_id}.pdf")
            
        pdf_filename = f"PaymentReceipt_{pe_id}.pdf"
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
                return {"status":True,"msg":"Email sent successfully!"}
            except Exception as e:
                print(f"Failed to send email. Error: {e}")
                frappe.log_error(f'Failed make Email notifcation for Razorpay payment done for {customer} {e}' )

                return {"status":False,"msg":"Failed to send email."}
    else:
        return {"status":False,"msg":"Invalid parameters passed.","parameters":[pe_id, customer, customer_name, recipient, subject]}


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



@frappe.whitelist()
def update_payment_entry_linked_doc(doc, method):

    if doc.party_type=="Customer" and doc.party:
        references=doc.references
        references_dict={}
        for item in references:
            if item.reference_doctype in ["Sales Order","Sales Invoice"]:
                references_dict[item.reference_name]=[item.reference_doctype,item.allocated_amount]
        try:
            customer_doc = frappe.get_doc(doc.party_type, doc.party)
            if customer_doc.custom_customer_status_=="HOLD":
                # print("Customer is Hold")
                so_list = frappe.get_all("Sales Order", 
                                         filters={"customer":doc.party},
                                         fields=["name","rounded_total","advance_paid"])
                hold=False
                for so in so_list:
                    # print("Has SO",so.rounded_total,so.advance_paid)
                    # print(references_dict)
                    # print(not so.advance_paid)
                    if not so.advance_paid or (so.rounded_total-so.advance_paid) >= 1:
                        if so.name in references_dict:
                            print("Current PE and has Adv")
                            if (so.rounded_total-so.advance_paid-references_dict[so.name][1]) <=1:
                                continue
                            

                        sii_dict = frappe.get_all("Sales Invoice Item", 
                                                    filters={"sales_order": so.name,
                                                             "docstatus":("not in",[2])},
                                                    fields=["parent"])
                        # print("Has pending SO")
                        if sii_dict :
                            # print("Has SI")
                            sii_list=list(set([sii.parent for sii in sii_dict]))
                            si_dict = frappe.get_all("Sales Invoice", 
                                                        filters={"name":("in",sii_list),
                                                                "docstatus":("not in",[2]),
                                                                "outstanding_amount":(">=",1)})
                            if si_dict:
                                # print("Has pending SI")
                                hold=True
                                break
                            else:
                                continue
                        
                        hold=True
                        break
                    elif so.name in references_dict:
                        # print("Current PE no adv")
                        if (so.rounded_total-references_dict[so.name][1]) <=1:
                            continue
                        hold=True
                        break

                if not hold:
                    customer_doc.custom_customer_status_="ACTIVE"
                    customer_doc.save()
        except Exception as e:
            # print(e)
            frappe.logger().error(f"Error Triggering status change for Payment Entry {doc.name}: {e}")



@frappe.whitelist()
def get_unreconciled_bnk_transactions():
    try:
        current_date = datetime.now()
        first_day_of_current_month = datetime(current_date.year, current_date.month, 1)

        # last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

                # Get the employee document
        bnk_tran_list = frappe.get_all('Bank Transaction', 
                                      filters={"unallocated_amount":(">",0.00),
                                               "docstatus":1,
                                            #    "date":("<",first_day_of_current_month),
                                               },
                                      fields=["date","bank_account","deposit","withdrawal"]
                                      )
        bnk_tran_map={}
        for bnk_tran in bnk_tran_list:
            if bnk_tran.bank_account not in bnk_tran_map:
                bnk_tran_map[bnk_tran.bank_account]={"count":1,
                                                     "deposit":bnk_tran.deposit,
                                                     "withdrawal":bnk_tran.withdrawal,
                                                     "count_this_month":0,
                                                     "deposit_this_month":0,
                                                     "withdrawal_this_month":0}
            else:
                bnk_tran_map[bnk_tran.bank_account]["count"]+=1
                bnk_tran_map[bnk_tran.bank_account]["deposit"]+=bnk_tran.deposit
                bnk_tran_map[bnk_tran.bank_account]["withdrawal"]+=bnk_tran.withdrawal


        bnk_tran_list_current_month = frappe.get_all('Bank Transaction', 
                                filters={"unallocated_amount":(">",0.00),
                                        "docstatus":1,
                                        "date":(">=",first_day_of_current_month)},
                                fields=["date","bank_account","deposit","withdrawal"]
                                )
        for bnk_tran_this_month in bnk_tran_list_current_month:
            if bnk_tran_this_month.bank_account not in bnk_tran_map:
                bnk_tran_map[bnk_tran_this_month.bank_account]={"count":0,
                                                                "deposit":0,
                                                                "withdrawal":0,
                                                                "count_this_month":1,
                                                                "deposit_this_month":bnk_tran_this_month.deposit,
                                                                "withdrawal_this_month":bnk_tran_this_month.withdrawal}
            else:
                bnk_tran_map[bnk_tran_this_month.bank_account]["count_this_month"]+=1
                bnk_tran_map[bnk_tran_this_month.bank_account]["deposit_this_month"]+=bnk_tran_this_month.deposit
                bnk_tran_map[bnk_tran_this_month.bank_account]["withdrawal_this_month"]+=bnk_tran_this_month.withdrawal

        return {
            "status": True,
            "bnk_tran_map": bnk_tran_map
        }

    except Exception as e:
        # Log the error
        frappe.log_error(message=str(e), title="Failed to get bank transactions details")
        
        return {
            "status": False,
            "msg": f"Failed to get bank transactions details: {str(e)}"
        }
