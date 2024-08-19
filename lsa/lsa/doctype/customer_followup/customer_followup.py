
# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerFollowup(Document):
	def before_insert(doc):
		followup=frappe.get_all(doc.doctype, filters={ 'status': "Open","customer_id":doc.customer_id})
		if followup:
			frappe.throw((f"An Open Followup for {doc.customer_id} already exists."))

		followup_sales_order_summary=doc.sales_order_summary
		followup_sales_order_summary=followup_sales_order_summary.strip()
		followup_sales_order_summary_list=followup_sales_order_summary.split(", ")
		for sales_order in followup_sales_order_summary_list:
			sales_order_exists=frappe.get_all("Sales Order", 
									   filters={"name":sales_order,"customer":doc.customer_id})
			if sales_order_exists:
				previous_followup_list=frappe.get_all(doc.doctype,filters={"sales_order_summary": ["like", f"%{sales_order}%"]})
				sales_order_doc=frappe.get_doc("Sales Order", sales_order)
				sales_order_doc.custom_followup_count=len(previous_followup_list)+1
				# print(sales_order_doc)
				sales_order_doc.save()

		

	def before_save(doc):
		# if doc.next_followup_date is None and doc.status=="Closed":
		# 	frappe.throw((f"An Open Followup for {doc.customer_id} already exists."))
		pass
	def on_trash(doc):

		followup_sales_order_summary=doc.sales_order_summary
		followup_sales_order_summary=followup_sales_order_summary.strip()
		followup_sales_order_summary_list=followup_sales_order_summary.split(", ")
		for sales_order in followup_sales_order_summary_list:
			sales_order_exists=frappe.get_all("Sales Order", 
									   filters={"name":sales_order,"customer":doc.customer_id})
			if sales_order_exists:
				sales_order_doc=frappe.get_doc("Sales Order", sales_order)
				sales_order_doc.custom_followup_count-=1
				# print(sales_order_doc)
				sales_order_doc.save()

@frappe.whitelist()
def close_followup(docname):
	try:
		followup_doc=frappe.get_doc("Customer Followup", docname)
		followup_doc.status="Closed"
		followup_doc.save()
		return {"status":True,"msg":"Followup Closed Successfully"}
	except Exception as e:
		return {"status":False,"msg":e}


	

