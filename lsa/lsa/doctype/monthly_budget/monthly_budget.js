// // // Copyright (c) 2024, Mohan and contributors
// // // For license information, please see license.txt

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

//             // Fetch Sales Order and Sales Invoice records for the selected month
//             frappe.call({
//                 method: 'lsa.lsa.doctype.monthly_budget.monthly_budget.get_sales_orders_for_month',
//                 args: {
//                     month: month,
//                     year: year
//                 },
//                 callback: function(response) {
//                     // Log the response to understand its structure
//                     console.log(response.message);

//                     if (response.message) {
//                         let salesOrders = response.message.sales_orders || [];
//                         let salesInvoices = response.message.sales_invoices || [];
//                         let actualAmountSO = 0;
//                         let actualAmountSI = 0;

//                         // Calculate the actual amounts from the sales orders and invoices
//                         salesOrders.forEach(function(order) {
//                             actualAmountSO += order.amount;
//                         });

//                         salesInvoices.forEach(function(invoice) {
//                             actualAmountSI += invoice.amount;
//                         });

//                         // Display the actual amounts
//                         frm.set_value('monthly_actual_amount_so', actualAmountSO);
//                         frm.set_value('monthly_actual_amount_si', actualAmountSI);

//                         // Calculate and update the achieved percentages
//                         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//                         let siMonthlyPlanAmount = frm.doc.si_monthly_plan_amount;
//                         updateAchievedPercentages(frm, monthlyPlanAmount, siMonthlyPlanAmount, actualAmountSO, actualAmountSI);

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
//         // Get the actual amount from the form
//         let actualAmountSO = frm.doc.monthly_actual_amount_so;
//         let actualAmountSI = frm.doc.monthly_actual_amount_si;
//         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//         let siMonthlyPlanAmount = frm.doc.si_monthly_plan_amount;
        
//         updateAchievedPercentages(frm, monthlyPlanAmount, siMonthlyPlanAmount, actualAmountSO, actualAmountSI);
//     },
//     monthly_actual_amount_si: function(frm) {
//         // Get the actual amount from the form
//         let actualAmountSO = frm.doc.monthly_actual_amount_so;
//         let actualAmountSI = frm.doc.monthly_actual_amount_si;
//         let monthlyPlanAmount = frm.doc.monthly_plan_amount;
//         let siMonthlyPlanAmount = frm.doc.si_monthly_plan_amount;

//         updateAchievedPercentages(frm, monthlyPlanAmount, siMonthlyPlanAmount, actualAmountSO, actualAmountSI);
//     }
// });

// function updateAchievedPercentages(frm, monthlyPlanAmount, siMonthlyPlanAmount, actualAmountSO, actualAmountSI) {
//     if (monthlyPlanAmount !== 0) {
//         let monthlyAchievedPercentageSO = (actualAmountSO / monthlyPlanAmount) * 100;
//         frm.set_value('monthly_achieved_percentage_so', monthlyAchievedPercentageSO);
//     } else {
//         frappe.msgprint('Monthly Plan Amount cannot be zero.');
//     }

//     if (siMonthlyPlanAmount !== 0) {
//         let monthlyAchievedPercentageSI = (actualAmountSI / siMonthlyPlanAmount) * 100;
//         frm.set_value('monthly_achieved_percentage_si', monthlyAchievedPercentageSI);
//     } else {
//         frappe.msgprint('Sales Invoice Monthly Plan Amount cannot be zero.');
//     }

//     // Optionally, calculate and update total achieved percentage if needed
//     // let totalActualAmount = actualAmountSO + actualAmountSI;
//     // let totalPlanAmount = monthlyPlanAmount + siMonthlyPlanAmount;
//     // if (totalPlanAmount !== 0) {
//     //     let monthlyAchievedPercentageTotal = (totalActualAmount / totalPlanAmount) * 100;
//     //     frm.set_value('monthly_achieved_percentage_total', monthlyAchievedPercentageTotal);
//     // } else {
//     //     frappe.msgprint('Total Plan Amount cannot be zero.');
//     // }
// }
