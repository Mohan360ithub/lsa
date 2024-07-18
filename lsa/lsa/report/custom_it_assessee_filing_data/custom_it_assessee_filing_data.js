// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Custom IT Assessee Filing Data"] = {
	"filters": [
		{
			"fieldname": "ay",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "IT Assessee File Yearly Report"
		},
	]
};



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
			fieldname: 'it_step_2_status',
			label: 'Filing Status',
			fieldtype: 'MultiSelect',
			options:["PENDING INITIAL CONTACT", "DOCUMENTS REQUESTED", "DOCUMENTS PARTIALLY RECEIVED",
                "DOCUMENTS FULLY COLLECTED", "REVIEWED AND VERIFIED", "RETURN PREPARED", "SHARED TO CLIENT REVIEW",
                "FILED", "ACK AND VERIFIED", "DOCS SHARED WITH CLIENT"],
			// reqd: true,
		},
		{
			fieldname: 'message',
			label: 'Message',
			fieldtype: 'Small Text',
			reqd: true,
		}
	], function (values) {
		it_step_2_status=null
		if (values.it_step_2_status){
			it_step_2_status=values.it_step_2_status
		}
		
		frappe.call({
			method: 'lsa.lsa.report.custom_it_assessee_filing_data.custom_it_assessee_filing_data.send_bulk_wa_for_filtered_it_customer',
			args: {
				'message': values.message,
				'customer_status': values.customer_status,
				'ay':frappe.query_report.get_filter_value('ay'),
				'it_step_2_status': it_step_2_status,
			},
			callback: function (resBulkWA) {
				// Handle the response as needed
				if (resBulkWA.message) {
					frappe.msgprint(resBulkWA.message.msg);
				}
			}
		});
				
	}, 'Configure bulk customer notifications for IT filing:');
}



