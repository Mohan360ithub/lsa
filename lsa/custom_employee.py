import frappe
import requests
from frappe import _
from frappe.utils import today,add_days, cint, flt, getdate,get_first_day,get_last_day
from datetime import datetime, timedelta, date
from hrms.hr.doctype.leave_allocation.leave_allocation import get_previous_allocation
from hrms.hr.doctype.leave_application.leave_application import (get_leave_balance_on,get_leaves_for_period,)
from itertools import groupby
from frappe.utils import now_datetime




@frappe.whitelist()
def checking_user_authentication(user_email=None):  
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["HR Manager","HR User","LSA CEO Admin","LSA CEO ADMIN TEAM","Lsa HR"]

        for role in roles:
            if role in doc_perm_roles:
                status = True
                break
        user_emp_id=None
        if status==False:
            user_emp = frappe.get_all('Employee', filters={'user_id': user_email})
            if user_emp:
                user_emp_id=user_emp[0].name

        return {"status": status, "value": [roles,user_emp_id]}

    except Exception as e:
        #print(e)
        return {"status": "Failed"}
    



@frappe.whitelist()
def get_employees_with_birthday_in_current_month():
    current_date = now_datetime().date()
    one_week_before = current_date - timedelta(days=7)
    one_week_after = current_date + timedelta(days=7)

    # Fetch employees with birthdays and custom anniversary dates
    employees = frappe.get_all("Employee",
        filters={
            "status": "Active",
        },
        fields=["name", "employee_name", "date_of_birth", "custom_anniversary_date","date_of_joining"],
    )

    curr_mon = {}
    for emp in employees:
        if emp.date_of_birth:
            dob_this_year = emp.date_of_birth.replace(year=current_date.year)
            if one_week_before <= dob_this_year <= one_week_after:
                date_key = emp.date_of_birth.strftime("%m-%d")
                if date_key in curr_mon:
                    curr_mon[date_key].append((emp.employee_name, "birthday"))
                else:
                    curr_mon[date_key] = [(emp.employee_name, "birthday")]

        if emp.custom_anniversary_date:
            anniv_this_year = emp.custom_anniversary_date.replace(year=current_date.year)
            if one_week_before <= anniv_this_year <= one_week_after:
                date_key = emp.custom_anniversary_date.strftime("%m-%d")
                if date_key in curr_mon:
                    curr_mon[date_key].append((emp.employee_name, "anniversary"))
                else:
                    curr_mon[date_key] = [(emp.employee_name, "anniversary")]
        
        if emp.date_of_joining:
            anniv_this_year = emp.date_of_joining.replace(year=current_date.year)
            if one_week_before <= anniv_this_year <= one_week_after:
                date_key = emp.date_of_joining.strftime("%m-%d")
                if date_key in curr_mon:
                    curr_mon[date_key].append((emp.employee_name, "joining"))
                else:
                    curr_mon[date_key] = [(emp.employee_name, "joining")]

    sorted_curr_mon = {key: curr_mon[key] for key in sorted(curr_mon)}
    return sorted_curr_mon



def get_employee_for_user():
    current_user = frappe.session.user
    employee = frappe.get_all("Employee", 
                                   filters={"user_id": current_user,"status":"Active"}, 
                                   fields=["name","employee_name","company","designation","department"])
    # print(employee)
    if employee:
         return employee
    return None


# @frappe.whitelist()
# def get_leave_data():
#     today = datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d")
#     year = today.year
#     from_date = datetime(year, 1, 1)
#     to_date = datetime(year, 12, 31 )

#     # leave_types = get_leave_types()
#     leave_types = ['Leave Without Pay', 'Compensatory Off',  'Privilege Leave', 'Sick Leave', 'Special Leave']

#     active_employees = get_employee_for_user()

#     precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
#     # consolidate_leave_types = len(active_employees) > 1 and filters.consolidate_leave_types
#     row = None


