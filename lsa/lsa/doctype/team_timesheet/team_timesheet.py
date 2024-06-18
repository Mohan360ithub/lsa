# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TeamTimesheet(Document):
	pass

@frappe.whitelist()
def get_employee_id_for_current_user():
    current_user = frappe.session.user
    employee_list = frappe.get_all("Employee", 
                                   filters={"user_id": current_user, "status": "Active"}, 
                                   fields=["name"])
    if not employee_list:
        return None
    return employee_list[0].name
