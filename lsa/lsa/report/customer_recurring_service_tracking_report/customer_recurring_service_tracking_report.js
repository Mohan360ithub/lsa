// Copyright (c) 2023, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Recurring Service Tracking Report"] = {
    "filters": [
   		{
			fieldname: "enabled",
			label: __("Enabled"),
			fieldtype: "Select",
			options:["All","Yes","No"],
			default: "Yes",
		},
		{
			fieldname: "service_user",
			label: __("Customer with/without Services"),
			fieldtype: "Select",
			options:["All","Customers with Services","Customers without Services"],
			default: "Customers with Services",
		},		
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options:["All","ACTIVE","ON NOTICE","HOLD"],
			default: "All",
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
				   
    ]
};
