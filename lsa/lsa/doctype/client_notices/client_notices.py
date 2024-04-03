# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClientNotices(Document):
	def on_update(self):
		if self.notices_status == "Closed" :
			self.status="Close"




@frappe.whitelist()
def set_prof_partner(doctype, txt, searchfield, start, page_len, filters):
	prof_partners=frappe.get_all("Supplier", 
									   filters={"supplier_group":"Associate Consultants (Prof Partner)"})
	prof_partners=[(i.name,) for i in prof_partners]
	return prof_partners



