import frappe
from frappe.model.document import Document
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta

class GstFillingData(Document):
    def before_insert(self):
        all_freq_doc = frappe.get_all('Gst Filling Data',filters={"gst_filling_report_id":self.gst_filling_report_id})
        doc=frappe.get_doc("Gst Filing Data Report",self.gst_filling_report_id)
        doc.step_4_count=len(all_freq_doc)+1
        doc.save()

    def on_trash(self):
        all_freq_doc = frappe.get_all('Gst Filling Data',filters={"gst_filling_report_id":self.gst_filling_report_id})
        doc=frappe.get_doc("Gst Filing Data Report",self.gst_filling_report_id)
        doc.step_4_count=len(all_freq_doc)-1
        doc.save()

    def before_save(doc):
        doc_list = frappe.get_all(doc.doctype, filters={"name": doc.name})
        if doc_list:
            old_doc = frappe.get_doc(doc.doctype, doc.name)
            if doc.filing_status == "Filed Summery Shared With Client" and old_doc.filing_status != "Filed Summery Shared With Client":
                existing_gst_file = frappe.get_all(doc.doctype,
                                                    filters={'customer_id': doc.customer_id,
                                                            "filing_status": "Filed Summery Shared With Client"},
                                                    fields=["name", "fy", "month", "modified"]
                                                    )
                latest_file_fy = doc.fy
                latest_file_mon = doc.month
                latest_file_date = doc.modified
                month_num = {"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9,
                            "jan": 10, "feb": 11, "mar": 12}
                if existing_gst_file:
                    count = 1
                    for gst_file in existing_gst_file:
                        fy_y = int(gst_file.fy.split("-")[0])
                        fy_y_o = int(latest_file_fy.split("-")[0])
                        if fy_y_o < fy_y:
                            latest_file_date = gst_file.modified
                            latest_file_fy = gst_file.fy
                            latest_file_mon = gst_file.month
                        elif fy_y_o == fy_y:
                            mon = (gst_file.month.split("-")[0].lower())
                            mon_o = (latest_file_mon.split("-")[0].lower())
                            if month_num[mon_o] < month_num[mon]:
                                latest_file_date = gst_file.modified
                                latest_file_mon = gst_file.month

                year = str(int(latest_file_fy.split("-")[0]))
                if latest_file_mon.lower() in ["jan", "feb", "mar"]:
                    year = str(int(latest_file_fy.split("-")[1]))
                    
                date_object = datetime.strptime(str(latest_file_date).split(" ")[0], '%Y-%m-%d')
                formatted_date = date_object.strftime('%b-%Y')
                formatted_date="-".join([ele.upper() for ele in formatted_date.split("-")])
                # print(latest_file_mon,fy_y_o,formatted_date)
                gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                gst_doc.last_filed = "for " + latest_file_mon +"-"+year+ " in " + formatted_date
                gst_doc.save()

            elif doc.filing_status != "Filed Summery Shared With Client" and old_doc.filing_status == "Filed Summery Shared With Client":
                existing_gst_file = frappe.get_all(doc.doctype,
                                                filters={'customer_id': doc.customer_id,
                                                            "filing_status": "Filed Summery Shared With Client",
                                                            "name": ("not in", [doc.name])},
                                                fields=["name", "fy", "month", "modified"]
                                                )
                latest_file_fy = ""
                latest_file_mon = ""
                latest_file_date = ""
                month_num = {"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9,
                            "jan": 10, "feb": 11, "mar": 12}
                if existing_gst_file:
                    for gst_file in existing_gst_file:
                        if latest_file_fy == "":
                            latest_file_date = gst_file.modified
                            latest_file_fy = gst_file.fy
                            latest_file_mon = gst_file.month
                        else:
                            fy_y = int(gst_file.fy.split("-")[0])
                            fy_y_o = int(latest_file_fy.split("-")[0])
                            if fy_y_o < fy_y:
                                latest_file_date = gst_file.modified
                                latest_file_fy = gst_file.fy
                                latest_file_mon = gst_file.month
                            elif fy_y_o == fy_y:
                                mon = (gst_file.month.split("-")[0].lower())
                                mon_o = (latest_file_mon.split("-")[0].lower())
                                if month_num[mon_o] < month_num[mon]:
                                    latest_file_date = gst_file.modified
                                    latest_file_mon = gst_file.month

                year = str(int(latest_file_fy.split("-")[0]))
                if latest_file_mon.lower() in ["jan", "feb", "mar"]:
                    year = str(int(latest_file_fy.split("-")[1]))
                
                if latest_file_date:
                    date_object = datetime.strptime(str(latest_file_date).split(" ")[0], '%Y-%m-%d')
                    formatted_date = date_object.strftime('%b-%Y')
                    formatted_date="-".join([ele.upper() for ele in formatted_date.split("-")])
                    gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                    gst_doc.last_filed = "for " + latest_file_mon +"-"+year+ " in " + formatted_date
                    gst_doc.save()
                else:
                    gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                    gst_doc.last_filed = ""
                    gst_doc.save()
            if doc.submitted ==1 and old_doc.submitted==0:
                gst_filling_data = frappe.get_all(doc.doctype,
                                    filters={'gst_yearly_filling_summery_id': doc.gst_yearly_filling_summery_id,
                                                'non_compliant':1,
                                                'name':("not in",[doc.name]),
                                                },)
                doc.non_compliant=0
                if not gst_filling_data :
                    gst_doc = frappe.get_doc("Gst Yearly Filing Summery", doc.gst_yearly_filling_summery_id)
                    gst_doc.non_compliant = 0
                    gst_doc.save()
                
                gst_yearly_summary_data = frappe.get_all("Gst Yearly Filing Summery",
                                    filters={'gst_file_id': doc.gstfile,
                                            'non_compliant':1,
                                                },)
                if not gst_yearly_summary_data:
                    gstfile_doc = frappe.get_doc("Gstfile", doc.gstfile)
                    gstfile_doc.non_compliant = 0
                    gstfile_doc.save()
                        
            elif doc.submitted ==0 and old_doc.submitted==1:
                doc.non_compliant=1
                gst_doc = frappe.get_doc("Gst Yearly Filing Summery", doc.gst_yearly_filling_summery_id)
                gst_doc.non_compliant = 1
                gst_doc.save()
                gstfile_doc = frappe.get_doc("Gstfile", doc.gstfile)
                gstfile_doc.non_compliant = 1
                gstfile_doc.save()



