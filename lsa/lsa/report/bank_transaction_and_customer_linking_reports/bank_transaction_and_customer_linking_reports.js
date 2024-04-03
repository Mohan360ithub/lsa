// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Bank Transaction and Customer Linking Reports"] = {
	"filters": [
		{
			fieldname: "transaction_type",
			label: __("Transaction Type"),
			fieldtype: "Select",
			options:["","Internal Transfer","Receive"],
			default: "Receive",
		},		
	]
};

