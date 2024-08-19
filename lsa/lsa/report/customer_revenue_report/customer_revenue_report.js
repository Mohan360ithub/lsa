// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Revenue Report"] = {
	"filters": [
		{
			"fieldname": "customer_id",
			"label": __("Customer ID"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd":1,
		},
		
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "FY",
			"reqd":1,
		},
		// {
		// 	"fieldname": "month",
		// 	"label": __("Month"),
		// 	"fieldtype": "Select",
		// 	"options": ["", "JAN", "FEB", "MAR",  "APR", "MAY", "JUN", 
		// 				"JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
		// 				// "JAN-MAR","APR-JUN","JUL-SEP",  "OCT-DEC",
		// 				],
			
		// },
		

	]
};

