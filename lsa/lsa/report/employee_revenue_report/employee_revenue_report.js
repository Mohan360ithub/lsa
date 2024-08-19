// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Revenue Report"] = {
	"filters": [
		{
			"fieldname": "employee_id",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd":1,
		},
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "FY",
			"reqd":1,
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": ["April", "May", "June", "July", "August", "September", 
						 "October", "November", "December","January", "February", "March",
						// "JAN-MAR","APR-JUN","JUL-SEP",  "OCT-DEC",
						],
			"reqd":1,
			
		},
		

	]
};

