import frappe
from frappe import _
from datetime import datetime, timedelta, date
from frappe.utils import now_datetime




@frappe.whitelist()
def get_employees_with_absent():

    cur_month = frappe.utils.now_datetime().month

    # Fetch employees with birthdays in the current month
    employees = frappe.get_all("Employee", 
                                   filters={"status":"Active"}, 
                                   fields=["name","employee_name","company","designation","department"])
    if employees:
        employees_dict = {}
        for emp in employees:
            employees_dict[emp.name] = emp.employee_name
        
        today = date.today()
        # today = datetime.strptime("2024-05-15", "%Y-%m-%d")


        # Calculate the start date of the current month
        start_date = date(today.year, today.month, 1)

        # Calculate the end date of the current month
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)


        leave_applications = frappe.get_all("Leave Application",
                                             filters={
                                                      "from_date": ("between", [str(start_date), str(end_date)]),
                                                      },
                                             fields=["name", "from_date", "to_date", "employee","status"])
        

        # Initialize the dictionary
        leave_dict = {}

        # Iterate over each leave application
        for leave in leave_applications:
            # from_date = datetime.strptime(str(leave["from_date"]), "%Y-%m-%d")
            # to_date = datetime.strptime(str(leave["to_date"]), "%Y-%m-%d")
            from_date = leave.from_date
            to_date = leave.to_date
            employee = leave["employee"]
            status = leave["status"]
            
            # Generate key-value pairs for each day in the leave application range
            current_date = from_date
            while current_date <= to_date or current_date<=to_date:
                leave_dict[(current_date, employee)] = status
                current_date += timedelta(days=1)
        
        absent_date = frappe.get_all("Attendance",
                                     filters={"docstatus": 1,
                                              "status": "Absent",
                                              "attendance_date": ("between", [str(start_date), str(end_date)]),
                                              },
                                     fields=["name", "attendance_date", "employee","working_hours"],
                                     order_by="attendance_date desc")
        absent_data = {}
        for ab_date in absent_date:
            absent_date_checkin = frappe.get_all("Employee Checkin",
                                     filters={"attendance": ab_date.name},
                                     fields=["name", "time", "log_type","custom_automatically_marked_by_system"],
                                     order_by="time asc")

            if str(ab_date.attendance_date) not in absent_data:
                absent_data[str(ab_date.attendance_date)] = []



            if (ab_date.attendance_date,ab_date.employee) in leave_dict:
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Applied for leave but not approved"])
            elif absent_date_checkin and (len(absent_date_checkin)%2 != 0 or absent_date_checkin[0].log_type == "OUT"):
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Mismatch in Checkins"])
            elif absent_date_checkin :
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Short working hours"])
            else:
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Need to apply for Leave"])

        return absent_data
    return None





###########Srikanth's Code####################################################################
 
@frappe.whitelist()
def get_approved_leave_applications():
    current_date = now_datetime().date()  # Get the current date in YYYY-MM-DD format
    leave_applications = frappe.get_all(
        'Leave Application',
        filters={
            'status': 'Approved',
            'to_date': ['>=', current_date]  # Filter to get only to_date greater than or equal to current date
        },
        fields=['employee_name', 'from_date', 'to_date', 'total_leave_days','name']
    )
    
    return leave_applications
 
 
@frappe.whitelist()
def get_notapproved_leave_applications():
    current_date = now_datetime().date()  # Get the current date in YYYY-MM-DD format
    leave_applications = frappe.get_all(
        'Leave Application',
        filters={
            'status': 'Open'
            # 'to_date': ['>=', current_date]  # Filter to get only to_date greater than or equal to current date
        },
        fields=['employee_name','posting_date','from_date', 'to_date', 'total_leave_days','name']
    )
 
    
    return leave_applications

###################################################################################

