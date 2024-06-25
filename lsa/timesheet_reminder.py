import frappe
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


@frappe.whitelist()
def mail_remainder_for_timesheet():
    # Get yesterday's date
    # yesterday = datetime.now() - timedelta(days=1)
    # print("hi in one minute")
    # Check if yesterday was a working day
    if True:
        from datetime import datetime, date

        # Get the current year and month
        current_year = datetime.now().year
        current_month = datetime.now().month
        #current_year=2023
        #current_month = 12
        # print(current_year)
        first_day_of_month = date(current_year, current_month, 1)
        if current_year == 2024 and current_month == 6:
            first_day_of_month = date(current_year, current_month, 11)

        # Get the last day of the current month
        if current_month == 12:
            last_day_of_month = date(current_year, current_month, 31)
        else:
            last_day_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)
        

        # Retrieve attendance data for yesterday
        attendance_data = frappe.get_all('Attendance', 
                                         filters={
                                                    'docstatus': 1,
                                                    'status': 'Present',
                                                    'attendance_date': ['between', [first_day_of_month, last_day_of_month]]
                                                },
                                        fields=['employee','attendance_date'])
        attendance_data_emp={}
        for at in attendance_data:
            if at.employee not in attendance_data_emp:
                attendance_data_emp[at.employee]=[str(datetime.strptime(str(at.attendance_date), '%Y-%m-%d').strftime('%d-%m-%Y'))]
            else:
                attendance_data_emp[at.employee]+=[str(datetime.strptime(str(at.attendance_date), '%Y-%m-%d').strftime('%d-%m-%Y'))]
        del attendance_data

        timesheet_data = frappe.get_all('Team Timesheet', 
                                         filters={
                                                    'docstatus': 1,
                                                    'date': ['between', [first_day_of_month, last_day_of_month]],
                                                },
                                        fields=['employee','date'])
        timesheet_data_emp={}
        for ts in timesheet_data:
            if ts.employee not in timesheet_data_emp:
                timesheet_data_emp[ts.employee]=[str(datetime.strptime(str(ts.date), '%Y-%m-%d').strftime('%d-%m-%Y'))]
            else:
                timesheet_data_emp[ts.employee]+=[str(datetime.strptime(str(ts.date), '%Y-%m-%d').strftime('%d-%m-%Y'))]
        del timesheet_data

        mail_emp_date={}
        for emp in attendance_data_emp:
            if emp in timesheet_data_emp:
                for day in attendance_data_emp[emp]:
                    if day not in timesheet_data_emp[emp]:
                        if emp not in mail_emp_date:
                            mail_emp_date[emp]=[day]
                        else:
                            mail_emp_date[emp]+=[day]
            else:
                mail_emp_date[emp]=attendance_data_emp[emp]
        # del attendance_data_emp
        # del timesheet_data_emp
        
        return send_reminder_email_timesheet(mail_emp_date)


def send_reminder_email_timesheet(mail_emp_date):
    if mail_emp_date:
        emp_ls=frappe.get_all("Employee",
                                    filters={
                                        "name":("in",list(mail_emp_date)),
                                        "status":"Active",
                                    },
                                    fields=["name","employee_name","personal_email","company_email","reports_to","custom_timesheet"]
                                )
        # print(emp_ls)
        # email_account = frappe.get_doc("Email Account", "LSA OFFICE")

        email_account = frappe.get_doc("Email Account", "LSA HR")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()

        # Send the email
        sender_email = email_account.email_id
        sender_password=email_account.get_password()

        for emp in emp_ls:
            # cc_email = "hr@lsaoffice.com"
            cc_email=""
            if emp.reports_to:
                emp_rep_to=frappe.get_doc("Employee",emp.reports_to)
                if emp_rep_to.user_id:
                    cc_email+=(","+emp_rep_to.user_id)
                if not emp.custom_timesheet:
                    continue

            emp_name=emp.employee_name
            emp_pers_mail=emp.personal_email
            emp_official_mail=emp.company_email

            # dates=(", ").join([str(dt) for dt in mail_emp_date[emp.name]])
            

            # Email configuration
            sender_email = sender_email
            your_password=sender_password
            # cc_email = "hr@lsaoffice.com"
            receiver_email = f"{emp_pers_mail},{emp_official_mail}"
            
            
            subject = "Reminder: Timesheet Non-Submission"
    
            body = f'''<html>
                        <head>
                            <style>
                                .container {{
                                    font-family: Arial, sans-serif;
                                    padding: 20px;
                                    border: 1px solid #ccc;
                                    border-radius: 5px;
                                    background-color: #f9f9f9;
                                }}
                                .greeting {{
                                    
                                    margin-bottom: 10px;
                                }}
                                .message {{
                                    margin-bottom: 15px;
                                }}
                                .signature {{
                                    font-style: italic;
                                    color: #777;
                                }}
                                .disclaimer {{
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
                                <div class="greeting">Dear {emp_name},</div>
                                <div class="message">
                                    <p>This is a friendly reminder to submit your timesheet for the following dates:</p>
                                    <ul>'''
            for dt in mail_emp_date[emp.name]:
                body+=f"<li>{dt}</li>"

            body+='''
                                    </ul>
                                    <p>Please ensure that your timesheet is submitted promptly to avoid any delays in processing.</p>
                                </div>
                                <div class="signature">Best regards,<br>LSA Office</div>

                                <div class="disclaimer">This is a system-generated email. Please do not reply to this message.</div>
                            </div>
                        </body>
                    </html>
                    '''
            # Create the email message
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver_email
            message['Cc'] = cc_email 

            #bcc_email = "360ithub.developers@gmail.com"
            #message['Bcc'] = bcc_email

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
                    server.sendmail(sender_email, receiver_email.split(',') + cc_email.split(','), message.as_string())
                    # print ("Email sent successfully!")
                except Exception as e:
                    print (f"Failed to send email. Error: {e}")
        return ("Email sent successfully!")
    return "Invalid Input"




