# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NoticeFollowup(Document):
    def before_insert(self):
        followups = frappe.get_all(self.doctype, filters={'status': "Open", "client_notices_id": self.client_notices_id})
        if followups:
            followup_id = followups[0].name
            followup_url = "https://online.lsaoffice.com/app/notice-followups/" + followup_id
            frappe.throw(f"An Open Follow-up for {self.client_notices_id} already exists. <a href='{followup_url}'>{followup_id}</a>")


@frappe.whitelist()
def get_activities(client_notices_id):
    # Fetch open ToDos
    todos = frappe.get_all('Notice Followup', filters={'client_notices_id':client_notices_id}, fields=['name','status', 'date', 'description','allocated_to','followup_type'])
    return todos
    

@frappe.whitelist()
def get_todo_details(todo_name):
    todo = frappe.get_doc('Notice Followup', todo_name)
    return {
        'name':todo.name,
        'description': todo.description,
        'followup_type': todo.followup_type,
        'date': todo.date,
        'allocated_to': todo.allocated_to,
        'next_followup_date':todo.next_followup_date,
        'followup_type':todo.followup_type,
        # Add more fields as needed
    }     
    
@frappe.whitelist()
def update_todo(todo_name, updated_values):
    todo = frappe.get_doc('Notice Followup', todo_name)

    # Parse the JSON string into a dictionary
    updated_values_dict = frappe.parse_json(updated_values)

    # Update the ToDo with the edited values
    todo.update(updated_values_dict)
    todo.save()
    return True


@frappe.whitelist()
def get_open_fu(client_notices_id):
    followup=frappe.get_all("Notice Followup", 
                            filters={"status":"Open",
                                     "client_notices_id":client_notices_id})
    if followup:
         return followup[0].name
         
         



