# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class Gstfile(Document):

    def before_insert(self):
        pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]\w{3}$'
        field_value = self.gst_number
        if not re.match(pattern, field_value):
            frappe.throw("Please Enter Valid GST Number")

    def on_update(self):
        gst_file = frappe.get_all("Gstfile", filters={"name": self.name})
        if gst_file:
            gst_filling_data_s = frappe.get_all("Gst Filling Data",
                                                filters={"gstfile": self.name})
            # print(gst_filling_data_s)
            for gst_filling_data in gst_filling_data_s:
                frappe.set_value("Gst Filling Data", gst_filling_data.name, "gst_password", self.gst_password)

    def before_save(self):
        gst_file = frappe.get_all("Gstfile", filters={"name": self.name})
        if gst_file:
            freq_type_map = {"M": ["Regular", "QRMP"], "Q": ["Composition"]}
            old_doc = frappe.get_doc(self.doctype, self.name)

            old_frequency = old_doc.frequency
            new_frequency = self.frequency

            old_gst_type = old_doc.gst_type
            new_gst_type = self.gst_type

            if new_frequency not in freq_type_map:
                frappe.throw(f"Invalid frequency selected")
            elif old_frequency != new_frequency and new_gst_type not in freq_type_map[new_frequency]:
                frappe.throw(f"'{new_gst_type}' type customer can't have frequency '{new_frequency}'")

            if self.gst_type == "Composition":
                self.frequency = "Q"
            elif self.gst_type in ["Regular", "QRMP"]:
                self.frequency = "M"

            frequency_dict = {"M": 12, "Q": 4, "H": 2, "Y": 1}
            self.annual_fees = self.current_recurring_fees * frequency_dict[self.frequency]

            field_to_update = ["enabled","customer_id"]
            
            for field in field_to_update:
                if self.get(field) != old_doc.get(field):
                    # Find link fields in the current doctype
                    link_fields = frappe.get_all(
                        "DocField",
                        filters={"fieldtype": "Link", "options": self.doctype},
                        fields=["parent", "fieldname"]
                    )

                    for link_field in link_fields:
                        link_fieldname = link_field["fieldname"]
                        fetch_from = link_fieldname + "." + field

                        if link_field:
                            # Find fields that fetch from the current doctype's field
                            doctypes_fetching_field = frappe.get_all(
                                "DocField",
                                filters={"fetch_from": fetch_from, "parent": link_field["parent"]},
                                fields=["parent", "fieldname"]
                            )

                            for doctype_fetching_field in doctypes_fetching_field:
                                parent_doctype = doctype_fetching_field["parent"]
                                fetched_fieldname = doctype_fetching_field["fieldname"]

                                # Log the changes or perform actions based on the fetched doctypes and fields
                                frappe.logger().info(f"Field '{fetched_fieldname}' in doctype '{parent_doctype}' fetches from {self.doctype}'s {field} field and needs to be handled.")

                                # Find related documents where the link field points to the current document
                                related_docs = frappe.get_all(parent_doctype, filters={link_fieldname: self.name}, fields=["name"])
                                for related_doc in related_docs:
                                    frappe.db.set_value(parent_doctype, related_doc["name"], fetched_fieldname, self.get(field))

                    frappe.db.commit()



