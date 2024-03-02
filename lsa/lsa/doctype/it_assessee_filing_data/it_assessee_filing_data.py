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
                                    filters={"it_assessee_file":current_form_name})
        if not(existing_doc):
            filing_data_doc = frappe.new_doc('IT Assessee Filing Data')
            filing_data_doc.ay = yearly_report
            filing_data_doc.it_assessee_file = current_form_name
            filing_data_doc.created_manually=1
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


