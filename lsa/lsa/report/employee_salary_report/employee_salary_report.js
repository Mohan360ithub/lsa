// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Salary Report"] = {
	"filters": [
			{
				"fieldname": "fy",
				"label": __("Fiscal Year"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				reqd: true,
			},

			{
				"fieldname": "month",
				"label": __("Month"),
				"fieldtype": "Select",
				"options": "April\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember\nJanuary\nFebruary\nMarch",
				reqd: true,
			},
			{
				"fieldname": "employee",
				"label": __("Employee"),
				"fieldtype": "Link",
				"options": "Employee",
			},
	

	]
};