def get_financial_year(date):
    if date.month >= 4:
        start_year = date.year
        end_year = date.year + 1
    else:
        start_year = date.year - 1
        end_year = date.year
    return f"{start_year}-{end_year}"

@frappe.whitelist()
def check_gst_compliance(manual=None):
    month_dict = {
                    1: "JAN",
                    2: "FEB",
                    3: "MAR",
                    4: "APR",
                    5: "MAY",
                    6: "JUN",
                    7: "JUL",
                    8: "AUG",
                    9: "SEP",
                    10: "OCT",
                    11: "NOV",
                    12: "DEC"
                }
    today = dt.date.today()
    # today=dt.date(2024, 7, 25)
    today_day_number = today.day

    one_month_before = dt.date(today.year, today.month-1, 21)

    # one_month_before = today - relativedelta(months=1)
    # fy = get_financial_year(one_month_before)
    # month_number = one_month_before.month
    # month_name=month_dict[month_number]
    # today_day_number = today.day
    # one_month_before = today - relativedelta(months=1)

    fy = get_financial_year(one_month_before)
    month_number = one_month_before.month
    month_name=month_dict[month_number]
    # print(today_day_number,month_number,fy)
    if today_day_number >= 21:
        gst_type=["Regular","QRMP"]
        if month_number%3==0:
            gst_type.append("Composition")

        gst_filling_data = frappe.get_all("Gst Filling Data",
                                            filters={'fy': fy,
                                                     'gst_type':("in",gst_type),
                                                     'month':("like","%"+month_name),
                                                    #  'gstfile_enabled':1,
                                                    #  'filing_status':("not in",["Filed Summery Shared With Client"]),
                                                     'submitted':0,
                                                     },)
        # print(len(gst_filling_data))
        for step_4 in gst_filling_data:
            gst_filling = frappe.get_doc("Gst Filling Data", step_4.name)
            gst_filling.non_compliant = 1
            gst_filling.save()
            gst_yearly_summary = frappe.get_doc("Gst Yearly Filing Summery", gst_filling.gst_yearly_filling_summery_id)
            gst_yearly_summary.non_compliant = 1
            gst_yearly_summary.save()
            gstfile_doc = frappe.get_doc("Gstfile", gst_filling.gstfile)
            gstfile_doc.non_compliant = 1
            gstfile_doc.save()
    

        return len(gst_filling_data)
    else:
        frappe.log_error(message=f"today_day_number: {today_day_number}, month_number: {month_number}, month_name: {month_name}", title="Error in GST Filing Non-compliance Marking")

