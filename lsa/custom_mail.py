import frappe
import requests
from frappe import _
# from frappe.utils import today
# from datetime import datetime,timedelta,time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


@frappe.whitelist()
def single_mail(email_account,recipients,subject,html_message,cc_email=None):
    # recipients = ["vatsal.k@360ithub.com"]
    email_account = frappe.get_doc("Email Account", email_account)
    sender_email = email_account.email_id
    sender_password = email_account.get_password()

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ",".join(recipients)
    if cc_email:  # Add CC if provided
        #cc_email.append("vatsal.k@360ithub.com")
        message['Cc'] = ",".join(cc_email)
        # print(",".join(cc_email))
    message['Subject'] = subject
    message.attach(MIMEText(html_message, 'html'))


    # Connect to the SMTP server and send the email
    smtp_server = 'smtp-mail.outlook.com'
    # smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        try:
            # Send email
            recipients_all = recipients + (cc_email if cc_email else [])
            resp=server.sendmail(sender_email, recipients_all , message.as_string())
            # print("Mail sent successfully!")
            # print(",".join(recipients))
            # print(resp)
            # print(sender_email,sender_password)
            return {"status":True,"msg": "Mail sent successfully!"}
        except Exception as er:
            # print(f"Failed to send email. Error: {er}")
            return {"status":False,"msg": f"Failed to send notification:{er}"}






# @frappe.whitelist()
# def single_mail_with_attachment(email_account, recipients, subject, html_message, cc_email=None, attachments=None):
#     email_account = frappe.get_doc("Email Account", email_account)
#     sender_email = email_account.email_id
#     sender_password = email_account.get_password()

#     # Create the email message
#     message = MIMEMultipart()
#     message['From'] = sender_email
#     message['To'] = ",".join(recipients)

#     if cc_email:  # Add CC if provided
#         message['Cc'] = ",".join(cc_email)

#     message['Subject'] = subject

#     # Attach the HTML message body
#     message.attach(MIMEText(html_message, 'html'))

#     # Handle file attachments
#     if attachments:
#         for attachment in attachments:
#             part = MIMEBase('application', 'octet-stream')
#             part.set_payload(attachment['fcontent'])  # Use binary content
#             encoders.encode_base64(part)
#             part.add_header(
#                 'Content-Disposition',
#                 f'attachment; filename="{attachment["fname"]}"',
#             )
#             message.attach(part)

#     # Connect to the SMTP server and send the email
#     smtp_server = 'smtp-mail.outlook.com'
#     smtp_port = 587
#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
            
#             # Combine recipients and CC emails
#             recipients_all = recipients + (cc_email if cc_email else [])
            
#             # Send the email
#             server.sendmail(sender_email, recipients_all, message.as_string())
            
#             return {"status": True, "msg": "Mail sent successfully!"}
#     except Exception as er:
#         return {"status": False, "msg": f"Failed to send notification: {er}"}
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication  # Import MIMEApplication for attachments
from email import encoders

@frappe.whitelist()
def single_mail_with_attachment(email_account, recipients, subject, html_message, cc_email=None, attachments=None):
    # print('attttttttttttttttttt',attachments)
    email_account = frappe.get_doc("Email Account", email_account)
    sender_email = email_account.email_id
    sender_password = email_account.get_password()

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ",".join(recipients)

    if cc_email:  # Add CC if provided
        message['Cc'] = ",".join(cc_email)

    message['Subject'] = subject

    # Attach the HTML message body
    message.attach(MIMEText(html_message, 'html'))

    # Handle file attachments
    if attachments:
        for attachment in attachments:
            part = MIMEApplication(attachment['fcontent'], Name=attachment['fname'])
            part['Content-Disposition'] = f'attachment; filename="{attachment["fname"]}"'
            message.attach(part)

    # Connect to the SMTP server and send the email
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            # Combine recipients and CC emails
            recipients_all = recipients + (cc_email if cc_email else [])

            # Send the email
            server.sendmail(sender_email, recipients_all, message.as_string())

            return {"status": True, "msg": "Mail sent successfully!"}
    except Exception as er:
        return {"status": False, "msg": f"Failed to send notification: {er}"}
