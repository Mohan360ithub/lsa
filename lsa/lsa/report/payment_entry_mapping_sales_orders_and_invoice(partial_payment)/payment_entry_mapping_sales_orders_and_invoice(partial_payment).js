// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Payment Entry Mapping Sales Orders and Invoice(Partial payment)"] = {
	"filters": [
				{
			"fieldname": "customer_id",
			"label": __("CID"),
			"fieldtype": "Link",
			"options": "Customer",
		},

		{
			fieldname: "doc_status",
			label: __("Doc Status"),
			fieldtype: "MultiSelect",
			options:["Draft","Submitted","Cancelled"],
			default: "Draft,Submitted",
			hidden:1,
		},


		{
			fieldname: "custom_payment_status",
			label: __("Payment Status"),
			fieldtype: "MultiSelect",  // Change fieldtype to "MultiSelect" for multi-select filter
			options: ["Cleared","Partially Paid"],
			default: "Partially Paid",
			hidden:1,
		},
		// {
		// 	fieldname: "customer_enabled",
		// 	label: __("Customer Enabled"),
		// 	fieldtype: "Select",
		// 	options:["","Customer Enabled","Customer Disabled"],
		// 	default: "Customer Enabled",
		// },
		{
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Select",
			options:["Yes","No",""],
			default: "No",
			hidden:1,
		},
				{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},

		// Account Paid To
		{
			fieldname: "paid_to",
			label: __("Account Paid To"),
			fieldtype: "Link",
			options:"Account"
		},
		// Mode of Payment
		{
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			options:"Mode of Payment"
			
		},
	]
};
