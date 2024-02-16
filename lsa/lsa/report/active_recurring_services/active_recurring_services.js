frappe.query_reports["Active recurring services"] = {
	"filters": [
		{
			"fieldname": "customer_id",
			"label": __("CID"),
			"fieldtype": "Link",
			"options": "Customer",
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

function fetchAndSetOptions() {
	frappe.call({
		method: 'lsa.lsa.report.active_recurring_services.active_recurring_services.get_services',
		callback: function(response) {
			if (response && response.message) {
				var service_list = JSON.parse(response.message);
				frappe.query_report.set_filter_options('service_name', service_list);
			} else {
				console.error('Error fetching services');
			}
		}
	});
}

