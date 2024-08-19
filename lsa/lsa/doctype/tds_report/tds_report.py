# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TDSREPORT(Document):
	def on_submit(self):
            try:
                # Fetch records from Gstfile with filter gst_type = 'regular'
                tds_file = frappe.get_all("TDS File", filters={"enabled": 1}, fields=["name","customer_id"])
                # print(tds_file)

                # Create new records in TDS QTRLY FILING
                new_records = []
                for record in tds_file:
                    new_record = frappe.get_doc({
                        "doctype": "TDS QTRLY FILING",
                        "tds_file": record.name,
                        "tds_report": self.name,
                        "fy": self.fy,
                        "customer_id": record.customer_id,
                        # Set other fields as needed
                        # "some_other_field": "Some Value"
                    })

                    new_record.insert()
                    new_records.append(new_record.as_dict())

                frappe.msgprint("New Records Created in TDS QTRLY FILING!")

                return {"success": True}
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), "Error in fetch_and_insert_records")
                return {"success": False, "error_message": str(e)}

