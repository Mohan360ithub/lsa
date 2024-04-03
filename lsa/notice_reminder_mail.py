import frappe
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def mail_remainder_for_client_notice():
    notice_fu=frappe.get_all("Notice Followup",
                             filters={"status":"Open"}, 
                             fields=["name","next_followup_date","allocated_to","client_notices_id",
                                     "customer_id","customer_name","contact_person","mobile_no"])
    today = datetime.now().date()
    tomorrow= today + timedelta(days=1)
    ls={}
    for notice in notice_fu:
        if notice.next_followup_date in (today,tomorrow):
            if notice.allocated_to not in ls:
                ls[notice.allocated_to]=[[notice.name,notice.client_notices_id,notice.customer_id,notice.customer_name,
                                            notice.next_followup_date,notice.contact_person,notice.mobile_no]]
            else:
                ls[notice.allocated_to]+=[[notice.name,notice.client_notices_id,notice.customer_id,notice.customer_name,
                                            notice.next_followup_date,notice.contact_person,notice.mobile_no]]
                
    send_reminder_mail_notice(ls)
    return


def send_reminder_mail_notice(ls):
    
    if ls:
        for emp in ls:
            e_mail=frappe.get_doc("Official Email","Official Email")
            emp_name=""
            emp_ls=frappe.get_all("Employee",
                                    filters={
                                        "company_email":emp
                                    },
                                    fields=["employee_name"]
                                )
            if emp_ls:
                emp_name=emp_ls[0].employee_name

            # Email configuration
            sender_email = e_mail.email_id
            your_password=e_mail.app_password
            cc_email = "vatsal.k@360ithub.com"
            receiver_email = "360ithub.developers@gmail.com"
            subject = 'Client Notice Reminder for approaching due date'

            # body ='for client notice reminder'
            body = f"<html><body><p style='color: black;'>Dear {emp_name},</p>"
            body += "<p style='color: black;'>Please find below the Client Notices reaching the deadline of doc submission. Please followup ASAP:</p>"
            body += '''<table class="table table-bordered" style="border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr style="background-color: #3498DB; color: white; text-align: left;">
                                <th style="border: solid 2px #bcb9b4;">Notice ID</th>
                                <th style="border: solid 2px #bcb9b4;">Customer ID</th>
                                <th style="border: solid 2px #bcb9b4;">Customer Name</th>
                                <th style="border: solid 2px #bcb9b4;">Next Follow-up Date</th>
                                <th style="border: solid 2px #bcb9b4;">Contact Person</th>
                                <th style="border: solid 2px #bcb9b4;">Mobile No</th>
                            </tr>
                        </thead>
                        <tbody>
            '''

            for allocated_to, data in ls.items():
                for row in data:
                    body += f"<tr style='color: black;'><td style='border: solid 2px #bcb9b4;'>{row[1]}</td><td style='border: solid 2px #bcb9b4;'>{row[2]}</td><td style='border: solid 2px #bcb9b4;'>{row[3]}</td><td style='border: solid 2px #bcb9b4;'>{row[4]}</td><td style='border: solid 2px #bcb9b4;'>{row[5]}</td><td style='border: solid 2px #bcb9b4;'>{row[6]}</td></tr>"

            body += "</tbody></table></body></html>"




            # Create the email message
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Cc'] = cc_email 
            message['Subject'] = subject
            message.attach(MIMEText(body, 'html'))


            # Connect to the SMTP server
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, your_password)
                try:
                    # Send email
                    server.sendmail(sender_email, receiver_email.split(',') + cc_email.split(','), message.as_string())
                    print("Email sent successfully!")
                except Exception as e:
                    print(f"Failed to send email. Error: {e}")

   

