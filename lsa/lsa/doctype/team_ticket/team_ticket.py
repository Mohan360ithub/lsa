# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class TeamTicket(Document):

	def after_insert(doc):

		user=frappe.session.user

		sub_category=doc.sub_category
		sub_category_doc = frappe.get_doc('Team Ticket Sub Category', sub_category)

		ticket_executive_list=set()
		if user!="Administrator":
			ticket_executive_list.add(user)
		
		if sub_category_doc.mail_notification:
			for i in sub_category_doc.mail_notification:
				ticket_executive_list.add(i.user)
		ticket_executive_list = list(ticket_executive_list)

		ticket_manager_list=set()
		admin_setting_doc = frappe.get_doc("Admin Settings")
		for i in admin_setting_doc.team_ticket_cc_mails:
			ticket_manager_list.add(i.user)
		ticket_manager_list = list(ticket_manager_list)

		
		ticket_notification(doc,ticket_executive_list,ticket_manager_list,sub_category_doc.sub_category)


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

        frappe.sendmail(
            # recipients=recipients,  # Use the list of combined email addresses
            recipients=ticket_executive_list,
			cc=ticket_manager_list,
            subject=subject,
            message=message
        )
        # print(list(executive_list), subject, message)
        return {"status": True, "message": "Notified for Ticket Successfully"}
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to notified for Ticket raised")
        # print(f"{e}")
        return {"status": False, "message": f"Failed to notified for Ticket raised {e}"}

