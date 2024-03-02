
# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re

class Gstfile(Document):

	def before_insert(self):

		pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]\w{3}$'
		field_value = self.gst_number
		if not re.match(pattern,field_value):
			frappe.throw("Please Enter Valid GST Number")

	def on_update(self):
		gst_filling_data_s=frappe.get_all("Gst Filling Data",
                                    filters={"gstfile":self.name})
		print(gst_filling_data_s)
		for gst_filling_data in gst_filling_data_s:
			frappe.set_value("Gst Filling Data", gst_filling_data.name, "gst_password", self.gst_password)

	def before_save(self):
		freq_type_map={"M":["Regular","QRMP"],"Q":["Composition"]}
		old_doc = frappe.get_doc(self.doctype,self.name)

		old_frequency = old_doc.frequency
		new_frequency=self.frequency

		old_gst_type = old_doc.gst_type
		new_gst_type=self.gst_type

		if new_frequency not in freq_type_map:
			frappe.throw(f"Invalid frequency selected")
		elif old_frequency!=new_frequency and  new_gst_type not in freq_type_map[new_frequency]:
			frappe.throw(f"'{new_gst_type}' type customer can't have frequency '{new_frequency}'")


		if self.gst_type=="Composition":
			self.frequency="Q"
		elif self.gst_type in ["Regular","QRMP"]:
			self.frequency="M"

		frequency_dict={"M":12,"Q":4,"H":2,"Y":1}
		self.annual_fees=self.current_recurring_fees*frequency_dict[self.frequency]
			