@frappe.whitelist()
def get_leave_data():
    today = datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d")
    year = today.year
    from_date = datetime(year, 1, 1)
    to_date = datetime(year, 12, 31 )

    active_employees = get_employee_for_user()
    return get_employee_leave_data(active_employees,to_date,from_date)


def get_employee_leave_data(active_employees,to_date,from_date):
    
    precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
    # consolidate_leave_types = len(active_employees) > 1 and filters.consolidate_leave_types
    leave_types = ['Leave Without Pay', 'Compensatory Off',  'Privilege Leave', 'Sick Leave', 'Special Leave']
    row = None

    data = []

    data = []
    if active_employees:
        for leave_type in leave_types:
            
            row = frappe._dict({"leave_type": leave_type})

            for employee in active_employees:
                row = frappe._dict({"leave_type": leave_type})

                row.employee = employee.name
                row.employee_name = employee.employee_name

                leaves_taken = (
                    get_leaves_for_period(employee.name, leave_type, from_date, to_date) * -1
                )

                new_allocation, expired_leaves, carry_forwarded_leaves = get_allocated_and_expired_leaves(
                    from_date, to_date, employee.name, leave_type
                )
                opening = get_opening_balance(employee.name, leave_type, from_date, carry_forwarded_leaves)

                row.leaves_allocated = flt(new_allocation, precision)
                row.leaves_expired = flt(expired_leaves, precision)
                row.opening_balance = flt(opening, precision)
                row.leaves_taken = flt(leaves_taken, precision)

                closing = new_allocation + opening - (row.leaves_expired + leaves_taken)
                row.closing_balance = flt(closing, precision)
                if leave_type=="Leave Without Pay":
                    row.closing_balance = 0

                row.indent = 1
                data.append(row)

    return data



def get_leave_types() -> list[str]:
	LeaveType = frappe.qb.DocType("Leave Type")
	return (frappe.qb.from_(LeaveType).select(LeaveType.name).orderby(LeaveType.name)).run(
		pluck="name"
	)


def get_opening_balance(
	employee: str, leave_type: str, from_date, carry_forwarded_leaves: float
) -> float:
	# allocation boundary condition
	# opening balance is the closing leave balance 1 day before the filter start date
	opening_balance_date = add_days(from_date, -1)
	allocation = get_previous_allocation(from_date, leave_type, employee)

	if (
		allocation
		and allocation.get("to_date")
		and opening_balance_date
		and getdate(allocation.get("to_date")) == getdate(opening_balance_date)
	):
		# if opening balance date is same as the previous allocation's expiry
		# then opening balance should only consider carry forwarded leaves
		opening_balance = carry_forwarded_leaves
	else:
		# else directly get leave balance on the previous day
		opening_balance = get_leave_balance_on(employee, leave_type, opening_balance_date)

	return opening_balance


def get_allocated_and_expired_leaves(
	from_date: str, to_date: str, employee: str, leave_type: str
) -> tuple[float, float, float]:
	new_allocation = 0
	expired_leaves = 0
	carry_forwarded_leaves = 0

	records = get_leave_ledger_entries(from_date, to_date, employee, leave_type)

	for record in records:
		# new allocation records with `is_expired=1` are created when leave expires
		# these new records should not be considered, else it leads to negative leave balance
		if record.is_expired:
			continue

		if record.to_date < getdate(to_date):
			# leave allocations ending before to_date, reduce leaves taken within that period
			# since they are already used, they won't expire
			expired_leaves += record.leaves
			leaves_for_period = get_leaves_for_period(
				employee, leave_type, record.from_date, record.to_date
			)
			expired_leaves -= min(abs(leaves_for_period), record.leaves)

		if record.from_date >= getdate(from_date):
			if record.is_carry_forward:
				carry_forwarded_leaves += record.leaves
			else:
				new_allocation += record.leaves

	return new_allocation, expired_leaves, carry_forwarded_leaves


