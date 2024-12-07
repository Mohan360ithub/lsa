// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Efficiency Report"] = {
    filters: [
        {
            fieldname: "date_range",
            label: __("Date Range"),
            fieldtype: "DateRange",
            reqd: 0
        },
        {
            fieldname: "user",
            label: __("User"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options("User", txt);
            }
        },
        {
            fieldname: "master_gst_file",
            label: __("Master GST File"),
            fieldtype: "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options("Customer Chargeable Doctypes", txt);
            }
        }
    ]
};
