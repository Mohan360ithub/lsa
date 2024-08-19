# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from lsa.custom_mail import single_mail


class TeamTicket(Document):
    ################################### Srikanth Code Start #################################################################
    def before_insert(self):

        user = self.created_by
        #####################################################Modified By Vatsal Start #################################################
        sub_category = self.sub_category
        sub_category_list=frappe.get_all("Team Ticket Sub Category",filters={"name":sub_category},fields=["name","sub_category"])
        if sub_category_list and sub_category_list[0].sub_category == "Attendance Regularization":
        #####################################################Modified By Vatsal End #################################################
            date_to_regularise=datetime.strptime(self.regularization_date, "%Y-%m-%d").date()
            employee = frappe.get_all('Employee', filters={'user_id': user}, fields=['name'])

            absent_record = frappe.get_all(
                                            'Attendance',
                                            filters={
                                                'employee': employee[0].name,
                                                'status': "Absent",
                                            },
                                            fields=["attendance_date"]
                                            
                                        )
            absent_record_list=[record.attendance_date for record in absent_record]
            
            if date_to_regularise not in absent_record_list:
                frappe.throw(
                    f"You are applying Regularisation for Invalid Date!"
                )
        

            # Check if a record with the same regularization_date exists for the same created_by user
            existing_regularisation_record = frappe.get_all(
                                                            'Team Ticket',
                                                            filters={
                                                                'created_by': self.created_by,
                                                                'regularization_date': self.regularization_date,
                                                            },
                                                            fields=['name', 'created_by']
                                                        )
                                                        

            if existing_regularisation_record:
                frappe.throw(
                    f"An attendance regularization request for {self.regularization_date} already exists."
                )
    ################################### Srikanth Code End #################################################################

    def after_insert(self):
        user = frappe.session.user
        sub_category = self.sub_category
        sub_category_doc = frappe.get_doc('Team Ticket Sub Category', sub_category)

        ticket_executive_list = set()
        if user != "Administrator":
            ticket_executive_list.add(user)
        
        if sub_category_doc.mail_notification:
            for i in sub_category_doc.mail_notification:
                ticket_executive_list.add(i.user)
        ticket_executive_list = list(ticket_executive_list)

        ticket_manager_list = set()
        admin_setting_doc = frappe.get_doc("Admin Settings")
        for i in admin_setting_doc.team_ticket_cc_mails:
            ticket_manager_list.add(i.user)
        ticket_manager_list = list(ticket_manager_list)

        ticket_notification(self, ticket_executive_list, ticket_manager_list, sub_category_doc.sub_category)


def ticket_notification(doc,ticket_executive_list,ticket_manager_list,sub_category):
    try:
        now = datetime.now()
        # Format the datetime in DD-MM-YYYY HH:MM AM/PM
        time_of_change = now.strftime("%d-%m-%Y %I:%M %p")
        user_full_name = frappe.db.get_value("User", frappe.session.user, "full_name")

        subject = f"{doc.type} Ticket raised by {user_full_name}"
        message = f"""
            <p>Dear Team,<br><br> A {doc.type} Ticket raised by {user_full_name} with following details. </p>
            <table style="border-collapse: collapse; width: 60%;">
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Ticket Ref.</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;"><a href="https://online.lsaoffice.com/app/team-ticket/{doc.name}">{doc.name}</a></td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Ticket Title</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{doc.title}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Raised By</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{user_full_name}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Type</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{doc.type}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">Sub-Category</td>
                    <td style="border: 1px solid #f0f0f0; padding: 8px; text-align: left;">{sub_category}</td>
                </tr>
            </table>
			<p>Please make a note of it and do the needful.</p>
            <br><br>
            <p>Best regards,<br>LSA Office</p>
        """

        # frappe.sendmail(
        #     # recipients=recipients,  # Use the list of combined email addresses
        #     recipients=ticket_executive_list,
		# 	cc=ticket_manager_list,
        #     subject=subject,
        #     message=message
        # )
        resp=single_mail("LSA Accounts",ticket_executive_list,subject,message,ticket_manager_list)
        if not resp["status"]:
            msg=resp['msg']
            print(f"Failed to send Team Ticket notification: {msg}")
            frappe.log_error(message=f"Failed to send mail for Team Ticket notification {doc.name}", title=f"Failed to send mail for Team Ticket notification {doc.name}")
            return {"status":False,"msg": f"Failed to send mail for to send Team Ticket notification {doc.name}"}
        
        # print(list(executive_list), subject, message)
        return {"status": True, "message": "Notified for Ticket Successfully"}
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to notified for Ticket raised")
        # print(f"{e}")
        return {"status": False, "message": f"Failed to notified for Ticket raised {e}"}

################################### Srikanth Code Start #################################################################
@frappe.whitelist()
def check_details_already_existing_date_or_not():
    try:
        cur_month = frappe.utils.now_datetime().month
        usr = frappe.session.user
        emp_data = frappe.get_all('Employee', filters={"user_id": usr}, fields=['name', 'employee_name','user_id'])
        
        regularization_records = []
        for emp in emp_data:
            emp_name = emp.name
            mail_id = emp.user_id
            attendance_regularization = frappe.get_all(
                "Team Ticket",
                filters={
                    # "employee": emp_name,
                    "created_by": mail_id
                },
                fields=["regularization_date", "name"]
            )
            for record in attendance_regularization:
                # Convert date format to 'dd-mm-yyyy'
                formatted_date = frappe.utils.formatdate(record['regularization_date'], "dd-MM-yyyy")
                regularization_records.append({
                    "regularization_date": formatted_date,
                    "name": record['name']
                })
        
        return regularization_records
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Error in check_details_already_existing_date_or_not')
        return {"error": str(e)}
################################### Srikanth Code End #################################################################


