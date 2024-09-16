// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Missing SO for Recurring Services"] = {
	"filters": [
		{
			fieldname: "fy",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "FY",
			reqd:1,
		},
		// {
		// 	fieldname: "missing",
		// 	label: __("Missing"),
		// 	fieldtype: "Select",
		// 	options: ["","Yes","No"],
		// 	default:"Yes",
		// },
		{
			fieldname: "service_master",
			label: __("Service Name"),
			fieldtype: "Link",
			options: "Customer Chargeable Doctypes",
		},
		{
			fieldname: "service_enabled",
			label: __("Service Enabled"),
			fieldtype: "Select",
			options: ["","Yes","No"],
            		default: "Yes",
		},
		// {
		// 	fieldname: "frequency_filter",
		// 	label: __("Frequency"),
		// 	fieldtype: "MultiSelect",
		// 	options: ["M","Y","Q","H"],
		// },
		{
			"fieldname": "customer_id",
			"label": __("CID"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		// {
		// 	fieldname: "from_date",
		// 	label: __("From Date"),
		// 	fieldtype: "Date",
		// },
		// {
		// 	fieldname: "to_date",
		// 	label: __("To Date"),
		// 	fieldtype: "Date",
		// },
		// {
		// 	"fieldname": "date_range",
		// 	"label": __("Date Range"),
		// 	"fieldtype": "DateRange",
		// },
	]
};
