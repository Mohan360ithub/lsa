import frappe
from datetime import date,datetime,timedelta,time


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

        cc_recipients=leave_approvers(leave_application.employee)["cc_recipients"]

        recipients = leave_application.custom_employee_mail_id
        subject = "Leave Application Submitted"
        message = f"Dear {leave_application.employee_name},<br><br>Your leave application from {leave_application.from_date} to {leave_application.to_date} has been submitted successfully. If you have any questions, please contact HR."
        
 
        # Send the email
        frappe.sendmail(
            recipients=recipients,
            cc=cc_recipients,
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

            cc_recipients=leave_approvers(leave_application_doc.employee)["cc_recipients"]
            
            subject = "Leave Application Cancelled"
            message = f"Dear {leave_application_doc.employee_name},<br><br>Your leave application from {leave_application_doc.from_date} to {leave_application_doc.to_date} has been cancelled. If you have any questions, please contact HR."
            
            recipients = leave_application_doc.custom_employee_mail_id
            
            leave_application_doc.status='Cancelled'
 
            # Send the email
            frappe.sendmail(
                recipients=recipients,
                cc=cc_recipients,
                subject=subject,
                message=message
            )
            leave_application_doc.save()
            
            return {'msg':"Cancelled Succesfully"}
    except Exception as e:
        frappe.msgprint(f'{e}')
        return {'msg':f'{e}'}
 
    # Mark the leave application as not applied
    # leave_application.db_set('leave_applied', 0)

#################################### Srikanths Code End ######################################

@frappe.whitelist()
def leave_action(name,approved_by):
    try:
        
        leave_application_doc = frappe.get_doc("Leave Application", name)
        if leave_application_doc!="Cancelled":
            user=frappe.get_doc("User",approved_by)

            cc_recipients=leave_approvers(leave_application_doc.employee)["cc_recipients"]
            
            subject = f"Leave Application {leave_application_doc.status}"
            message = f"Dear {leave_application_doc.employee_name},<br><br>Your leave application from {leave_application_doc.from_date} to {leave_application_doc.to_date} has been {leave_application_doc.status} by {user.full_name}. If you have any questions, please contact HR."
            
            recipients = leave_application_doc.custom_employee_mail_id
 
            # Send the email
            frappe.sendmail(
                recipients=recipients,
                cc=cc_recipients,
                subject=subject,
                message=message
            )
            
            return {"status":True,'msg':"Submitted Succesfully"}
    except Exception as e:
        # frappe.msgprint(f'{e}')
        return {"status":False,'msg':f'{e}'}


@frappe.whitelist()
def leave_approvers(emp_id):
    emp_doc = frappe.get_doc("Employee", emp_id)
    cc_recipients=set()
    admin_setting_doc = frappe.get_doc("Admin Settings")
    for i in admin_setting_doc.leave_application_mails:
        cc_recipients.add(i.user)

    global_leave_approvers=set()
    admin_setting_doc = frappe.get_doc("Admin Settings")
    for j in admin_setting_doc.global_leave_approver:
        global_leave_approvers.add(j.user)
    
    if emp_doc.user_id:
        if emp_doc.reports_to:
            reporting_manager_doc = frappe.get_doc("Employee", emp_doc.reports_to)
            if reporting_manager_doc.user_id:
                cc_recipients.add(reporting_manager_doc.user_id)
        if emp_doc.leave_approver:
            cc_recipients.add(emp_doc.leave_approver)
            global_leave_approvers.add(emp_doc.leave_approver)
    return {"cc_recipients":list(cc_recipients),"global_leave_approvers":list(global_leave_approvers)}

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




@frappe.whitelist()
def erp_last_checkin():
    usr=frappe.session.user
    emp_list = frappe.get_all("Employee", filters={"user_id":usr})
    if not emp_list:
        return {"status":False,"msg":f"No Employee found for {usr} user"}
    
    zero_am_time = datetime.combine(date.today(), time(0, 1))
    checkin_list = frappe.get_all("Employee Checkin",
                                    filters={"employee":emp_list[0].name},
                                    fields=["log_type","time"],
                                    order_by='time desc',
                                    limit=1)
    if checkin_list:
        dict_log={"IN":"OUT","OUT":"IN"}
        return {"status":True,"type":dict_log[checkin_list[0].log_type],"time":checkin_list[0].time}
    else:
        return {"status":False,"msg":"No Checkin-log found for"}

@frappe.whitelist()
def erp_checkin(location):
    usr=frappe.session.user
    emp_list = frappe.get_all("Employee", filters={"user_id":usr})
    if not emp_list:
        return {"status":False,"msg":f"No Employee found for {usr} user, you can't create checkin log"}
    try:
        zero_am_time = datetime.combine(date.today(), time(0, 1))
        checkin_list = frappe.get_all("Employee Checkin",
                                      filters={"employee":emp_list[0].name,"time":(">=",zero_am_time)},
                                      fields=["log_type"],
                                      order_by='time asc')
        if (not checkin_list or checkin_list[-1].log_type=="OUT") and location:
            log_type="IN"
            emp_id=emp_list[0].name
            return create_log(emp_id,location,log_type)
        elif checkin_list[-1].log_type=="IN":
            log_type="OUT"
            emp_id=emp_list[0].name
            return create_log(emp_id,location,log_type)
    except Exception as e:
        # frappe.msgprint(f'{e}')
        return {"status":False,'msg':f'{e}'}

def create_log(emp_id,location,log_type):
    try:
        emp_doc = frappe.get_doc("Employee", emp_id)
        checkin_log = frappe.new_doc('Employee Checkin')
        checkin_log.employee = emp_doc.name
        checkin_log.time = frappe.utils.now_datetime()
        checkin_log.log_type = log_type
        checkin_log.location = location
        checkin_log.shift = emp_doc.default_shift
        checkin_log.custom_marked_from_erp = 1
        # checkin_log.insert()
        return {"status":True,"msg":f"Employee checkin log created Successfully"}
    except Exception as e:
        # frappe.msgprint(f'{e}')
        return {"status":False,'msg':f'{e}'}


