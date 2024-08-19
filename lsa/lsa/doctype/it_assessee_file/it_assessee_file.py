import frappe
from frappe.model.document import Document

class ITAssesseeFile(Document):
    def before_save(self):
        field_to_update = ["enabled", "customer_id"]
        if frappe.db.exists(self.doctype, self.name):
            old_doc = frappe.get_doc(self.doctype, self.name)
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


