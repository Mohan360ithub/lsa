import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
 
class TeamTask(Document):
    def after_insert(self):
        if self.assigned_to:
            # Add permissions for the new user
            frappe.log_error( title=f"Assigned to shared {self.assigned_to}")
            frappe.share.add("Team Ticket", self.name, self.assigned_to, read=1, write=0, share=0)
            
            
    def before_save(self):
        frappe.throw("Hooks working!!!")
        # Check if assigned_to has been updated
        if self.is_new():
            return

        previous_assigned_user = frappe.db.get_value("Team Ticket", self.name, "assigned_to")
        if previous_assigned_user and previous_assigned_user != self.assigned_to:
            frappe.log_error( title=f"Unassigned to shared {previous_assigned_user}")
            # Remove permissions from the previous user
            frappe.share.remove("Team Ticket", self.name, previous_assigned_user)
            if  self.assigned_to:
                frappe.share.add("Team Ticket", self.name, self.assigned_to, read=1, write=0, share=0)
                frappe.log_error( title=f"Assigned after unassigning to shared {self.assigned_to}")


        
        if not previous_assigned_user and self.assigned_to:
            # Add permissions for the new user
            frappe.log_error( title=f"Assigned freshly to shared {self.assigned_to}")
            frappe.share.add("Team Ticket", self.name, self.assigned_to, read=1, write=0, share=0)

        frappe.db.commit()
        
    def validate(self):
        self.update_task_due_status()
    
    def update_task_due_status(self):
        if self.task_status == 'Completed':
            # if not self.completion_date_time:
            self.completion_date_time = now_datetime()
            self.task_due_status = 'Closed'
        elif self.task_status == 'Cancelled':
            self.task_due_status = 'Closed'
        elif self.task_status == 'Hold':
            self.task_due_status = 'Hold'
 
####################################  SCHEDULAR CODE ##############################################################
from frappe.utils import now_datetime
 
@frappe.whitelist()
def check_overdue_tasks():
    now = now_datetime()
    
    # Fetch all tasks where completion_date_time is greater than expected_end_date_time
    overdue_tasks = frappe.get_all('Team Task',
                                    filters={
                                        # 'completion_date_time': ('<', now),
                                        'expected_end_date_time': ('<', now), #### Less than 25 < 26
                                        'task_status': ['in', ['Pending', 'Under Process']]  # Corrected syntax for 'in' operator
                                    },
                                    fields=['name'])
    print(overdue_tasks)
    for task in overdue_tasks:
        doc = frappe.get_doc('Team Task', task['name'])  # Access 'name' key from task dictionary
        #print('dddddddddddddd',doc)
        # if doc.task_due_status != 'Over Due':
        doc.task_due_status = 'Over Due'
        doc.save()