# @frappe.whitelist()
# def check_gst_compliance(manual=None):
#     month_dict = {
#         1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
#         7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"
#     }
    
#     today = dt.date.today()
#     # Uncomment for testing purposes
#     # today = dt.date(2024, 7, 25)

#     # Get the current and previous month
#     current_month = today.month
#     current_year = today.year
#     previous_month = today - relativedelta(months=1)
    
#     # Determine if today is past the 21st of the current month or if the new month has arrived
#     past_21st = today.day >= 21
#     new_month = today.month != previous_month.month

#     if past_21st or new_month:
#         fy = get_financial_year(previous_month)
#         month_number = previous_month.month
#         month_name = month_dict[month_number]
        
#         # Determine GST types
#         gst_type = ["Regular", "QRMP"]
#         if month_number % 3 == 0:
#             gst_type.append("Composition")
        
#         # Fetch non-submitted GST Filling Data for the previous month
#         gst_filling_data = frappe.get_all(
#             "Gst Filling Data",
#             filters={
#                 'fy': fy,
#                 'gst_type': ("in", gst_type),
#                 'month': ("like", "%" + month_name),
#                 'submitted': 0,
#             }
#         )
        
#         # Mark GST Filling Data and related summary as non-compliant
#         for step_4 in gst_filling_data:
#             gst_filling = frappe.get_doc("Gst Filling Data", step_4.name)
#             gst_filling.non_compliant = 1
#             gst_filling.save()
            
#             gst_yearly_summary = frappe.get_doc("Gst Yearly Filing Summery", gst_filling.gst_yearly_filling_summery_id)
#             gst_yearly_summary.non_compliant = 1
#             gst_yearly_summary.save()
        
#         return len(gst_filling_data)
#     else:
#         frappe.log_error(
#             message=f"Today is {today}, which is before the 21st of the month or not in a new month. No GST Filing Data will be marked as non-compliant.",
#             title="Info: GST Filing Non-compliance Check"
#         )

@frappe.whitelist()
def create_gst_filing_data(gst_yearly_filling_summery_id,gstfile,gst_type,fy,gst_filing_data_report):
    try:
        existing_doc=frappe.get_all("Gst Filling Data",
                                    filters={"gst_yearly_filling_summery_id":gst_yearly_filling_summery_id,
                                             "gst_filling_report_id":gst_filing_data_report})
        
        gstfile_doc=frappe.get_doc("Gstfile",gstfile)
        if not(existing_doc):
            gst_filing_data_report_doc=frappe.get_all("Gst Filing Data Report",
                                    filters={"name":gst_filing_data_report},
                                    fields=["name","month","quarterly"])
            gst_filling_data = frappe.new_doc('Gst Filling Data')
            if gst_filing_data_report_doc[0].month:
                gst_filling_data.month = gst_filing_data_report_doc[0].month
                gst_filling_data.gst_filling_report_id=gst_filing_data_report_doc[0].name
            else:
                gst_filling_data.month = gst_filing_data_report_doc[0].quarterly
                gst_filling_data.gst_filling_report_id=gst_filing_data_report_doc[0].name
            gst_filling_data.gst_yearly_filling_summery_id = gst_yearly_filling_summery_id
            gst_filling_data.gstfile = gstfile
            gst_filling_data.customer_id = gstfile_doc.customer_id
            gst_filling_data.created_manually=1
            gst_filling_data.insert()
            gst_filling_data.save()

            return "Gst Filing Data created successfully."
        else:
            return "Gst Filling Data you are trying to create already exists"
    except frappe.exceptions.ValidationError as e:
        frappe.msgprint(f"Validation Error: {e}")
        return False
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False

@frappe.whitelist()
def checking_user_authentication(user_email):
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_records = frappe.get_all('DocPerm',
                                          filters={'parent': 'Gst Filling Data', 'create': 1},
                                          fields=["role"])
        for doc_perm_record in doc_perm_records:
            if doc_perm_record.role in roles:
                status = True
                break
        if user_email == "pankajsankhla90@gmail.com":
            status = True
        return {"status": status, "value": [roles, doc_perm_records]}

    except Exception as e:
        # print(e)
        return {"status": "Failed"}



