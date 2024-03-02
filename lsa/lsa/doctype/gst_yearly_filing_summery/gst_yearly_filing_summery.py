# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GstYearlyFilingSummery(Document):
	def before_insert(self):
		all_yearly_doc = frappe.get_all('Gst Yearly Filing Summery',filters={"fy":self.fy})
		doc=frappe.get_doc("Gst Yearly Summery Report",self.fy)
		doc.step_2_count=len(all_yearly_doc)+1
		doc.save()
	def on_trash(self):
		all_yearly_doc = frappe.get_all('Gst Yearly Filing Summery',filters={"fy":self.fy})
		doc=frappe.get_doc("Gst Yearly Summery Report",self.fy)
		doc.step_2_count=len(all_yearly_doc)-1
		doc.save()

	
@frappe.whitelist()
def create_gst_yearly_filing_manually(gst_yearly_summary_report,gstfile,
									  company_name,customer_id,customer_status,executive_name,gst_type):
	try:
		existing_doc=frappe.get_all("Gst Yearly Filing Summery",
                                    filters={"gst_file_id":gstfile})
		if not(existing_doc):
			new_doc = frappe.new_doc('Gst Yearly Filing Summery')

			new_doc.gst_yearly_summery_report_id = gst_yearly_summary_report
			new_doc.fy = gst_yearly_summary_report
			new_doc.cid = customer_id
			new_doc.gst_file_id = gstfile
			new_doc.customer_status = customer_status
			new_doc.gstin = gstfile
			new_doc.gst_executive = executive_name
			new_doc.gst_type = gst_type
			new_doc.created_manually=1

			new_doc.save()
			return "Gst Yearly Filing Summery created successfully."
		else:
			return "Gst Yearly Filing Summery you are trying to create already exists"
	except Exception as e:
		print(e)
		return {"status":"Failed","dvalues":e}

@frappe.whitelist()
def checking_user_authentication(user_email):
	try:
		status=False
		user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

		# Extract roles from the result
		roles = [role.get('role') for role in user_roles]
		doc_perm_records = frappe.get_all('DocPerm',
									 filters = {'parent': 'Gst Yearly Filing Summery','create': 1},
									 fields=["role"])
		for doc_perm_record in doc_perm_records:
			if  doc_perm_record.role in roles:
				status=True
				break
		return {"status":status,"value":[roles,doc_perm_records]}
		
	except Exception as e:
		print(e)
		return {"status":"Failed"}



@frappe.whitelist()
def sync_step_2_with_step_4(yearly_summery):
    response = {}
    try:
        step_2_doc = frappe.get_doc("Gst Yearly Filing Summery", yearly_summery)
        step_4_list = frappe.get_all("Gst Filling Data",
                                    filters={'gst_yearly_filling_summery_id': yearly_summery,
                                            'submitted': 1},
                                    fields=["sales_total_taxable", "purchase_total_taxable", "tax_paid_amount",
                                            "interest_paid_amount", "penalty_paid_amount", "name",
                                            "fy", "month", "modified"])

        latest_file_mon = ""
        first_file_mon = ""
        month_num = {"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9, "jan": 10, "feb": 11, "mar": 12}

        # Initialize variables
        sales_total_taxable = 0.00
        purchase_total_taxable = 0.00
        tax_paid_amount = 0.00
        interest_paid_amount = 0.00
        penalty_paid_amount = 0.00

        for step_4 in step_4_list:
            sales_total_taxable += step_4.sales_total_taxable
            purchase_total_taxable += step_4.purchase_total_taxable
            tax_paid_amount += step_4.tax_paid_amount
            interest_paid_amount += step_4.interest_paid_amount
            penalty_paid_amount += step_4.penalty_paid_amount

            if not latest_file_mon:
                latest_file_mon = step_4.month
            else:
                mon = step_4.month.split("-")[0].lower()
                mon_o = latest_file_mon.split("-")[0].lower()
                if month_num[mon_o] < month_num[mon]:
                    latest_file_mon = step_4.month

            if not first_file_mon:
                first_file_mon = step_4.month
            else:
                mon = step_4.month.split("-")[0].lower()
                mon_o = first_file_mon.split("-")[0].lower()
                if month_num[mon_o] > month_num[mon]:
                    first_file_mon = step_4.month

        # Update fields in step 2 document
        step_2_doc.sales_total_taxable = sales_total_taxable
        step_2_doc.purchase_total_taxable = purchase_total_taxable
        step_2_doc.tax_paid_amount = tax_paid_amount
        step_2_doc.interest_paid_amount = interest_paid_amount
        step_2_doc.penalty_paid_amount = penalty_paid_amount
        step_2_doc.fy_first_month_of_filling = first_file_mon
        step_2_doc.fy_last_month_of_filling = latest_file_mon

        # Save the changes
        step_2_doc.save()

        response["message"] = "Gst Yearly Filing Summary Synced successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."

    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"

    return response



@frappe.whitelist()
def sync_all_step_2_with_step_4():
    response = {}

    try:
        step_2_list = frappe.get_all("Gst Yearly Filing Summery")
        for step_2 in step_2_list:
            if True:
                step_2_doc = frappe.get_doc("Gst Yearly Filing Summery", step_2.name)
                step_4_list = frappe.get_all("Gst Filling Data",
                                            filters={'gst_yearly_filling_summery_id': step_2.name,
                                                    'submitted': 1},
                                            fields=["sales_total_taxable","purchase_total_taxable","tax_paid_amount",
													"interest_paid_amount","penalty_paid_amount", "name",
                                            		"fy", "month", "modified"])
                latest_file_mon = ""
                first_file_mon = ""
                month_num = {"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9, "jan": 10, "feb": 11, "mar": 12}

                # Initialize variables
                sales_total_taxable = 0.00
                purchase_total_taxable = 0.00
                tax_paid_amount = 0.00
                interest_paid_amount = 0.00
                penalty_paid_amount = 0.00
                for step_4 in step_4_list:
                    sales_total_taxable += step_4.sales_total_taxable
                    purchase_total_taxable += step_4.purchase_total_taxable
                    tax_paid_amount += step_4.tax_paid_amount
                    interest_paid_amount += step_4.interest_paid_amount
                    penalty_paid_amount += step_4.penalty_paid_amount

                    if not latest_file_mon:
                        latest_file_mon = step_4.month
                    else:
                        mon = step_4.month.split("-")[0].lower()
                        mon_o = latest_file_mon.split("-")[0].lower()
                        if month_num[mon_o] < month_num[mon]:
                            latest_file_mon = step_4.month

                    if not first_file_mon:
                        first_file_mon = step_4.month
                    else:
                        mon = step_4.month.split("-")[0].lower()
                        mon_o = first_file_mon.split("-")[0].lower()
                        if month_num[mon_o] > month_num[mon]:
                            first_file_mon = step_4.month
                    

                # Update fields in step 2 document
                step_2_doc.sales_total_taxable = sales_total_taxable
                step_2_doc.purchase_total_taxable = purchase_total_taxable
                step_2_doc.tax_paid_amount = tax_paid_amount
                step_2_doc.interest_paid_amount = interest_paid_amount
                step_2_doc.penalty_paid_amount = penalty_paid_amount
                step_2_doc.fy_first_month_of_filling = first_file_mon
                step_2_doc.fy_last_month_of_filling = latest_file_mon

                # Save the changes
                step_2_doc.save()

        response["message"] = "Gst Yearly Filing Summary Synced successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."

    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"

    return response

