// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Executive wise Service masters Report"] = {
	"filters": [
			{
				"fieldname": "customer_id",
				"label": __("CID"),
				"fieldtype": "Link",
				"options": "Customer",
			},

			{
				"fieldname": "executive",
				"label": __("Executive"),
				"fieldtype": "Link",
				"options": "User",
			},
			{
				"fieldname": "assigned_executive",
				"label": __("Assigned Executive"),
				"fieldtype": "Check",
				"default": 1,
			},
	
			{
				fieldname: "service_name",
				label: __("Service Name"),
				fieldtype: "Link",
				options: "Customer Chargeable Doctypes",
				// options: function() {
				// 	fetchAndSetOptions();
				// },
			},
			{
				fieldname: "frequency_filter",
				label: __("Frequency"),
				fieldtype: "MultiSelect",
				options: ["M","Y","Q","H"],
			},

	]
};


function myFunction() {
	frappe.prompt([
		{
			fieldname: 'service',
			label: 'Service Master',
			fieldtype: 'Link',
			options: 'Customer Chargeable Doctypes',
			reqd: true,
		},
		{
			fieldname: 'old_exe',
			label: 'Old Executive',
			fieldtype: 'Link',
			options: 'User',
			// reqd: true,
		},
		{
			fieldname: 'new_exe',
			label: 'New Executive',
			fieldtype: 'Link',
			options: 'User',
			reqd: true,
		}
	], function (values) {
		
		frappe.call({
			method: 'lsa.lsa.report.executive_wise_service_masters_report.executive_wise_service_masters_report.erp_last_checkin',
			args: {
				'service': values.service,
				'new_exe': values.new_exe,
				'old_exe': values.old_exe,
			},
			callback: function (resAsEx) {
				// Handle the response as needed
				if (resAsEx.message) {
					frappe.msgprint(resAsEx.message.msg);
					// console.log(response.message)
					// You can also update the form or perform other actions here
				}else{
					// frappe.msgprint(resWaSingle.message.msg);
					// console.log(resWa.message)
				}
			}
		});
				
	}, 'Executive Reassignment');
}
