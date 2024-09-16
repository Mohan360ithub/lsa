
frappe.query_reports["Gst Filling Data Custom Report"] = {
	"filters": [
		
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Gst Yearly Summery Report"
		},
		{
			"fieldname": "gst_type",
			"label": __("GST Type"),
			"fieldtype": "Select",
			"options": ["", "Regular", "Composition", "QRMP"],
			"on_change": function() {
				// Call a function to update the "Month" filter options based on "gst_type"
				updateMonthFilterOptions();
			}
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
			}
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
		{
			"fieldname": "non_compliant",
			"label": __("Compliance Status"),
			"fieldtype": "Select",
			"options": [ "","Compliant", "Non-Compliant",],
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


function bulk_wa_txt_message() {

	frappe.prompt([
		{
			fieldname: 'customer_status',
			label: 'Customer Status',
			fieldtype: 'MultiSelect',
			options: ["ACTIVE","ON NOTICE","HOLD"],
			reqd: true,
		},
		{
			fieldname: 'gst_step_4_status',
			label: 'Filing Status',
			fieldtype: 'MultiSelect',
			options:["Pending", "Filed Summery Shared With Client", "GSTR-1 or IFF Prepared and Filed",
                "GSTR-2A/2B or 4A/4B Reco done", "Data Collected", "Data Finalized", "Tax Calculation Done",
                "Tax Informed to Client", "Tax Payment Processed", "GSTR-3B / CMP08 Prepared and Filed"],
			// reqd: true,
		},
		{
			fieldname: 'message',
			label: 'Message',
			fieldtype: 'Small Text',
			reqd: true,
		}
	], function (values) {
		gst_step_4_status=null
		if (values.gst_step_4_status){
			gst_step_4_status=values.gst_step_4_status
		}
		
		frappe.call({
			method: 'lsa.lsa.report.gst_filling_data_custom_report.gst_filling_data_custom_report.send_bulk_wa_for_filtered_gst_customer',
			args: {
				'message': values.message,
				'customer_status': values.customer_status,
				'fy':frappe.query_report.get_filter_value('fy'),
				'gst_type':frappe.query_report.get_filter_value('gst_type'),
				'month':frappe.query_report.get_filter_value('month'),
				'non_compliant':frappe.query_report.get_filter_value('non_compliant'),
				"customer_enable_status":frappe.query_report.get_filter_value("customer_status"),
				"customer_id":frappe.query_report.get_filter_value("customer_id"),
				'gst_step_4_status': gst_step_4_status,
			},
			callback: function (resBulkWA) {
				// Handle the response as needed
				if (resBulkWA.message.status) {
					frappe.msgprint(resBulkWA.message.msg);
				}else{
					console.log(resBulkWA)
				}
			}
		});
				
	}, 'Configure bulk customer notifications for GST filing:');
}


