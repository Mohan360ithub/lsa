// // Copyright (c) 2024, Mohan and contributors
// // For license information, please see license.txt

frappe.ui.form.on("Monthly Budget", {
    refresh(frm) {
        // Add a custom button
        frm.add_custom_button(__('Get Actual Amount'), function() {
            // Get the month and year from the form fields
            let month = frm.doc.month;
            let year = frm.doc.year;

            if (!month || !year) {
                frappe.msgprint(__('Please select both month and year.'));
                return;
            }

            // Fetch Sales Order records for the selected month
            frappe.call({
                method: 'lsa.lsa.doctype.monthly_budget.monthly_budget.get_sales_orders_for_month',
                args: {
                    month: month,
                    year: year
                },
                callback: function(response) {
                    console.log(response.message); // Debug line to check response
                    let salesOrders = response.message.sales_orders;
                    let salesInvoice = response.message.sales_invoices;

                    // Check if salesOrders is an array and has data
                    if (Array.isArray(salesOrders) && salesOrders.length > 0) {
                        let actualAmount = 0;

                        // Calculate the actual amount from the sales orders
                        salesOrders.forEach(function(order) {
                            actualAmount += order.amount;
                        });

                        // Display the actual amount
                        frm.set_value('monthly_actual_amount_so', actualAmount);

                        // Save the form
                        frm.save();
                    }
                    // Check if salesOrders is an array and has data
                    if (Array.isArray(salesInvoice) && salesInvoice.length > 0) {
                        let actualAmount = 0;

                        // Calculate the actual amount from the sales orders
                        salesInvoice.forEach(function(order) {
                            actualAmount += order.amount;
                        });

                        // Display the actual amount
                        frm.set_value('monthly_actual_amount_si', actualAmount);

                        // Save the form
                        frm.save();
                    }
                     else {
                        frappe.msgprint('No Sales Orders found for the selected month.');
                    }
                }
            });
        });

    },
    monthly_actual_amount_so: function(frm) {
        // Get the actual amount from the form
        let actualAmount = frm.doc.monthly_actual_amount_so;
        let monthlyPlanAmount = frm.doc.monthly_plan_amount;

        if (monthlyPlanAmount !== 0) {
            // Calculate and update the monthly_achieved_percentage_so
            let monthlyAchievedPercentage = (actualAmount / monthlyPlanAmount) * 100;
            frm.set_value('monthly_achieved_percentage_so', monthlyAchievedPercentage);
        } else {
            frappe.msgprint('Monthly Plan Amount cannot be zero.');
        }
    },
    monthly_actual_amount_si: function(frm) {
        // Get the actual amount from the form
        let actualAmount = frm.doc.monthly_actual_amount_si;
        let monthlyPlanAmount = frm.doc.si_monthly_plan_amount;

        if (monthlyPlanAmount !== 0) {
            // Calculate and update the monthly_achieved_percentage_so
            let monthlyAchievedPercentage = (actualAmount / monthlyPlanAmount) * 100;
            comsole.log(monthlyAchievedPercentage);
            frm.set_value('monthly_achieved_percentage_si', monthlyAchievedPercentage);
        } else {
            frappe.msgprint('Monthly Plan Amount cannot be zero.');
        }
    }
});




// frappe.ui.form.on("Monthly Budget", {
//     refresh(frm) {
//         // Add a custom button
//         frm.add_custom_button(__('Get Actual Amount'), function() {
//             // Get the month and year from the form fields
//             let month = frm.doc.month;
//             let year = frm.doc.year;

//             if (!month || !year) {
//                 frappe.msgprint(__('Please select both month and year.'));
//                 return;
//             }

//             // Fetch Sales Order records for the selected month
//             frappe.call({
//                 method: 'lsa.lsa.doctype.monthly_budget.monthly_budget.get_sales_orders_and_invoices_for_month',
//                 args: {
//                     month: month,
//                     year: year
//                 },
//                 callback: function(response) {
//                     if (response.message) {
//                         console.log(response.message);
//                         let salesOrdersAndInvoices = response.message;
//                         let actualAmountSO = 0;
//                         let actualAmountSI = 0;

//                         // Calculate the actual amounts from the sales orders and invoices
//                         salesOrdersAndInvoices.forEach(function(record) {
//                             if (record.doctype === 'Sales Order') {
//                                 actualAmountSO += record.amount;
//                             } else if (record.doctype === 'Sales Invoice') {
//                                 actualAmountSI += record.amount;
//                             }
//                         });

//                         // Display the actual amounts
//                         frm.set_value('monthly_actual_amount_so', actualAmountSO);
//                         frm.set_value('monthly_actual_amount_si', actualAmountSI);

//                         // Calculate and update the achieved percentages
//                         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//                         updateAchievedPercentages(frm, monthlyPlanAmount, actualAmountSO, actualAmountSI);

//                         // Save the form
//                         frm.save();
//                     } else {
//                         frappe.msgprint('No Sales Orders or Invoices found for the selected month.');
//                     }
//                 }
//             });
//         });

//     },
//     monthly_actual_amount_so: function(frm) {
//         // Calculate and update the achieved percentages
//         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//         let actualAmountSO = frm.doc.monthly_actual_amount_so;
//         let actualAmountSI = frm.doc.monthly_actual_amount_si;
//         updateAchievedPercentages(frm, monthlyPlanAmount, actualAmountSO, actualAmountSI);
//     },
//     monthly_actual_amount_si: function(frm) {
//         // Calculate and update the achieved percentages
//         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//         let actualAmountSO = frm.doc.monthly_actual_amount_so;
//         let actualAmountSI = frm.doc.monthly_actual_amount_si;
//         updateAchievedPercentages(frm, monthlyPlanAmount, actualAmountSO, actualAmountSI);
//     }
// });

// function updateAchievedPercentages(frm, monthlyPlanAmount, actualAmountSO, actualAmountSI) {
//     if (monthlyPlanAmount !== 0) {
//         let totalActualAmount = actualAmountSO + actualAmountSI;
//         let monthlyAchievedPercentageSO = (actualAmountSO / monthlyPlanAmount) * 100;
//         let monthlyAchievedPercentageSI = (actualAmountSI / monthlyPlanAmount) * 100;
//         let monthlyAchievedPercentageTotal = (totalActualAmount / monthlyPlanAmount) * 100;

//         frm.set_value('monthly_achieved_percentage_so', monthlyAchievedPercentageSO);
//         frm.set_value('monthly_achieved_percentage_si', monthlyAchievedPercentageSI);
//         // frm.set_value('monthly_achieved_percentage_total', monthlyAchievedPercentageTotal);
//     } else {
//         frappe.msgprint('Monthly Plan Amount cannot be zero.');
//     }
// }
