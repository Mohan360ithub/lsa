# # Copyright (c) 2024, Mohan and contributors
# # For license information, please see license.txt


import frappe
from frappe.model.document import Document

class LeadFollowup(Document):
    def before_insert(self):
        followups = frappe.get_all(self.doctype, filters={'status': "Open", "lead_id": self.lead_id})
        if followups:
            followup_id = followups[0].name
            followup_url = "https://online.lsaoffice.com/app/lead-followup/" + followup_id
            frappe.throw(f"An Open Follow-up for {self.lead_id} already exists. <a href='{followup_url}'>{followup_id}</a>")


@frappe.whitelist()
def create_todo(date, description, lead_name, lead_id, assign_to=None, category=None):
    todo = frappe.get_doc({
        'doctype': 'ToDo',
        'date': date,
        'allocated_to': assign_to,
        'description': description,
        'category': category,
        'reference_type': "Lead",
        'reference_name': lead_id,
        'custom_lead_id1':lead_id,
        'custom_lead_name': lead_name
    })
    todo.insert(ignore_permissions=True)

    return todo.name

@frappe.whitelist()
def get_activities(lead_id):
    # Fetch open ToDos
    todos = frappe.get_all('Lead Followup', filters={'lead_id':lead_id}, fields=['name','status', 'date', 'description','allocated_to','followup_type'])
    return todos
    
# @frappe.whitelist()
# def close_todo(todo_name):
#     try:
#         # Load the ToDo
#         todo = frappe.get_doc('Lead Followup', todo_name)
        
#         # Set the status to 'Closed'
#         todo.status = 'Closed'
        
#         # Save the changes
#         todo.save()
        
#         return True
#     except frappe.DoesNotExistError:
#         frappe.msgprint(f"ToDo {todo_name} not found.")
#         return False
#     except Exception as e:
#         frappe.msgprint(f"Error closing ToDo: {str(e)}")
#         return False

@frappe.whitelist()
def get_todo_details(todo_name):
    todo = frappe.get_doc('Lead Followup', todo_name)
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
    todo = frappe.get_doc('Lead Followup', todo_name)

    # Parse the JSON string into a dictionary
    updated_values_dict = frappe.parse_json(updated_values)

    # Update the ToDo with the edited values
    todo.update(updated_values_dict)
    todo.save()
    return True


@frappe.whitelist()
def get_open_fu(lead_id):
    followup=frappe.get_all("Lead Followup", 
                            filters={"status":"Open",
                                     "lead_id":lead_id})
    if followup:
         return followup[0].name
         
         
@frappe.whitelist()
def lost_lead(lead_id,lost_reason):
    lead_doc=frappe.get_doc("Lead", lead_id)
    if lead_doc:
         lead_doc.custom_lead_lost_reason=lost_reason
         lead_doc.status="Lost"
         lead_doc.save()
         return True
    return False

