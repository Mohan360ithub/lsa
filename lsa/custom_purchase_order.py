# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe



@frappe.whitelist()
def set_prof_partner(doctype, txt, searchfield, start, page_len, filters):
	prof_partners=frappe.get_all("Supplier", 
									   filters={"supplier_group":"Associate Consultants (Prof Partner)"})
	prof_partners=[(i.name,) for i in prof_partners]
	return prof_partners

@frappe.whitelist()
def reset_prof_partner(doctype, txt, searchfield, start, page_len, filters):
	prof_partners=frappe.get_all("Supplier")
	prof_partners=[(i.name,) for i in prof_partners]
	return prof_partners


@frappe.whitelist()
def set_item_price(supplier_id, item_code):
	prof_partner=frappe.get_all("Supplier",
							  	 	filters={"name":supplier_id})
	it_price=0.00
	if prof_partner:
		prof_partner_doc=frappe.get_doc("Supplier",prof_partner[0].name)
		for item in prof_partner_doc.custom_services:
			if item.service==item_code:
				it_price=item.fees

	return it_price




@frappe.whitelist()
def set_items(doctype, txt, searchfield, start, page_len, filters):
	print(filters)
	prof_partner_doc=frappe.get_doc("Supplier","CA Nidhi Agarwal")
	item_l=[]
	for item in prof_partner_doc.custom_services:
		item_l.append(item.service)
	item_l=[(i.name,) for i in item_l]
	return item_l
