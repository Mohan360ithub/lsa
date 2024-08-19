import frappe
from frappe.model.document import Document

class GstYearlySummeryReport(Document):
    def on_submit(self):
        try:
            # Fetch records from Gstfile with filter gst_type = 'regular'
            gstfile_records = frappe.get_all("Gstfile", filters={"enabled": 1}, fields=["gst_number","customer_id"])
            # print(gstfile_records)

            # Create new records in GST Monthly Filing
            new_records = []
            for record in gstfile_records:
                new_record = frappe.get_doc({
                    "doctype": "Gst Yearly Filing Summery",
                    "gst_file_id": record.gst_number,
                    "fy": self.fy,
                    "gst_yearly_summery_report_id": self.fy,
                    "customer_id":record.customer_id,
                    # Set other fields as needed
                    # "some_other_field": "Some Value"
                })

                new_record.insert()
                new_records.append(new_record.as_dict())

            frappe.msgprint("New Records Created in GST Yearly Filing Summery!")

            return {"success": True}
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in fetch_and_insert_records")
            return {"success": False, "error_message": str(e)}

