# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TaskGroup(Document):
	pass


# @frappe.whitelist()
# def get_task_group(doctype, txt, searchfield, start, page_len, filters):
#     print("Task Group Setup")
#     task_groups = frappe.get_all('Task Group',
# 								filters={

# 									},
# 								fields=["department"])
#     task_group_list=list(set([(i.department,) for i in task_groups]))
#     return task_group_list

@frappe.whitelist()
def get_activity(doctype, txt, searchfield, start, page_len, filters):
    task_groups = frappe.get_all('Task Group',
								filters={

									},
								fields=["department","name"])
    task_group_list=list(set([(i.name,) for i in task_groups]))
    return task_group_list

@frappe.whitelist()
def get_masters(doctype, txt, searchfield, start, page_len, filters):
    master = filters.get('master')
    customer_id = filters.get('customer_id')
    master_customer_map={"Gstfile":"customer_id",
                         "TDS File":"customer_id",
			 "Provident Fund File":"customer_id",
			 "Professional Tax File":"customer_id",
			 "MCA ROC File":"customer_id",
			 "IT Assessee File":"customer_id",
			 "Client Notices":"cid",
                         "Registration Application":"customer",
						}

    if customer_id:
        masters = frappe.get_all(master, filters={master_customer_map[master]: customer_id})
        master_list = [(master.name,) for master in masters]
        return  master_list
    elif master:
        masters = frappe.get_all(master)
        master_list = [(master.name,) for master in masters]
        return master_list
    else:
         return []