def get_leave_ledger_entries(
	from_date: str, to_date: str, employee: str, leave_type: str
) -> list[dict]:
	ledger = frappe.qb.DocType("Leave Ledger Entry")
	return (
		frappe.qb.from_(ledger)
		.select(
			ledger.employee,
			ledger.leave_type,
			ledger.from_date,
			ledger.to_date,
			ledger.leaves,
			ledger.transaction_name,
			ledger.transaction_type,
			ledger.is_carry_forward,
			ledger.is_expired,
		)
		.where(
			(ledger.docstatus == 1)
			& (ledger.transaction_type == "Leave Allocation")
			& (ledger.employee == employee)
			& (ledger.leave_type == leave_type)
			& (
				(ledger.from_date[from_date:to_date])
				| (ledger.to_date[from_date:to_date])
				| ((ledger.from_date < from_date) & (ledger.to_date > to_date))
			)
		)
	).run(as_dict=True)




# @frappe.whitelist()
# def get_employees_with_absent():
#     cur_month = frappe.utils.now_datetime().month


#     # Fetch employees with birthdays in the current month
#     employee = get_employee_for_user()
#     if employee:
#         today = date.today()

#         # Calculate the start date of the current month
#         start_date = date(today.year, today.month, 1)

#         # Calculate the end date of the current month
#         if today.month == 12:
#             end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
#         else:
#             end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
#         absent_date = frappe.get_all("Attendance",
#                                     filters={"docstatus":1,
#                                             "status":"Absent",
#                                             "attendance_date":("between",[str(start_date),str(end_date)]),
#                                             "employee":employee[0].name,
#                                             },
#                                     fields=["name","attendance_date"])
#         absent_data={}
#         for ab_date in absent_date:
#             absent_date_checkin = frappe.get_all("Employee Checkin",
#                                     filters={"attendance":ab_date.name,
#                                             "employee":employee[0].name,
#                                             },
#                                     fields=["name","time","log_type"]
#                                             )
#             if absent_date_checkin:
#                 absent_data[str(ab_date.attendance_date)]=absent_date_checkin
#             else:
#                 absent_data[str(ab_date.attendance_date)]=[]
            

#         print(absent_data)
#         return absent_data
#     return None

########################################### Srikanth Code Modification of get_employees_with_absent functionStart ################################################################

@frappe.whitelist()
def get_employees_with_absent():
    cur_month = frappe.utils.now_datetime().month
    # Fetch all employee data
    usr=frappe.session.user
    emp_data = frappe.get_all('Employee', filters={"user_id":usr}, fields=['name', 'employee_name','user_id'])
    reg_req_date={}
    # Iterate over each employee to check for absences
    for emp in emp_data:
        emp_name = emp.name
        emp_mail = emp.user_id
        # Fetch attendance regularization requests for the employee
        attendance_regularization = frappe.get_all(
            "Team Ticket",
            filters={
                # "employee": emp_name,
                "created_by": emp_mail,
        
            },
            fields=["regularization_date","name","created_by"]
        )

        
        # Check if there are any requests for the employee
        if attendance_regularization:
            for request in attendance_regularization:
                date_value=(request.regularization_date)
                reg_req_date[date_value]= request.name
    
    # Fetch employees with birthdays in the current month
    employees = get_employee_for_user()
    if employees:
        employees_dict = {}
        for emp in employees:
            employees_dict[emp.name] = emp.employee_name       
        today = date.today()

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
                                                      "employee":employees[0].name,
                                                      },
                                             fields=["name", "from_date", "to_date", "employee","status"])
        # Initialize the dictionary
        leave_dict = {}

        # Iterate over each leave application
        for leave in leave_applications:
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
                                              "employee":employees[0].name,
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


            regularization_exists = None
            if (ab_date.attendance_date,ab_date.employee) in leave_dict:
                
                # if (ab_date.attendance_date) in reg_req_date:
                #     regularization_exists=reg_req_date[ab_date.attendance_date]

                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Applied for leave but not approved"])
            elif absent_date_checkin and (len(absent_date_checkin)%2 != 0 or absent_date_checkin[0].log_type == "OUT"):
                
                if (ab_date.attendance_date) in reg_req_date:
                     regularization_exists=reg_req_date[ab_date.attendance_date]
                     
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Mismatch in Checkins",regularization_exists])
            elif absent_date_checkin :
                
                if (ab_date.attendance_date) in reg_req_date:
                    regularization_exists=reg_req_date[ab_date.attendance_date]
                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Short working hours",regularization_exists])
            else:
               
               
                if (ab_date.attendance_date) in reg_req_date:
                     regularization_exists=reg_req_date[ab_date.attendance_date]

                absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Need to apply for Leave",regularization_exists])

        return absent_data
    return None
