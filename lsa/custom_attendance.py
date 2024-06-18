import frappe
from datetime import date,datetime,timedelta


@frappe.whitelist()
def checkin_out_for_missed_logs():
    today = date.today()
    #today = date(2024, 6, 15) 
    day = today.day
    month = today.month
    year = today.year

    from_datetime = datetime(year, month, day, 00, 00, 00)
    to_datetime = datetime(year, month, day, 23, 59, 59)
    
    check_logs= frappe.get_all("Employee Checkin",
                               filters={"time":("between",[from_datetime,to_datetime])},
                               fields=["employee","log_type","name"],
                               order_by="time",
                               )
    emp_checkins={}
    for log in check_logs:

        if log.employee not in emp_checkins:
            emp_checkins[log.employee]=[]
        emp_checkins[log.employee].append(log)
    for emp in emp_checkins:
        if emp_checkins[emp][-1].log_type !="OUT":
            last_in_log=frappe.get_doc("Employee Checkin",emp_checkins[emp][-1].name)
            one_minute = timedelta(minutes=1)
            out_time = last_in_log.time + one_minute

            checkin_doc = frappe.get_doc({
                                        "doctype": "Employee Checkin",
                                        "employee": last_in_log.employee,
                                        "log_type": "OUT",
                                        "time": out_time,
                                        "shift": last_in_log.shift,
                                        "location":last_in_log.location,
                                        "shift_start":last_in_log.shift_start,
                                        "shift_end":last_in_log.shift_end,
                                        "shift_actual_start":last_in_log.shift_actual_start,
                                        "shift_actual_end":last_in_log.shift_actual_end,
                                        "custom_automatically_marked_by_system":1,
                                    })
            checkin_doc.insert()

            frappe.db.commit()


    
    

#################################### Srikanths Code Start #############################################################
    
################## NEw code for sending mail for applied and cancelled leave ############################
@frappe.whitelist()
def apply_for_leave(name):
    try:
        leave_application = frappe.get_doc("Leave Application", name)
        
        subject = "Leave Application Submitted"
        message = f"Dear {leave_application.employee_name},<br><br>Your leave application from {leave_application.from_date} to {leave_application.to_date} has been submitted successfully. If you have any questions, please contact HR."
        
        recipients = leave_application.custom_employee_mail_id
 
        # Send the email
        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message
        )
    except Exception as e:
        frappe.msgprint(f'{e}')
    # Mark the leave application as applied
    # leave_application.db_set('leave_applied', 1)
 
@frappe.whitelist()
def cancel_leave(name):
    try:
        
        leave_application_doc = frappe.get_doc("Leave Application", name)
        if leave_application_doc!="Cancelled":
            user=frappe.session.user
            # frappe.set_user("Administrator")
            
            subject = "Leave Application Cancelled"
            message = f"Dear {leave_application_doc.employee_name},<br><br>Your leave application from {leave_application_doc.from_date} to {leave_application_doc.to_date} has been cancelled. If you have any questions, please contact HR."
            
            recipients = leave_application_doc.custom_employee_mail_id
            
            leave_application_doc.status='Cancelled'
 
            # Send the email
            frappe.sendmail(
                recipients=recipients,
                subject=subject,
                message=message
            )
            leave_application_doc.save()
            # frappe.set_user(user)
            
            return {'msg':"Cancelled Succesfully"}
    except Exception as e:
        frappe.msgprint(f'{e}')
        return {'msg':f'{e}'}
 
    # Mark the leave application as not applied
    # leave_application.db_set('leave_applied', 0)

    
#################################### Srikanths Code End ######################################

# #################################### Srikanths Code Modified by Vatsal Start #############################################################
    
# ################## NEw code for sending mail for applied and cancelled leave ############################
# import frappe
# from frappe.core.doctype.communication.email import make
 
# @frappe.whitelist()
# def apply_for_leave(leave_app_id):
#     try:

#         leave_application_doc = frappe.get_doc("Leave Application", leave_app_id)
#         emp_doc = frappe.get_doc("Employee", leave_application_doc.employee)

#         cc_recipients=set()

#         # admin_setting_doc = frappe.get_doc("Admin Settings")
#         # for i in admin_setting_doc.leave_application_mails:
#         #     cc_recipients.add(i.user)
        
#         subject = f"Leave Application {leave_application_doc.name} Submitted"
#         message = f"Dear {leave_application_doc.employee_name},<br><br>Your leave application from {leave_application_doc.from_date} to {leave_application.to_date} has been submitted successfully. If you have any questions, please contact HR."
        
#         if emp_doc.user_id:
#             recipients=(emp_doc.user_id)
#             if emp_doc.reports_to:
#                 reporting_manager_doc = frappe.get_doc("Employee", emp_doc.reports_to)
#                 if reporting_manager_doc.user_id:
#                     cc_recipients.add(reporting_manager_doc.user_id)
#             if emp_doc.leave_approver:
#                 cc_recipients.add(emp_doc.leave_approver)
    
#             # Send the email
#             frappe.sendmail(
#                 recipients=recipients,
#                 cc=list(cc_recipients),
#                 subject=subject,
#                 message=message
#             )
#             return {"status": True, "msg":"Applied for Leave Successfully!!!"}
#         else:
#             return {"status": False, "msg":"Employee not linked with any User"}
#     except Exception as e:
#         # frappe.msgprint(f'{e}')
#         return {"status": False, "msg":f"Error Applying for Leave: {e}"}
 
# @frappe.whitelist()
# def cancel_leave(leave_app_id):
#     try:
        
#         leave_application_doc = frappe.get_doc("Leave Application", leave_app_id)
#         if leave_application_doc.status!="Cancelled":
#             emp_doc = frappe.get_doc("Employee", leave_application_doc.employee)

#             cc_recipients=set()

#             # admin_setting_doc = frappe.get_doc("Admin Settings")
#             # for i in admin_setting_doc.leave_application_mails:
#             #     cc_recipients.add(i.user)

#             if emp_doc.user_id:
#                 recipients=(emp_doc.user_id)
#                 if emp_doc.reports_to:
#                     reporting_manager_doc = frappe.get_doc("Employee", emp_doc.reports_to)
#                     if reporting_manager_doc.user_id:
#                         cc_recipients.add(reporting_manager_doc.user_id)
#                 if emp_doc.leave_approver:
#                     cc_recipients.add(emp_doc.leave_approver)
            
#                 subject = "Leave Application Cancelled"
#                 message = f"Dear {leave_application_doc.employee_name},<br><br>Your leave application from {leave_application_doc.from_date} to {leave_application_doc.to_date} has been cancelled. If you have any questions, please contact HR."
                

                
#                 leave_application_doc.status='Cancelled'
    
#                 # Send the email
#                 frappe.sendmail(
#                     recipients=recipients,
#                     cc=list(cc_recipients),
#                     subject=subject,
#                     message=message
#                 )
#                 leave_application_doc.save()
#                 # frappe.set_user(user)
#                 return {"status": True, "msg":"Leave Cancelled Successfully!!!"}
#             else:
#                 return {"status": False, "msg":"Employee not linked with any User"}
#         else:
#             return {"status": False, "msg":f"Leave already Cancelled"}
#     except Exception as e:
#         # frappe.msgprint(f'{e}')
#         return {"status": False, "msg":f"Error Cancelling the Leave: {e}"}

# #################################### Srikanths Code Modified by Vatsal End ##################################################

