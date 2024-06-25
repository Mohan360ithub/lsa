// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Gst Yearly Filing Summery custom report"] = {
	"filters": [
		
	{
		"fieldname": "gst_yearly_summery_report_id",
		"label": __("Fiscal Year"),
		"fieldtype": "Link",
		"options": "Gst Yearly Summery Report",
		"reqd":1,
	},
	{
		"fieldname": "gst_type",
		"label": __("GST Type"),
		"fieldtype": "Select",
		"options": ["", "Regular", "Composition", "QRMP"],
		
	},
	
	{
			"fieldname": "customer_id",
			"label": __("Customer ID"),
			"fieldtype": "Link",
			"options": "Customer"
	},
	
	{
		"fieldname": "customer_status",
		"label": __("Customer Status"),
		"fieldtype": "Select",
		"options": [ "","Enabled", "Disabled",],
		"default":"Enabled",
	},
	{
		"fieldname": "gst_status",
		"label": __("GST Status"),
		"fieldtype": "Select",
		"options": [ "","GST Enabled", "GST Disabled",],
		"default":"GST Enabled",
	},
	{
		"fieldname": "non_compliant",
		"label": __("Compliance Status"),
		"fieldtype": "Select",
		"options": [ "","Compliant", "Non-Compliant",],
	},
	{
		"fieldname": "gst_file",
		"label": __("GSTIN"),
		"fieldtype": "Link",
		"options": "Gstfile",
	},

	]
};