########################################### Srikanth Code Start ################################################################

# @frappe.whitelist()
# def get_employees_with_absent():

#     cur_month = frappe.utils.now_datetime().month

#     # Fetch employees with birthdays in the current month
#     employees = get_employee_for_user()
#     if employees:
#         employees_dict = {}
#         for emp in employees:
#             employees_dict[emp.name] = emp.employee_name
        
#         today = date.today()
#         # today = datetime.strptime("2024-05-15", "%Y-%m-%d")


#         # Calculate the start date of the current month
#         start_date = date(today.year, today.month, 1)

#         # Calculate the end date of the current month
#         if today.month == 12:
#             end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
#         else:
#             end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)


#         leave_applications = frappe.get_all("Leave Application",
#                                              filters={
#                                                       "from_date": ("between", [str(start_date), str(end_date)]),
#                                                       "employee":employees[0].name,
#                                                       },
#                                              fields=["name", "from_date", "to_date", "employee","status"])
        

#         # Initialize the dictionary
#         leave_dict = {}

#         # Iterate over each leave application
#         for leave in leave_applications:
#             # from_date = datetime.strptime(str(leave["from_date"]), "%Y-%m-%d")
#             # to_date = datetime.strptime(str(leave["to_date"]), "%Y-%m-%d")
#             from_date = leave.from_date
#             to_date = leave.to_date
#             employee = leave["employee"]
#             status = leave["status"]
            
#             # Generate key-value pairs for each day in the leave application range
#             current_date = from_date
#             while current_date <= to_date or current_date<=to_date:
#                 leave_dict[(current_date, employee)] = status
#                 current_date += timedelta(days=1)
        
#         absent_date = frappe.get_all("Attendance",
#                                      filters={"docstatus": 1,
#                                               "status": "Absent",
#                                               "employee":employees[0].name,
#                                               "attendance_date": ("between", [str(start_date), str(end_date)]),
#                                               },
#                                      fields=["name", "attendance_date", "employee","working_hours"],
#                                      order_by="attendance_date desc")
#         absent_data = {}
#         for ab_date in absent_date:
#             absent_date_checkin = frappe.get_all("Employee Checkin",
#                                      filters={"attendance": ab_date.name},
#                                      fields=["name", "time", "log_type","custom_automatically_marked_by_system"],
#                                      order_by="time asc")

#             if str(ab_date.attendance_date) not in absent_data:
#                 absent_data[str(ab_date.attendance_date)] = []



#             if (ab_date.attendance_date,ab_date.employee) in leave_dict:
#                 absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Applied for leave but not approved"])
#             elif absent_date_checkin and (len(absent_date_checkin)%2 != 0 or absent_date_checkin[0].log_type == "OUT"):
#                 absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Mismatch in Checkins"])
#             elif absent_date_checkin :
#                 absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], True, absent_date_checkin,ab_date.working_hours,"Short working hours"])
#             else:
#                 absent_data[str(ab_date.attendance_date)].append([employees_dict[ab_date.employee], False, absent_date_checkin,ab_date.working_hours,"Need to apply for Leave"])

