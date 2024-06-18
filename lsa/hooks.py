app_name = "lsa"
app_title = "Lsa"
app_publisher = "Mohan"
app_description = "Lsa"
app_email = "mohan@360ithub.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lsa/css/lsa.css"
# app_include_js = "/assets/lsa/js/lsa.js"

# include js, css files in header of web template
# web_include_css = "/assets/lsa/css/lsa.css"
# web_include_js = "/assets/lsa/js/lsa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lsa/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "lsa/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "lsa.utils.jinja_methods",
#	"filters": "lsa.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "lsa.install.before_install"
# after_install = "lsa.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "lsa.uninstall.before_uninstall"
# after_uninstall = "lsa.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "lsa.utils.before_app_install"
# after_app_install = "lsa.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "lsa.utils.before_app_uninstall"
# after_app_uninstall = "lsa.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lsa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

doc_events = {
    "Customer": {
        "on_update": "lsa.custom_customer.update_linked_doctypes"
    }
}


# Scheduled Tasks
# ---------------


scheduler_events = {
    "cron":{
        "* * * * *":
            [
            #"lsa.pankaj1.cron",
            ],
        "0 9 * * *":
            [
            "lsa.notice_reminder_mail.mail_remainder_for_client_notice",
            "lsa.timesheet_reminder.mail_remainder_for_timesheet",
            ],
        "0,30 * * * *":
            [
            #"lsa.unofficial_whatsapp_scheduler.send_scheduled_whatsapp_message",
            ],
        "00 1 21 * *":
            [
            "lsa.lsa.doctype.gst_filling_data.gst_filling_data.check_gst_compliance"
            ],
        "00 23 * * *":
            [
            "lsa.custom_attendance.checkin_out_for_missed_logs"
            ],
            
    },
    # "all": [
    #   "lsa.tasks.all"
    # ],
    # "daily": [
    #   "lsa.tasks.daily"
    # ],
    # "hourly": [
    #   "lsa.tasks.hourly"
    # ],
    # "weekly": [
    #   "lsa.tasks.weekly"
    # ],
    # "monthly": [
    #   "lsa.tasks.monthly"
    # ],
}

# Testing
# -------

# before_tests = "lsa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "lsa.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "lsa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["lsa.utils.before_request"]
# after_request = ["lsa.utils.after_request"]

# Job Events
# ----------
# before_job = ["lsa.utils.before_job"]
# after_job = ["lsa.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"lsa.auth.validate"
# ]






