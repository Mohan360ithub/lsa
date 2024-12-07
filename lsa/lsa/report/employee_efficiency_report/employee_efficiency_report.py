# import frappe
# from frappe import _

# def execute(filters=None):
#     """Main function to fetch data and return columns for the report."""
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns():
#     """Return columns for the report."""
#     return [
#         {
#             "label": _("CID"),
#             "fieldname": "cid",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("Client Name"),
#             "fieldname": "contact_person",
#             "fieldtype": "Data",
#             "width": 150,
#         },
#         {
#             "label": _("File Type"),
#             "fieldname": "file_type",
#             "fieldtype": "Data",
#             "width": 100,
#         },
#         {
#             "label": _("No Of Tasks"),
#             "fieldname": "no_of_tasks",
#             "fieldtype": "Int",
#             "width": 120,
#         },
#         {
#             "label": _("Total Effort (Min)"),
#             "fieldname": "total_effort",
#             "fieldtype": "Data",
#             "width": 150,
#         },
#         {
#             "label": _("Avg Effort (Min)"),
#             "fieldname": "avg_effort",
#             "fieldtype": "Float",
#             "width": 150,
#         },
#         {
#             "label": _("Employee"),
#             "fieldname": "employee_name",
#             "fieldtype": "Data",
#             "width": 150,
#         },
#     ]


# def get_data(filters):
#     """Fetch data for the report."""
#     gst_file = filters.get("master_gst_file")
#     date_range = filters.get("date_range")
#     employee_filter = filters.get("employee")

#     # Prepare filters for GST Filing query
#     gst_filters = {}
#     if gst_file and isinstance(gst_file, list) and gst_file:
#         gst_filters["name"] = gst_file[0]  # Extract the first file name
#     if gst_file and isinstance(gst_file, str):
#         gst_filters["name"] = gst_file  # If directly passed as a string

#     # Initialize data
#     report_data = []

#     # Query GST Filling data
#     gst_fillings = frappe.get_all(
#         "Gst Filling Data",
#         fields=["name", "contact_person"]  # Fetch only relevant fields
#     )

#     # If no GST fillings were found, return empty list
#     if not gst_fillings:
#         print("No GST Filling data found!")
#         return report_data

#     # Process the fetched GST fillings
#     for gst in gst_fillings:
#         # Fetch related status_change_history from the child table (no filters yet)
#         status_change_history = frappe.get_all(
#             "Status History",  # Replace this with the actual child table name
#             filters={"parent": gst.name},
#             fields=["updated_at", "changed_by", "duration"]
#         )

#         # Debugging: Print status_change_history for the current gst
#         # print(f"Status Change History for {gst.name}: {status_change_history}")

#         # Apply filters for date range and employee after fetching the data
#         filtered_tasks = [
#             task for task in status_change_history
#             if task.get("updated_at") and date_in_range(task["updated_at"], date_range)
#         ]

#         filtered_tasks = [
#             task for task in filtered_tasks if employee_matches(task.get("changed_by"), employee_filter)
#         ]

#         # Assign default file_type
#         file_type = "Gstfile"

#         # Fetch the employee name associated with the first task (assuming all tasks are by the same employee)
#         employee_name = get_employee_name(filtered_tasks[0].get("changed_by")) if filtered_tasks else None
		
#         no_of_tasks = len(filtered_tasks)
#         total_effort = calculate_total_effort(filtered_tasks)
#         avg_effort = total_effort / no_of_tasks if no_of_tasks else 0
            
#         report_data.append({
#             "cid": gst.name,
#             "contact_person": gst.contact_person,
#             "file_type": file_type,  # Default file type
#             "no_of_tasks": no_of_tasks,
#             "total_effort": total_effort,
#             "avg_effort": avg_effort,
#             "employee_name": employee_name,  # Employee name field
#         })
#         # print('employee_nameeeeeeeeeeeeeeeeee',employee_name)
#     return report_data