@frappe.whitelist()
def submit_gst_data(gst_yearly_filling_summary_id, sales_total_taxable, purchase_total_taxable, tax_paid_amount, interest_paid_amount, penalty_paid_amount,gst_filling_data,month):
    response = {}

    try:
        # Get the Gst Yearly Filing Summary document
        gst_yearly_filing_summary = frappe.get_doc("Gst Yearly Filing Summery", gst_yearly_filling_summary_id)

        # Convert input values to float before adding
        sales_total_taxable = float(sales_total_taxable)
        purchase_total_taxable = float(purchase_total_taxable)
        tax_paid_amount = float(tax_paid_amount)
        interest_paid_amount = float(interest_paid_amount)
        penalty_paid_amount = float(penalty_paid_amount)

        gst_yearly_filing_summary = frappe.get_doc("Gst Yearly Filing Summery", gst_yearly_filling_summary_id)
        # Get the Gst Yearly Filing Summary document
        existing_gst_file = frappe.get_all("Gst Filling Data",
                                                filters={'gst_yearly_filling_summery_id': gst_yearly_filling_summary_id,
                                                            "submitted": 1,
                                                            "name": ("not in", [gst_filling_data])},
                                                fields=["month"])
        mon_dict={"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9,
                            "jan": 10, "feb": 11, "mar": 12}
        first_filed_month=month
        last_filed_month=month
        
        for gst_file_4 in existing_gst_file:
            if first_filed_month=="":
                first_filed_month=gst_file_4.month
            else:
                cur_mon = (gst_file_4.month.split("-")[0].lower())
                first_filed_month_mon = (first_filed_month.split("-")[0].lower())
                if mon_dict[cur_mon] < mon_dict[first_filed_month_mon]:
                    first_filed_month=gst_file_4.month

            if last_filed_month=="":
                last_filed_month=gst_file_4.month
            else:
                cur_mon = (gst_file_4.month.split("-")[0].lower())
                last_filed_month_mon = (last_filed_month.split("-")[0].lower())
                if mon_dict[cur_mon] > mon_dict[last_filed_month_mon]:
                    last_filed_month=gst_file_4.month

        if first_filed_month:
            if mon_dict[first_filed_month.split("-")[0].lower()]<10:
                first_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[0])
            else:
                first_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[1])

        if last_filed_month:
            if mon_dict[last_filed_month.split("-")[0].lower()]<10:
                last_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[0])
            else:
                last_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[1])

        # Add values to the existing fields
        gst_yearly_filing_summary.sales_total_taxable += sales_total_taxable
        gst_yearly_filing_summary.purchase_total_taxable += purchase_total_taxable
        gst_yearly_filing_summary.tax_paid_amount += tax_paid_amount
        gst_yearly_filing_summary.interest_paid_amount += interest_paid_amount
        gst_yearly_filing_summary.penalty_paid_amount += penalty_paid_amount
        gst_yearly_filing_summary.fy_first_month_of_filling=first_filed_month
        gst_yearly_filing_summary.fy_last_month_of_filling=last_filed_month
        # Save the changes
        gst_yearly_filing_summary.save()

        gst_filling = frappe.get_doc("Gst Filling Data", gst_filling_data)
        gst_filling.submitted=1
        gst_filling.save()

        response["message"] = "Gst Yearly Filing Summary updated successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."
        # print("DoesNotExistErro")
    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"
        # print("Error",e)
    return response



