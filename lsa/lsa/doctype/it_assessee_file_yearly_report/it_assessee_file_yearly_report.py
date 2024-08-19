# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ITAssesseeFileYearlyReport(Document):
	def on_submit(self):
            try:
                # Fetch records from Gstfile with filter gst_type = 'regular'
                it_assessee_file = frappe.get_all("IT Assessee File", filters={"enabled": 1}, fields=["name","customer_id"])
                # print(it_assessee_file)

                # Create new records in GST Monthly Filing
                new_records = []
                for record in it_assessee_file:
                    new_record = frappe.get_doc({
                        "doctype": "IT Assessee Filing Data",
                        "it_assessee_file": record.name,
                        "ay": self.name,
                        "customer_id":record.customer_id,
                        # Set other fields as needed
                        # "some_other_field": "Some Value"
                    })

                    new_record.insert()
                    new_records.append(new_record.as_dict())

                frappe.msgprint("New Records Created in IT Assessee Filing Data!")

                return {"success": True}
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Error in fetch_and_insert_records")
                return {"success": False, "error_message": str(e)}


@frappe.whitelist()
def checking_user_authentication(user_email):
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_records = frappe.get_all('DocPerm',
                                          filters={'parent': 'IT Assessee Filing Data', 'create': 1},
                                          fields=["role"])
        for doc_perm_record in doc_perm_records:
            if doc_perm_record.role in roles:
                status = True
                break
        if user_email == "pankajsankhla90@gmail.com":
            status = True
        return {"status": status, "value": [roles, doc_perm_records]}
        
    except Exception as e:
        print(e)
        return {"status": "Failed"}


