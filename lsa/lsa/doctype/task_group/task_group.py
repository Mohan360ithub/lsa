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
    master_customer_map={"Gstfile":["customer_id","company_name","name"],
                         "TDS File":["customer_id","deductor_name","name"],
						 "Provident Fund File":["customer_id","company_name","name"],
						 "Professional Tax File":["customer_id","company_name","name"],
						 "MCA ROC File":["customer_id","company_name","name"],
						 "IT Assessee File":["customer_id","assessee_name","name"],
						 "Client Notices":["cid","customer_firm_name","name"],
                         "Registration Application":["customer","entity_name","name"],
						}

    if customer_id:
        masters = frappe.get_all(master, filters={master_customer_map[master][0]: customer_id},fields=master_customer_map[master])
        master_list = [(master_i.name,master_i[master_customer_map[master][1]]) for master_i in masters]
        return  master_list
    elif master:
        masters = frappe.get_all(master)
        master_list = [(master.name,) for master in masters]
        return master_list
    else:
         return []


