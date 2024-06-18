// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Executive wise Service masters Report"] = {
	"filters": [
			{
				"fieldname": "customer_id",
				"label": __("CID"),
				"fieldtype": "Link",
				"options": "Customer",
			},

			{
				"fieldname": "executive",
				"label": __("Executive"),
				"fieldtype": "Link",
				"options": "User",
			},
			{
				"fieldname": "assigned_executive",
				"label": __("Assigned Executive"),
				"fieldtype": "Check",
				"default": 1,
			},
	
			{
				fieldname: "service_name",
				label: __("Service Name"),
				fieldtype: "Link",
				options: "Customer Chargeable Doctypes",
				// options: function() {
				// 	fetchAndSetOptions();
				// },
			},
			{
				fieldname: "frequency_filter",
				label: __("Frequency"),
				fieldtype: "MultiSelect",
				options: ["M","Y","Q","H"],
			},

	]
};
