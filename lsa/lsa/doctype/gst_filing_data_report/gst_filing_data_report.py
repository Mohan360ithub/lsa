# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GstFilingDataReport(Document):

    def before_submit(self):
        try:
            # Get the values of gst_yearly_summery_report and gst_type fields
            gst_yearly_summery_report = self.gst_yearly_summery_report
            gst_type = self.gst_type

            # Check gst_type and set quarterly or monthly accordingly
            if gst_type == "Regular" or gst_type == "QRMP":
                filing_frequency = self.month
            elif gst_type == "Composition":
                filing_frequency = self.quarterly
            else:
                frappe.msgprint("Gst Type should be either 'Regular', 'QRMP', or 'Composition'.")
                return

            # Apply filter on "Gst Yearly Filing Summery" DocType
            filter_conditions = {
                "gst_yearly_summery_report_id": gst_yearly_summery_report,
                "gst_type": gst_type
            }

            # Fetch records based on filter conditions
            matching_records = frappe.get_all("Gst Yearly Filing Summery", filters=filter_conditions, 
                                              fields=["gst_yearly_summery_report_id","gst_file_id","gst_type","name","customer_id"])

            # Process matching records as needed
            for record in matching_records:
                gst_filling_data = frappe.new_doc("Gst Filling Data")
                gst_filling_data.gst_yearly_filling_summery_id = record.name
                gst_filling_data.gstfile = record.gst_file_id
                gst_filling_data.month = filing_frequency
                gst_filling_data.gst_filling_report_id = self.name
                gst_filling_data.gst_type = record.gst_type
                gst_filling_data.customer_id = record.customer_id

                gst_filling_data.insert()
            self.step_4_count=len(matching_records)
            frappe.msgprint("New Records Created in Gst Filling Data!")

        except Exception as e:
            frappe.throw(f"Error: {e}")
            # frappe.msgprint(f"An error occurred: {e}")

@frappe.whitelist()
def get_gst_filing_data_report(gst_type,fy):
    gst_filing_data_reports=frappe.get_all("Gst Filing Data Report",
                                           filters={"gst_yearly_summery_report":fy,"gst_type":gst_type},
                                           fields=["name"])
    gst_filing_data_reports=[i.name for i in gst_filing_data_reports]
    return gst_filing_data_reports