#         return absent_data
#     return None



@frappe.whitelist()
def get_employees_present_today():
    # Get today's date
    today_date = today()
    
    # Fetch all check-ins and check-outs for today, ordered by time
    checkins = frappe.get_all('Employee Checkin', 
                              filters={'time': ['>=', today_date]},
                              fields=['employee', 'employee_name', 'time', 'log_type'],
                              order_by='time')
    
    # Process the logs to get the first IN and the last OUT for each employee
    employee_logs = {}
    for checkin in checkins:
        employee = checkin['employee']
        if employee not in employee_logs:
            employee_logs[employee] = {'employee_name': checkin['employee_name'], 'first_in': None, 'last_out': None}
        
        if checkin['log_type'] == 'IN' and employee_logs[employee]['first_in'] is None:
            employee_logs[employee]['first_in'] = checkin['time']
        employee_logs[employee]['last_log'] = checkin['log_type']
        if checkin['log_type'] == 'OUT':
            employee_logs[employee]['last_out'] = checkin['time']
    
    # Prepare the final list
    result = []
    for employee, logs in employee_logs.items():
        last_out = logs['last_out'] if logs.get('last_log') == 'OUT' else None
        result.append({
            'employee': employee,
            'employee_name': logs['employee_name'],
            'first_in': logs['first_in'],
            'last_out': last_out
        })
    
    return result




@frappe.whitelist()
def get_notapproved_leave_applications_for_approver():

    usr=frappe.session.user
    # leave_applications = frappe.get_all(
    #     'Leave Application',
    #     filters={
    #         'status': 'Open',
    #         "leave_approver":usr,
    #         # 'to_date': ['>=', current_date]  # Filter to get only to_date greater than or equal to current date
    #     },
    #     fields=['employee_name','posting_date','from_date', 'to_date', 'total_leave_days','name']
    # )

    leave_applications = frappe.get_all(
        'Leave Application',
        filters={
            'docstatus': 0,
            "leave_approver":usr,
            # 'to_date': ['>=', current_date]  # Filter to get only to_date greater than or equal to current date
        },
        fields=['employee_name','posting_date','from_date', 'to_date', 'total_leave_days','name']
    )
 
    
    return leave_applications

###################################################################################


@frappe.whitelist()
def update_appraisal(employee, updated_ctc, from_date, remark, sal_structure,appraisal_cycle):
    # try:
        # Get the employee document
        employee_doc = frappe.get_doc('Employee', employee)
        
        new_appraisal_record = employee_doc.append('custom_appraisal_table', {})
        new_appraisal_record.from_date = from_date
        new_appraisal_record.date = date.today()
        new_appraisal_record.ctc = updated_ctc
        new_appraisal_record.old_ctc = employee_doc.ctc
        new_appraisal_record.remark = remark
        new_appraisal_record.created_by = frappe.session.user
        new_appraisal_record.appraisal_cycle = appraisal_cycle
        new_appraisal_record.salary_structure = sal_structure
        if employee_doc.ctc:
            new_appraisal_record.increment = round((float(updated_ctc) - employee_doc.ctc) / employee_doc.ctc * 100, 1)
        
        
        appraisal_cycle_validation = frappe.get_all('Appraisal Cycle',
                                                    filters={"name":appraisal_cycle,
                                                    "start_date":("<=",from_date),
                                                    "end_date":(">=",from_date),},
                                                    fields=["name","start_date","end_date"])
        appraisal_cycle_validation = [ap_cy.name for ap_cy in appraisal_cycle_validation]
        if appraisal_cycle not in appraisal_cycle_validation:
             frappe.throw("Invalid from date {from_date} for Appraisal cycle {appraisal_cycle}")
             

        appraisal_assignment = frappe.get_all('Appraisal',
                                              filters={"employee":employee_doc.name,
                                                       "docstatus":0},
                                                )
        if appraisal_assignment:
             return {
                    "status": False,
                    "msg": "An Open Appraisal already present for the Employee"
                }
            # Log the appraisal details
        appraisal_assignment = frappe.get_doc({
            'doctype': 'Appraisal',
            'employee': employee_doc.name,
            'appraisal_cycle': appraisal_cycle,
            "company":"LOKESH SANKHALA AND ASSOCIATES",
            "appraisal_template":"LSA Appraisal Template",
        })
        appraisal_assignment.insert()
        employee_doc.save()
    
        return {
            "status": True,
            "msg": "Appraisal created, pending for Approval"
        }

    # except Exception as e:
    #     # Log the error
    #     frappe.log_error(message=str(e), title="Failed to add Appraisal record")
        
    #     return {
    #         "status": False,
    #         "msg": f"Failed to add Appraisal record: {str(e)}"
    #     }

