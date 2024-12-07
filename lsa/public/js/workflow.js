// class workflowOverride extends frappe.ui.form.States {
//     show_actions() {
//         var added = false;
//         var me = this;

//         // if the loaded doc is dirty, don't show workflow buttons
//         if (this.frm.doc.__unsaved === 1) {
//             return;
//         }

//         function has_approval_access(transition) {
//             let approval_access = false;
//             const user = frappe.session.user;
//             if (
//                 user === "Administrator" ||
//                 transition.allow_self_approval ||
//                 user !== me.frm.doc.owner
//             ) {
//                 approval_access = true;
//             }
//             return approval_access;
//         }

//         frappe.workflow.get_transitions(this.frm.doc).then((transitions) => {
//             this.frm.page.clear_actions_menu();
//             transitions.forEach((d) => {
//                 if (frappe.user_roles.includes(d.allowed) && has_approval_access(d)) {
//                     added = true;
//                     me.frm.page.add_action_item(__(d.action), function () {
//                         console.log(me.frm.doc);
//                         // Check if the workflow is "Gst Filling Data"
//                         if (me.frm.doc.doctype === "Gst Filling Data") {
//                             frappe.confirm(
//                                 __("Are you sure you want to proceed with this action for Gst Filling Data?"),
//                                 function () {
//                                     // User confirmed
//                                     me.show_duration_prompt(d);
//                                 },
//                                 function () {
//                                     // User cancelled, do nothing
//                                     console.log("Workflow action cancelled by the user.");
//                                 }
//                             );
//                         } else {
//                             // For other workflows, directly proceed without confirmation
//                             me.apply_workflow_action(d);
//                         }
//                     });
//                 }
//             });

//             this.setup_btn(added);
//         });
//     }

//     show_duration_prompt(transition) {
//         var me = this;

//         // Store the old filing_status before workflow action
//         const old_status = me.frm.doc.filing_status;

//         frappe.prompt(
//             [
//                 {
//                     label: 'Hours',
//                     fieldname: 'hours',
//                     fieldtype: 'Int',
//                     reqd: 0
//                 },
//                 {
//                     fieldtype: 'Column Break'
//                 },
//                 {
//                     label: 'Minutes',
//                     fieldname: 'minutes',
//                     fieldtype: 'Int',
//                     reqd: 0
//                 }
//             ],
//             function (values) {
//                 // Validate the duration input
//                 const hours = values.hours || 0;
//                 const minutes = values.minutes || 0;

//                 if (hours === 0 && minutes === 0) {
//                     frappe.throw(__('You must provide a valid duration.'));
//                     return;
//                 }

//                 // Format the duration
//                 const formatted_duration = `${hours}h ${minutes}m`;

//                 // Apply workflow action first
//                 me.apply_workflow_action(transition).then(() => {
//                     // Append to the child table after workflow action
//                     const new_status = me.frm.doc.filing_status;

//                     me.frm.add_child("status_change_history", {
//                         old_status: old_status,
//                         new_status: new_status,
//                         changed_by: frappe.session.user,
//                         updated_at: frappe.datetime.now_datetime(),
//                         duration: formatted_duration
//                     });

//                     // Save the document with updated child table
//                     me.frm.save().then(() => {
//                         frappe.msgprint(__('Filing status updated successfully.'));
//                         me.frm.refresh();
//                     });
//                 });
//             },
//             __("Enter Duration"),
//             __("Submit")
//         );
//     }

//     apply_workflow_action(transition) {
//         var me = this;

//         return new Promise((resolve, reject) => {
//             frappe.dom.freeze();
//             me.frm.selected_workflow_action = transition.action;

//             me.frm.script_manager.trigger("before_workflow_action").then(() => {
//                 frappe
//                     .xcall("frappe.model.workflow.apply_workflow", {
//                         doc: me.frm.doc,
//                         action: transition.action
//                     })
//                     .then((doc) => {
//                         frappe.model.sync(doc);
//                         me.frm.refresh();
//                         me.frm.selected_workflow_action = null;
//                         me.frm.script_manager.trigger("after_workflow_action");
//                         resolve();
//                     })
//                     .catch((error) => {
//                         console.error(error);
//                         reject(error);
//                     })
//                     .finally(() => {
//                         frappe.dom.unfreeze();
//                     });
//             });
//         });
//     }
// }

// frappe.ui.form.States = workflowOverride;