@frappe.whitelist()
def custom_save_as_draft(gst_yearly_filling_summary_id, sales_total_taxable, purchase_total_taxable, tax_paid_amount, interest_paid_amount, penalty_paid_amount,gst_filling_data):
    response = {}

    try:
        gst_yearly_filing_summary = frappe.get_doc("Gst Yearly Filing Summery", gst_yearly_filling_summary_id)
        # Get the Gst Yearly Filing Summary document
        existing_gst_file = frappe.get_all("Gst Filling Data",
                                                filters={'gst_yearly_filling_summery_id': gst_yearly_filling_summary_id,
                                                            "submitted": 1,
                                                            "name": ("not in", [gst_filling_data])},
                                                fields=["month"])
        mon_dict={"apr": 1, "may": 2, "jun": 3, "jul": 4, "aug": 5, "sep": 6, "oct": 7, "nov": 8, "dec": 9,
                            "jan": 10, "feb": 11, "mar": 12}
        first_filed_month=""
        last_filed_month=""
        
        for gst_file_4 in existing_gst_file:
            if first_filed_month=="":
                first_filed_month=gst_file_4.month
            else:
                cur_mon = (gst_file_4.month.split("-")[0].lower())
                first_filed_month_mon = (first_filed_month.split("-")[0].lower())
                if mon_dict[cur_mon] < mon_dict[first_filed_month_mon]:
                    first_filed_month=gst_file_4.month

            if last_filed_month=="":
                last_filed_month=gst_file_4.month
            else:
                cur_mon = (gst_file_4.month.split("-")[0].lower())
                last_filed_month_mon = (last_filed_month.split("-")[0].lower())
                if mon_dict[cur_mon] > mon_dict[last_filed_month_mon]:
                    last_filed_month=gst_file_4.month
        if first_filed_month:
            if mon_dict[first_filed_month.split("-")[0].lower()]<10:
                first_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[0])
            else:
                first_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[1])

        if last_filed_month:
            if mon_dict[last_filed_month.split("-")[0].lower()]<10:
                last_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[0])
            else:
                last_filed_month+=("-"+gst_yearly_filing_summary.fy.split("-")[1])

        # Convert input values to float before adding
        sales_total_taxable = float(sales_total_taxable)
        purchase_total_taxable = float(purchase_total_taxable)
        tax_paid_amount = float(tax_paid_amount)
        interest_paid_amount = float(interest_paid_amount)
        penalty_paid_amount = float(penalty_paid_amount)

        # Add values to the existing fields
        gst_yearly_filing_summary.sales_total_taxable -= sales_total_taxable
        gst_yearly_filing_summary.purchase_total_taxable -= purchase_total_taxable
        gst_yearly_filing_summary.tax_paid_amount -= tax_paid_amount
        gst_yearly_filing_summary.interest_paid_amount -= interest_paid_amount
        gst_yearly_filing_summary.penalty_paid_amount -= penalty_paid_amount
        gst_yearly_filing_summary.fy_first_month_of_filling=first_filed_month
        gst_yearly_filing_summary.fy_last_month_of_filling=last_filed_month
        # Save the changes
        gst_yearly_filing_summary.save()

        gst_filling = frappe.get_doc("Gst Filling Data", gst_filling_data)
        gst_filling.submitted=0
        gst_filling.save()

        response["message"] = "Gst Yearly Filing Summary updated successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."
        # print(e)
    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"
        # print(e)

    return response







# def on_submit(self):
    #     # Get the gst_yearly_filling_summery_id from the current form
    #     gst_yearly_filling_summery_id = self.gst_yearly_filling_summery_id

    #     # Search for the Gst Yearly Filing Summery document
    #     gst_yearly_filing_summery = frappe.get_doc("Gst Yearly Filing Summery", {"name": gst_yearly_filling_summery_id})

    #     # Update sales_total_taxable
    #     self.update_field(gst_yearly_filing_summery, 'sales_total_taxable')

    #     # Update purchase_total_taxable
    #     self.update_field(gst_yearly_filing_summery, 'purchase_total_taxable')

    #     # Update tax_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'tax_paid_amount')

    #     # Update interest_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'interest_paid_amount')

    #     # Update penalty_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'penalty_paid_amount')

    #     # Save the changes
    #     gst_yearly_filing_summery.save()

    # def on_cancel(self):
    #     # Get the gst_yearly_filling_summery_id from the current form
    #     gst_yearly_filling_summery_id = self.gst_yearly_filling_summery_id

    #     # Search for the Gst Yearly Filing Summery document
    #     gst_yearly_filing_summery = frappe.get_doc("Gst Yearly Filing Summery", {"name": gst_yearly_filling_summery_id})

    #     # Update sales_total_taxable
    #     self.update_field(gst_yearly_filing_summery, 'sales_total_taxable', subtract=True)

    #     # Update purchase_total_taxable
    #     self.update_field(gst_yearly_filing_summery, 'purchase_total_taxable', subtract=True)

    #     # Update tax_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'tax_paid_amount', subtract=True)

    #     # Update interest_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'interest_paid_amount', subtract=True)

    #     # Update penalty_paid_amount
    #     self.update_field(gst_yearly_filing_summery, 'penalty_paid_amount', subtract=True)

    #     # Save the changes
    #     gst_yearly_filing_summery.save()

    # def update_field(self, gst_yearly_filing_summery, field_name, subtract=False):
    #     # Get the field value from the current form
    #     field_value = getattr(self, field_name)

    #     # Check if subtract flag is set
    #     if subtract:
    #         # Subtract the field value from the current value
    #         setattr(gst_yearly_filing_summery, field_name, getattr(gst_yearly_filing_summery, field_name) - field_value)
    #     else:
    #         # Increment the field by the current value
    #         setattr(gst_yearly_filing_summery, field_name, getattr(gst_yearly_filing_summery, field_name) + field_value)