# def get_employee_name(user_id):
#     print('user_iddddddddddddddddddddddd',user_id)
#     """Fetch the employee name associated with the user_id (changed_by field)."""
#     if not user_id:
#         return None

#     employee = frappe.db.get_value("Employee", {"user_id": user_id}, "name")
#     return employee



# from datetime import datetime

# def date_in_range(date, date_range):
#     """Check if the given date falls within the date range filter."""
#     if not date_range or len(date_range) != 2:
#         return True  # If no valid date range filter is applied, include all

#     start_date, end_date = date_range

#     # If the date is already a datetime object, no need to parse it.
#     if isinstance(date, datetime):
#         date_obj = date
#     else:
#         # Otherwise, convert string to datetime
#         date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

#     start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
#     end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
#     return start_date_obj <= date_obj <= end_date_obj

# def employee_matches(changed_by, employee_filter):
#     """Match the email in changed_by to the employee filter."""
#     if not employee_filter or not changed_by or not isinstance(employee_filter, list):
#         return True  # No filter or invalid data, include all
#     if len(employee_filter) == 0:
#         return True  # Empty employee filter, include all
#     # Find employee with this email
#     employee = frappe.db.get_value("Employee", {"user_id": changed_by}, "name")
#     return employee == employee_filter[0]  # Match with the first employee in the filter


# import re

# def parse_duration(duration):
#     # Match the pattern for hours and minutes with or without spaces (e.g., "2h30m", "2 h 30 min", "0h 2m")
#     match = re.match(r'(\d+)\s*h\s*(\d+)\s*m|(\d+)\s*h\s*(\d+)\s*min|(\d+)\s*m', duration)

#     if match:
#         # Extract hours and minutes depending on the match group
#         if match.group(1) and match.group(2):  # case for "Xh Ym"
#             hours = int(match.group(1))
#             minutes = int(match.group(2))
#         elif match.group(3) and match.group(4):  # case for "Xh Ymin"
#             hours = int(match.group(3))
#             minutes = int(match.group(4))
#         elif match.group(5):  # case for "Xm"
#             hours = 0
#             minutes = int(match.group(5))
#         return hours, minutes
#     else:
#         # If the format doesn't match, raise an error
#         raise ValueError(f"Invalid duration format: {duration}")

# def calculate_total_effort(tasks):
#     """Calculate total effort in minutes for filtered tasks."""
#     total_minutes = 0
#     for task in tasks:
#         duration = task.get("duration")
#         if duration:
#             try:
#                 hours, minutes = parse_duration(duration)
#                 total_minutes += (hours * 60) + minutes
#             except ValueError as e:
#                 print(f"Error parsing duration: {e}")
#     return total_minutes



import frappe
from frappe import _

def execute(filters=None):
    """Main function to fetch data and return columns for the report."""
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    """Return columns for the report."""
    return [
        {
            "label": _("CID"),
            "fieldname": "cid",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Client Name"),
            "fieldname": "contact_person",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("File Type"),
            "fieldname": "file_type",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("FY"),
            "fieldname": "fy",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Month"),
            "fieldname": "month",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("No Of Tasks"),
            "fieldname": "no_of_tasks",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Total Effort (Min)"),
            "fieldname": "total_effort",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Avg Effort (Min)"),
            "fieldname": "avg_effort",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": _("User"),
            "fieldname": "changed_by",
            "fieldtype": "Data",
            "width": 150,
        },
    ]