class workflowOverride extends frappe.ui.form.States {
    show_actions() {
        var added = false;
        var me = this;

        // if the loaded doc is dirty, don't show workflow buttons
        if (this.frm.doc.__unsaved === 1) {
            return;
        }

        function has_approval_access(transition) {
            let approval_access = false;
            const user = frappe.session.user;
            if (
                user === "Administrator" ||
                transition.allow_self_approval ||
                user !== me.frm.doc.owner
            ) {
                approval_access = true;
            }
            return approval_access;
        }

        frappe.workflow.get_transitions(this.frm.doc).then((transitions) => {
            this.frm.page.clear_actions_menu();
            transitions.forEach((d) => {
                if (frappe.user_roles.includes(d.allowed) && has_approval_access(d)) {
                    added = true;
                    me.frm.page.add_action_item(__(d.action), function () {
                        console.log(me.frm.doc);
                        // Check if the workflow is "Gst Filling Data"
                        if (me.frm.doc.doctype === "Gst Filling Data") {
                            frappe.confirm(
                                __("Are you sure you want to proceed with this action for Gst Filling Data?"),
                                function () {
                                    // User confirmed
                                    if (["Back", "Reset"].includes(d.action)) {
                                        me.show_reason_prompt(d);
                                    } else {
                                        me.show_duration_prompt(d);
                                    }
                                },
                                function () {
                                    // User cancelled, do nothing
                                    console.log("Workflow action cancelled by the user.");
                                }
                            );
                        } else {
                            // For other workflows, directly proceed without confirmation
                            me.apply_workflow_action(d);
                        }
                    });
                }
            });

            this.setup_btn(added);
        });
    }

    show_duration_prompt(transition) {
        var me = this;

        // Store the old filing_status before workflow action
        const old_status = me.frm.doc.filing_status;

        frappe.prompt(
            [
                {
                    label: 'Hours',
                    fieldname: 'hours',
                    fieldtype: 'Int',
                    reqd: 0
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    label: 'Minutes',
                    fieldname: 'minutes',
                    fieldtype: 'Int',
                    reqd: 0
                }
            ],
            function (values) {
                // Validate the duration input
                const hours = values.hours || 0;
                const minutes = values.minutes || 0;

                if (hours === 0 && minutes === 0) {
                    frappe.throw(__('You must provide a valid duration.'));
                    return;
                }

                // Format the duration
                const formatted_duration = `${hours}h ${minutes}m`;

                // Apply workflow action first
                me.apply_workflow_action(transition).then(() => {
                    // Append to the child table after workflow action
                    const new_status = me.frm.doc.filing_status;

                    me.frm.add_child("status_change_history", {
                        old_status: old_status,
                        new_status: new_status,
                        changed_by: frappe.session.user,
                        updated_at: frappe.datetime.now_datetime(),
                        duration: formatted_duration
                    });

                    // Save the document with updated child table
                    me.frm.save().then(() => {
                        frappe.msgprint(__('Filing status updated successfully.'));
                        me.frm.refresh();
                    });
                });
            },
            __("Enter Duration"),
            __("Submit")
        );
    }

    show_reason_prompt(transition) {
        var me = this;

        // Store the old filing_status before workflow action
        const old_status = me.frm.doc.filing_status;

        frappe.prompt(
            [
                {
                    label: 'Reason',
                    fieldname: 'reason',
                    fieldtype: 'Small Text',
                    reqd: 1
                }
            ],
            function (values) {
                const reason = values.reason;

                // Apply workflow action first
                me.apply_workflow_action(transition).then(() => {
                    // Append to the child table after workflow action
                    const new_status = me.frm.doc.filing_status;

                    me.frm.add_child("status_change_history", {
                        old_status: old_status,
                        new_status: new_status,
                        changed_by: frappe.session.user,
                        updated_at: frappe.datetime.now_datetime(),
                        reason: reason
                    });

                    // Save the document with updated child table
                    me.frm.save().then(() => {
                        frappe.msgprint(__('Filing status updated successfully.'));
                        me.frm.refresh();
                    });
                });
            },
            __("Enter Reason"),
            __("Submit")
        );
    }

    apply_workflow_action(transition) {
        var me = this;

        return new Promise((resolve, reject) => {
            frappe.dom.freeze();
            me.frm.selected_workflow_action = transition.action;

            me.frm.script_manager.trigger("before_workflow_action").then(() => {
                frappe
                    .xcall("frappe.model.workflow.apply_workflow", {
                        doc: me.frm.doc,
                        action: transition.action
                    })
                    .then((doc) => {
                        frappe.model.sync(doc);
                        me.frm.refresh();
                        me.frm.selected_workflow_action = null;
                        me.frm.script_manager.trigger("after_workflow_action");
                        resolve();
                    })
                    .catch((error) => {
                        console.error(error);
                        reject(error);
                    })
                    .finally(() => {
                        frappe.dom.unfreeze();
                    });
            });
        });
    }
}

frappe.ui.form.States = workflowOverride;
