// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Missing SO before 2024 for Recurring Services"] = {
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
		{
            "fieldname": "custom_gst_type",
            "label": __("Customer GST Type"),
            "fieldtype": "MultiSelectList",
            "options": ["NULL","Regular", "Composition", "QRMP"],
            // Custom filter logic will handle empty or "All" selection separately
            get_data: function (txt) {
                // Define the options array
                let options = ["NULL","Regular", "Composition", "QRMP"];
        
                // Filter options based on the input text
                return options.filter(option => option.toLowerCase().includes(txt.toLowerCase()));
            }
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