def get_data(filters):
    """Fetch data for the report."""
    gst_file = filters.get("master_gst_file")
    date_range = filters.get("date_range")
    user_filter = filters.get("user")

    # Enforce that a valid date range must be selected
    # if not date_range or len(date_range) != 2:
    #     frappe.msgprint(_("Please select a valid date range to load data."), raise_exception=True)
    #     return []

    # Prepare filters for GST Filing query
    gst_filters = {}
    if gst_file and isinstance(gst_file, list) and gst_file:
        gst_filters["name"] = gst_file[0]  # Extract the first file name
    if gst_file and isinstance(gst_file, str):
        gst_filters["name"] = gst_file  # If directly passed as a string

    # Initialize data
    report_data = []

    # Query GST Filing data
    gst_fillings = frappe.get_all(
        "Gst Filling Data",
        fields=["name", "contact_person", "customer_id","month","fy"]  # Fetch only relevant fields
    )

    # If no GST fillings were found, return empty list
    if not gst_fillings:
        print("No GST Filling data found!")
        return report_data

    # Process the fetched GST fillings
    for gst in gst_fillings:
        # Fetch related status_change_history from the child table
        status_change_history = frappe.get_all(
            "Status History",  # Replace this with the actual child table name
            filters={"parent": gst.name},
            fields=["updated_at", "changed_by", "duration"]
        )

        # Apply date range filter
        filtered_tasks = [
            task for task in status_change_history
            if task.get("updated_at") and date_in_range(task["updated_at"], date_range)
        ]

        # Apply user filter if provided
        filtered_tasks = [
            task for task in filtered_tasks if user_matches(task.get("changed_by"), user_filter)
        ]

        # Assign default file_type
        file_type = "Gstfile"

        no_of_tasks = len(filtered_tasks)
        total_effort = calculate_total_effort(filtered_tasks)
        avg_effort = total_effort / no_of_tasks if no_of_tasks else 0

        report_data.append({
            "cid": gst.customer_id,
            "month":gst.month,
            "fy":gst.fy,
            "contact_person": gst.contact_person,
            "file_type": file_type,  # Default file type
            "no_of_tasks": no_of_tasks,
            "total_effort": total_effort,
            "avg_effort": avg_effort,
            "changed_by": filtered_tasks[0]["changed_by"] if filtered_tasks else None,  # User field
        })

    return report_data



def user_matches(changed_by, user_filter):
    """Match the changed_by field to the user filter."""
    if not user_filter or not changed_by or not isinstance(user_filter, list):
        return True  # No filter or invalid data, include all
    if len(user_filter) == 0:
        return True  # Empty user filter, include all
    return changed_by in user_filter  # Match with any user in the filter


from datetime import datetime
from datetime import datetime

def date_in_range(date, date_range):
    """Check if a given date falls within the specified date range."""
    if not date_range or len(date_range) != 2:
        return True  # If no valid date range is provided, include all dates.

    # Parse start and end dates from the date range
    start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
    end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()

    # Ensure date is a string or extract the date part from a datetime object
    if isinstance(date, datetime):
        date_obj = date.date()
    elif isinstance(date, str):
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        raise TypeError(f"Unsupported type for date: {type(date)}")

    # Check if the date is within the range
    return start_date <= date_obj <= end_date


import re

def parse_duration(duration):
    # Match the pattern for hours and minutes with or without spaces (e.g., "2h30m", "2 h 30 min", "0h 2m")
    match = re.match(r'(\d+)\s*h\s*(\d+)\s*m|(\d+)\s*h\s*(\d+)\s*min|(\d+)\s*m', duration)

    if match:
        # Extract hours and minutes depending on the match group
        if match.group(1) and match.group(2):  # case for "Xh Ym"
            hours = int(match.group(1))
            minutes = int(match.group(2))
        elif match.group(3) and match.group(4):  # case for "Xh Ymin"
            hours = int(match.group(3))
            minutes = int(match.group(4))
        elif match.group(5):  # case for "Xm"
            hours = 0
            minutes = int(match.group(5))
        return hours, minutes
    else:
        # If the format doesn't match, raise an error
        raise ValueError(f"Invalid duration format: {duration}")


def calculate_total_effort(tasks):
    """Calculate total effort in minutes for filtered tasks."""
    total_minutes = 0
    for task in tasks:
        duration = task.get("duration")
        if duration:
            try:
                hours, minutes = parse_duration(duration)
                total_minutes += (hours * 60) + minutes
            except ValueError as e:
                print(f"Error parsing duration: {e}")
    return total_minutes
