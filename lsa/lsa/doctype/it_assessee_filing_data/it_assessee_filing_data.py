# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime


class ITAssesseeFilingData(Document):
    def before_insert(doc):
        existing_doc = frappe.get_all(doc.doctype, filters={'ay': doc.ay, "it_assessee_file": doc.it_assessee_file})
        if existing_doc:
            frappe.throw("The IT Assessee Filing Data already exists.")

    def on_update(doc):
        if doc.filing_status=="FILED":
            existing_it_file = frappe.get_all(doc.doctype, 
                                          filters={'customer_id': doc.customer_id,
                                                   "filing_status":("in",["DOCS SHARED WITH CLIENT","FILED","ACK AND VERIFIED"])},
                                          fields=["name","ay","modified"]
                                          )
            if (existing_it_file):
                latest_file=""
                latest_file_fy=""
                latest_file_date=""
                for it_file in existing_it_file:
                    if latest_file_fy=="":
                        latest_file=it_file.name
                        latest_file_date=it_file.modified
                        latest_file_fy=it_file.ay
                    else:
                        fy_y=int(it_file.ay.split("-")[0])
                        fy_y_o=int(latest_file_fy.split("-")[0])
                        if fy_y_o<fy_y:
                            latest_file=it_file.name
                            latest_file_date=it_file.modified
                            latest_file_fy=it_file.ay
                
                date_object = datetime.strptime(str(latest_file_date).split(" ")[0], '%Y-%m-%d')
                formatted_date = date_object.strftime('%b-%Y')
                it_doc=frappe.get_doc("IT Assessee File",doc.it_assessee_file)
                it_doc.last_filed='for ' +latest_file_fy +' in '+formatted_date
                it_doc.save()
    


@frappe.whitelist()
def create_it_assessee_filing_data(yearly_report, current_form_name):
    try:
        existing_doc=frappe.get_all("IT Assessee Filing Data",
                                    filters={"it_assessee_file":current_form_name,
                                             "ay":yearly_report})
        if not(existing_doc):
            it_master_doc=frappe.get_doc("IT Assessee File",current_form_name)
            filing_data_doc = frappe.new_doc('IT Assessee Filing Data')
            filing_data_doc.ay = yearly_report
            filing_data_doc.it_assessee_file = current_form_name
            filing_data_doc.created_manually=1
            filing_data_doc.customer_id=it_master_doc.customer_id
            filing_data_doc.it_enabled=it_master_doc.enabled
            filing_data_doc.save()

            return "IT Assessee Filing Data created successfully."
        else:
            return "IT Assessee Filing Data you are trying to create already exists"
    except frappe.exceptions.ValidationError as e:
        frappe.msgprint(f"Validation Error: {e}")
        return False
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False

################################# Srikanth code Start ################################################################

@frappe.whitelist()
def get_gst_yearly_filing_data(candidate_id,ay):
    # Modify the query to filter based on candidate_id
    gst_data = frappe.get_all('Gst Yearly Filing Summery',
                              filters={'cid': candidate_id,'gst_yearly_summery_report_id':ay},
                              fields=['gstin', 'fy_last_month_of_filling', 'sales_total_taxable', 'company'])
    return gst_data


################################# Srikanth code End ################################################################

@frappe.whitelist()
def it_filing_can_be_filed(fy,customer_id,doc_ids=None):
    try:
        # print('Hii it_filing_can_be_filed method called',fy,'  --  ',doc_id)
        it_filing_data = frappe.get_all('IT Assessee Filing Data',
                                        filters={
                                            "ay":fy,
                                            "customer_id":customer_id
                                            })
        for itr_filing in it_filing_data:
            if doc_ids and itr_filing.name in doc_ids:
                frappe.db.set_value('IT Assessee Filing Data', itr_filing.name, 'can_be_filed', "YES")
            else:
                frappe.db.set_value('IT Assessee Filing Data', itr_filing.name, 'can_be_filed', "NO")
        frappe.db.commit()
        return {"status":True,"msg":"IT Filing status updated successfully"}
    except Exception as e:
        frappe.error_log(f"{e}")
        return {"status":False,"msg":f"IT Filing status update failed: {e}"}

@frappe.whitelist()
def authenticate_user():
    user=frappe.session.user
    
    user_roles = frappe.get_roles(user)
    
    # Check if the user has the "Onboarding Officer" role
    if "Customer Onboarding Officer" in user_roles or "Lsa Front Desk CRM Executive(A,B)" in user_roles:
        return {"status": True, "message": "User is an Onboarding Officer."}
    else:
        return {"status": False, "message": "User does not have the Onboarding Officer role."}




