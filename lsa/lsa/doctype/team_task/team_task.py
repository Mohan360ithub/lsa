import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
 
class TeamTask(Document):
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