@frappe.whitelist()
def nonsubmitted_timesheet_dates():
    from datetime import datetime, date, timedelta

    current_user = frappe.session.user
    employee_list = frappe.get_all("Employee", 
                                   filters={"user_id": current_user, "status": "Active"}, 
                                   fields=["name", "employee_name", "company", "designation", "department"])
    if not employee_list:
        return []
    employee = employee_list[0].name

    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month
    # current_year = 2023
    # current_month = 12
    first_day_of_month = date(current_year, current_month, 1)
    if current_year==2024 and current_month==6:
        first_day_of_month = date(current_year, current_month, 11)

    # Get the last day of the current month
    if current_month == 12:
        last_day_of_month = date(current_year, current_month, 31)
    else:
        last_day_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)

    # Retrieve attendance data
    attendance_data = frappe.get_all('Attendance', 
                                     filters={
                                         "employee": employee,
                                         'docstatus': 1,
                                         'status': 'Present',
                                         'attendance_date': ['between', [first_day_of_month, last_day_of_month]]
                                     },
                                     fields=['employee', 'attendance_date', 'working_hours'])
    attendance_data_emp = {}
    for at in attendance_data:
        date_str = str(datetime.strptime(str(at.attendance_date), '%Y-%m-%d').strftime('%d-%m-%Y'))
        attendance_data_emp[date_str] = at.working_hours

    timesheet_data = frappe.get_all('Team Timesheet', 
                                     filters={
                                         "employee": employee,
                                         'docstatus': ["in", (0, 1)],
                                         'date': ['between', [first_day_of_month, last_day_of_month]],
                                     },
                                     fields=['employee', 'date',"total_working_hours", 'docstatus'])
    timesheet_data_emp = {}
    for ts in timesheet_data:
        date_str = str(datetime.strptime(str(ts.date), '%Y-%m-%d').strftime('%d-%m-%Y'))
        timesheet_data_emp[date_str] = [ts.docstatus, ts.total_working_hours]

    mail_emp_date = []
    for day, working_hours in attendance_data_emp.items():
        if day not in timesheet_data_emp:
            mail_emp_date.append((day, working_hours,0.00, "Timesheet Not Created"))
        elif timesheet_data_emp[day] == 0:
            mail_emp_date.append((day, working_hours,timesheet_data_emp[day][1], "Timesheet Created, Not Submitted"))

    return mail_emp_date



@frappe.whitelist()
def nonsubmitted_timesheet_dates_all_emp():
    from datetime import datetime, date, timedelta

    # Get all active employees
    employee_list = frappe.get_all("Employee", 
                                   filters={"status": "Active"}, 
                                   fields=["name", "employee_name", "company", "designation", "department"])

    # Get the current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month
    first_day_of_month = date(current_year, current_month, 1)
    if current_year == 2024 and current_month == 6:
        first_day_of_month = date(current_year, current_month, 11)

    # Get the last day of the current month
    if current_month == 12:
        last_day_of_month = date(current_year, current_month, 31)
    else:
        last_day_of_month = date(current_year, current_month + 1, 1) - timedelta(days=1)

    mail_emp_dates = []
    emp_count={}
    for emp in employee_list:
        employee = emp.name

        # Retrieve attendance data
        attendance_data = frappe.get_all('Attendance', 
                                         filters={
                                             "employee": employee,
                                             'docstatus': 1,
                                             'status': 'Present',
                                             'attendance_date': ['between', [first_day_of_month, last_day_of_month]]
                                         },
                                         fields=['employee', 'attendance_date', 'working_hours'])
        attendance_data_emp = {}
        emp_count[emp.employee_name]=0

        for at in attendance_data:
            date_str = str(datetime.strptime(str(at.attendance_date), '%Y-%m-%d').strftime('%d-%m-%Y'))
            attendance_data_emp[date_str] = at.working_hours

        # Retrieve timesheet data
        timesheet_data = frappe.get_all('Team Timesheet', 
                                         filters={
                                             "employee": employee,
                                             'docstatus': ["in", (0, 1)],
                                             'date': ['between', [first_day_of_month, last_day_of_month]],
                                         },
                                         fields=['employee', 'date',"total_working_hours", 'docstatus'])
        timesheet_data_emp = {}
        for ts in timesheet_data:
            date_str = str(datetime.strptime(str(ts.date), '%Y-%m-%d').strftime('%d-%m-%Y'))
            timesheet_data_emp[date_str] = [ts.docstatus, ts.total_working_hours]

        for day, working_hours in attendance_data_emp.items():
            emp_count[emp.employee_name]+=1
            if day not in timesheet_data_emp:
                mail_emp_dates.append({
                    "employee": emp.employee_name,
                    "date": day,
                    "checkin_hours": working_hours,
                    "timesheet_hours": 0.00,
                    "status": "Timesheet Not Created"
                })
            elif timesheet_data_emp[day] == 0:
                mail_emp_dates.append({
                    "employee": emp.employee_name,
                    "date": day,
                    "checkin_hours": working_hours,
                    "timesheet_hours": timesheet_data_emp[day][1],
                    "status": "Timesheet Created, Not Submitted"
                })

    return {"timesheet_data":mail_emp_dates,"emp_count":emp_count}




