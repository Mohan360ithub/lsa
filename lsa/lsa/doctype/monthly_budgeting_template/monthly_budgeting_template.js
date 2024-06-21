// Copyright (c) 2024, Mohan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Monthly Budgeting Template", {
    refresh(frm) {
        // Add a custom button
        frm.add_custom_button(__('Add Month and Year'), function() {
            // Open prompt to get month and year
            frappe.prompt([
                {
                    fieldname: 'month',
                    fieldtype: 'Select',
                    options: [
                        { value: 'January', label: 'January' },
                        { value: 'February', label: 'February' },
                        { value: 'March', label: 'March' },
                        { value: 'April', label: 'April' },
                        { value: 'May', label: 'May' },
                        { value: 'June', label: 'June' },
                        { value: 'July', label: 'July' },
                        { value: 'August', label: 'August' },
                        { value: 'September', label: 'September' },
                        { value: 'October', label: 'October' },
                        { value: 'November', label: 'November' },
                        { value: 'December', label: 'December' }
                    ].map(opt => opt.value).join('\n'), // Frappe needs options as newline-separated values
                    label: 'Month',
                    reqd: 1
                },
                {
                    fieldname: 'year',
                    fieldtype: 'Link',
                    options: 'Year',
                    label: 'Year',
                    reqd: 1
                }
            ], function(values) {
                // Prepare the new document with values from the current document and the prompt
                let new_doc = Object.assign({}, frm.doc, {
                    doctype: 'Monthly Budget',
                    month: values.month,
                    year: values.year
                });

                // Remove unnecessary fields
                delete new_doc.name;
                delete new_doc.__islocal;
                delete new_doc.__unsaved;
                delete new_doc.owner;

                // Create the new document
                frappe.call({
                    method: 'frappe.client.insert',
                    args: {
                        doc: new_doc
                    },
                    callback: function(response) {
                        if (response && response.message) {
                            frappe.msgprint('Monthly Budget document created successfully.');
                        } else {
                            frappe.msgprint('Failed to create Monthly Budget document.');
                        }
                    }
                });
            }, 'Enter Month and Year', 'Submit');
        });
    },
});
