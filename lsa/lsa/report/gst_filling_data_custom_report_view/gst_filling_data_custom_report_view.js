// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Gst Filling Data Custom Report View"] = {
	"filters": [
		
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Gst Yearly Summery Report",
			"default":"2023-2024",
		},
		{
			"fieldname": "gst_type",
			"label": __("GST Type"),
			"fieldtype": "Select",
			"options": ["", "Regular", "Composition", "QRMP"],
			"on_change": function() {
				// Call a function to update the "Month" filter options based on "gst_type"
				updateMonthFilterOptions();
			},
			"default":"Composition",
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": ["", "JAN", "FEB", "MAR", "JAN-MAR", "APR", "MAY", "JUN", "APR-JUN",
				"JUL", "AUG", "SEP", "JUL-SEP", "OCT", "NOV", "DEC", "OCT-DEC"],
			"get_query": function(doc) {
				// Call a function to get the modified options based on "gst_type"
				return getModifiedMonthFilterOptions(doc.gst_type);
			},
			"default":"APR-JUN",
		},
		{
			"fieldname": "customer_id",
			"label": __("Customer ID"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "customer_status",
			"label": __("Customer Status"),
			"fieldtype": "Select",
			"options": [ "","Enabled", "Disabled",],
			"default":"Enabled",
		},
	]
};

function updateMonthFilterOptions() {
	var gstType = frappe.query_report.get_filter_value("gst_type");

	// Based on gstType, enable or disable certain options in the "Month" filter
	var monthFilter = frappe.query_report.get_filter("month");
	var options = getModifiedMonthFilterOptions(gstType);
	monthFilter.df.options = options;
	monthFilter.refresh();
}

function getModifiedMonthFilterOptions(gstType) {
	// Return the modified options based on the selected "gst_type"
	if (gstType === "Composition") {
		return ["", "APR-JUN", "JUL-SEP", "OCT-DEC", "JAN-MAR"];
	} else {
		return ["","APR", "MAY", "JUN",
				"JUL", "AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR" ];
	}
}



// // Copyright (c) 2024, Mohan and contributors
// // For license information, please see license.txt

// frappe.query_reports["Gst Filling Data Custom Report"] = {
// 	"filters": [
		
// 		// {
// 		// 	"fieldname": "name",
// 		// 	"label": __("ID"),
// 		// 	"fieldtype": "Link",
// 		// 	"options": "Gst Filling Data"
// 		// },
// 		{
// 			"fieldname": "fy",
// 			"label": __("Fiscal Year"),	
// 			"fieldtype": "Link",
// 			"options": "Gst Yearly Summery Report"
// 		},
// 		{
// 			"fieldname": "gst_type",
// 			"label": __("GST Type"),
// 			"fieldtype": "Select",
//             "options": [
// 				"",
// 				"Regular",
// 				"Composition",
// 				"QRMP"	
// 			]
// 		},
		
// 		{
// 			"fieldname": "month",
// 			"label": __("Month"),
// 			"fieldtype": "Select",
//             "options": ["","JAN","FEB","MAR","JAN-MAR","APR","MAY","JUN","APR-JUN",
//                 		"JUL","AUG","SEP","JUL-SEP","OCT","NOV","DEC","OCT-DEC"]
// 		},

		
		
// 		// {
// 		// 	"fieldname": "executive",
// 		// 	"label": __("Executive"),
// 		// 	"fieldtype": "Data"
// 		// },
// // {
// // 			"fieldname": "gst_yearly_filling_summery_id",
// // 			"label": __("GstYearly Filing Summery Id"),
// // 			"fieldtype": "Link",
// // 			"options": "Gst Yearly Filing Summery"

// // 		}
// 	]
// };


