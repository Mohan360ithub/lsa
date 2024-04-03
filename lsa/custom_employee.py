import frappe
import requests
from frappe import _
from frappe.utils import today,add_days, cint, flt, getdate,get_first_day,get_last_day
from datetime import datetime
from hrms.hr.doctype.leave_allocation.leave_allocation import get_previous_allocation
from hrms.hr.doctype.leave_application.leave_application import (get_leave_balance_on,get_leaves_for_period,)
from itertools import groupby





@frappe.whitelist()
def checking_user_authentication(user_email=None):  
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["HR Manager","HR User","LSA CEO Admin","LSA CEO ADMIN TEAM"]

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
    cur_month = frappe.utils.now_datetime().month


    # Fetch employees with birthdays in the current month
    employees = frappe.get_all("Employee",
        filters={
            "status": "Active",
        },
        fields=["name", "employee_name", "date_of_birth"],
        order_by="date_of_birth asc"
    )
    curr_mon_birthday=[]
    for emp in employees:
        if emp.date_of_birth and emp.date_of_birth.month == cur_month:
            curr_mon_birthday.append(emp)

    return curr_mon_birthday




def get_employee_for_user():
    current_user = frappe.session.user
    employee = frappe.get_all("Employee", 
                                   filters={"user_id": current_user,"status":"Active"}, 
                                   fields=["name","employee_name","company","designation","department"])
    # print(employee)
    if employee:
         return employee
    return None


@frappe.whitelist()
def get_leave_data():
    today = datetime.strptime(frappe.utils.nowdate(), "%Y-%m-%d")
    year = today.year
    from_date = datetime(year, 1, 1)
    to_date = datetime(year, 12, 31 )

    leave_types = get_leave_types()
    active_employees = get_employee_for_user()

    precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
    # consolidate_leave_types = len(active_employees) > 1 and filters.consolidate_leave_types
    row = None

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







	

