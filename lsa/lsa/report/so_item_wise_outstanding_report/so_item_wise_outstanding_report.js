// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["SO Item wise Outstanding Report"] = {
	"filters": [
			{
				"fieldname": "customer_id",
				"label": __("CID"),
				"fieldtype": "Link",
				"options": "Customer",
			},
			// {
			// 	fieldname: "doc_status",
			// 	label: __("Doc Status"),
			// 	fieldtype: "MultiSelect",
			// 	options:["Draft","Submitted","Cancelled"],
			// 	default: "Draft,Submitted",
			// },
			{
				fieldname: "service_type",
				label: __("Service Type"),
				fieldtype: "MultiSelect",
				options:["","GST Filling","TDS Filling","PT Filling","ROC Filling","Incometax Filing"],
				default: "GST Filling",
			},
			{
				fieldname: "custom_payment_status",
				label: __("Payment Status"),
				fieldtype: "MultiSelect",  // Change fieldtype to "MultiSelect" for multi-select filter
				options: ["Unpaid","Cleared","Partially Paid"],
				default: "Unpaid,Partially Paid",
			},
			{
				fieldname: "customer_enabled",
				label: __("Customer Enabled"),
				fieldtype: "Select",
				options:["","Customer Enabled","Customer Disabled"],
				default: "Customer Enabled",
			},
			{
				fieldname: "sales_invoice",
				label: __("Sales Invoice"),
				fieldtype: "Select",
				options:["Yes","No",""],
				default: "No",
			},
			{
				fieldname: "customer_tag",
				label: __("Customer Payment Agreement"),
				fieldtype: "Select",
				options:["","SO Not Approved","SO Approved","Not Approached SO"],
				default: "",
			},

			{
				"fieldname": "executive",
				"label": __("Executive"),
				"fieldtype": "Link",
				"options": "User",
			},
			{
				fieldname: "from_date",
				label: __("From Date"),
				fieldtype: "Date",
				default: "2023-04-01",
				// reqd:1,
			},
			{
				fieldname: "to_date",
				label: __("To Date"),
				fieldtype: "Date",
				default: "2024-03-31",
				// reqd:1,
			},
		]
};