@frappe.whitelist()
def appraisal_submission(emp_id):
    # try:
        employee_doc = frappe.get_doc('Employee', emp_id)
        from_date=None
        sal_structure=None
        old_app=None
        new_app=None
        new_ctc=None
        for ap in employee_doc.custom_appraisal_table:
            if not ap.approved_by:
                new_app=ap
                sal_structure=ap.salary_structure
                from_date=ap.from_date
                new_ctc=ap.ctc
            if ap.approved_by and not ap.to_date:
                old_app=ap
            # print(ap.ctc,ap.approved_by,ap.to_date)
        if not new_app:
             frappe.throw("Add an Appraisal record in employee before revising CTC")
        to_date = from_date - timedelta(days=1)
        print(new_app.appraisal_cycle)


        appraisal_list=frappe.get_all("Appraisal",
                                      filters={"appraisal_cycle":new_app.appraisal_cycle,
                                               "employee":employee_doc.name,
                                               "docstatus":1})
        print(appraisal_list)
        if appraisal_list:
            frappe.throw("Already Approved Appraisal existsfor the appraisal cycle")
            return  {
                        "status": False,
                        "msg": f"Already Approved Appraisal existsfor the appraisal cycle"
                    }
        
        appraisal_list=frappe.get_all("Appraisal",
                                      filters={"appraisal_cycle":new_app.appraisal_cycle,
                                               "employee":employee_doc.name,
                                               "docstatus":0})
        print(appraisal_list)
        if not appraisal_list:
            frappe.throw("Open Appraisal for employee doesnot exists, create Appraisal first")
            return  {
                        "status": False,
                        "msg": f"Open Appraisal for employee doesnot exists, create Appraisal first"
                    }
        appraisal_doc=frappe.get_doc("Appraisal",appraisal_list[0].name)
        appraisal_doc.submit()

        # Assign the salary structure
        salary_structure_assignment = frappe.get_doc({
            'doctype': 'Salary Structure Assignment',
            'employee': employee_doc.employee,
            'salary_structure': sal_structure,
            'from_date': from_date,
            "base":round(new_ctc/12,2),
            "company":"LOKESH SANKHALA AND ASSOCIATES",
        })
        salary_structure_assignment.insert()
        salary_structure_assignment.submit()

        if old_app:
            old_app.to_date=to_date

        new_app.approved_by=frappe.session.user


        employee_doc.ctc = round(float(new_ctc),2)
        employee_doc.custom_monthly_salary = round(float(new_ctc)/12,2)
        employee_doc.save()
        # print("Executing w/o exception")

        return {
                "status": True,
                "msg": "Appraisal Submitted and CTC has been revised"
            }

    # except Exception as e:
    #     # Log the error
    #     frappe.log_error(message=str(e), title="Failed to submit appraisal and assign salary structure")
    #     print("Executing with exception",e)
        # return {
        #     "status": False,
        #     "msg": f"Failed to submit appraisal and assign salary structure: {str(e)}"
        # }



