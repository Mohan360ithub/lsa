import frappe
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


@frappe.whitelist()
def lead_notification(lead_name=None,mobile_no=None,source=None,custom_customer_id=None,type=None,lead_owner=None,city=None,custom_details=None,custom_services=None):


    try:
        # lead = frappe.get_all("Lead",leads[0].name)
                               
        email_account = frappe.get_doc("Email Account", "LSA Info")
        sender_email = email_account.email_id
        your_password= email_account.get_password()

        receiver_email= set()

        admin_setting_doc = frappe.get_doc("Admin Settings")
        for i in admin_setting_doc.lead_creation_notification_mails:
            receiver_email.add(i.user)

        receiver_email=",".join(list(receiver_email))

        subject = "Lead Creation Notification"

        lead_customer_id=''
        # Define lead details
        lead_name = lead_name
        lead_phone = mobile_no
        lead_source= source
        if lead_source=="Existing Customer":
            lead_customer_id= custom_customer_id
        lead_type = type
        lead_owner = lead_owner
        lead_city = city
        lead_details= custom_details
        service_of_interest= custom_services

        # Construct the HTML email body
        body = f"""
        <html>
        <head>
            <style>
                .container {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }}
                .table {{
                    border-collapse: collapse;
                    width: 100%;
                    border: 2px solid #444444;
                }}
                th, td {{
                    border: 2px solid #bcb9b4;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498DB;
                    color: white;
                }}
                .greeting {{
                    margin-bottom: 10px;
                }}
                .signature {{
                                    font-style: italic;
                                    color: #777;
                                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #777;
                    border-top: 1px solid #777;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="greeting">Dear Sir/Ma'am,</div>
                <p>This is to inform you about the details of a newly created lead:</p>
                <table class="table">
                    <thead>
                        <tr style="background-color:#3498DB;color:white;text-align: left;">
                            <th>S. No.</th>
                            <th>Field Name</th>
                            <th>Field Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>Name</td>
                            <td>{lead_name}</td>
                        </tr>
                        <tr>
                            <td>2</td>
                            <td>Email</td>
                            <td>{lead_phone}</td>
                        </tr>
                        <tr>
                            <td>3</td>
                            <td>Phone</td>
                            <td>{lead_source}</td>
                        </tr>
        """
        if lead_customer_id:
            body += f"""
                        <tr>
                            <td>4</td>
                            <td>Existing Customer</td>
                            <td>{lead_customer_id}</td>
                        </tr>
                """
        body += f"""
                        <tr>
                            <td>4</td>
                            <td>Company</td>
                            <td>{lead_type}</td>
                        </tr>
                        <tr>
                            <td>5</td>
                            <td>Owner</td>
                            <td>{lead_owner}</td>
                        </tr>
                        <tr>
                            <td>6</td>
                            <td>City</td>
                            <td>{lead_city}</td>
                        </tr>
                                  """
        if False:
            body += f"""
                            <tr>
                                <td>7</td>
                                <td>Interested Services</td>
                                <td>{service_of_interest}</td>
                            </tr>
                                    """
        body += f"""
                        <tr>
                            <td>7</td>
                            <td>Details</td>
                            <td>{lead_details}</td>
                        </tr>
                    </tbody>
                </table>
                <br><br>
                <div class="signature">Best regards,<br>LSA Office</div>
                <div class="footer">This is a system-generated email. Please do not reply to this message.</div>
            </div>
        </body>
        </html>
        """

        # Print or use the html_body as needed (e.g., send it in an email)
        # print(body)

        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))


        # Connect to the SMTP server
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, your_password)
            try:
                # Send email
                server.sendmail(sender_email, receiver_email.split(',') , message.as_string())
                # print ("Email sent successfully!")
                return {"status":True,"msg":"Successfully send Email notification regarding lead creation: "}
            except Exception as e:
                # print("Error:",e)
                frappe.msgprint (f"Failed to send email. Error: {e}")
                frappe.log_error(f"An error occurred while sending mail on creation of Lead: {e}")
                return {"status":False,"msg":f"Failed to send Email notification regarding lead creation: {e}"}
    except Exception as er:
        # print("Error: ",er)
        frappe.log_error(f"An error occurred while sending mail on creation of Lead: {er}")
        return {"status":False,"msg":f"Failed to send Email notification regarding lead creation: {er}"}



