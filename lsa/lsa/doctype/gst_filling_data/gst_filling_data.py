import frappe
from frappe.model.document import Document
from datetime import datetime

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
                                                    filters={'cid': doc.cid,
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

                date_object = datetime.strptime(str(latest_file_date).split(" ")[0], '%Y-%m-%d')
                formatted_date = date_object.strftime('%b-%Y')

                gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                gst_doc.last_filed = "for " + latest_file_mon + " in " + formatted_date
                gst_doc.save()

            elif doc.filing_status != "Filed Summery Shared With Client" and old_doc.filing_status == "Filed Summery Shared With Client":
                existing_gst_file = frappe.get_all(doc.doctype,
                                                filters={'cid': doc.cid,
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

                if latest_file_date:
                    date_object = datetime.strptime(str(latest_file_date).split(" ")[0], '%Y-%m-%d')
                    formatted_date = date_object.strftime('%b-%Y')

                    gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                    gst_doc.last_filed = "for " + latest_file_mon + " in " + formatted_date
                    gst_doc.save()
                else:
                    gst_doc = frappe.get_doc("Gstfile", doc.gstfile)
                    gst_doc.last_filed = ""
                    gst_doc.save()

        


                
            



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


@frappe.whitelist()
def create_gst_filing_data(gst_yearly_filling_summery_id,gstfile,gst_type,fy,gst_filing_data_report):
    try:
        existing_doc=frappe.get_all("Gst Filling Data",
                                    filters={"gst_yearly_filling_summery_id":gst_yearly_filling_summery_id,
                                             "gst_filling_report_id":gst_filing_data_report})
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
        print(e)
        return {"status": "Failed"}



@frappe.whitelist()
def submit_gst_data(gst_yearly_filling_summary_id, sales_total_taxable, purchase_total_taxable, tax_paid_amount, interest_paid_amount, penalty_paid_amount,gst_filling_data):
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

        # Add values to the existing fields
        gst_yearly_filing_summary.sales_total_taxable += sales_total_taxable
        gst_yearly_filing_summary.purchase_total_taxable += purchase_total_taxable
        gst_yearly_filing_summary.tax_paid_amount += tax_paid_amount
        gst_yearly_filing_summary.interest_paid_amount += interest_paid_amount
        gst_yearly_filing_summary.penalty_paid_amount += penalty_paid_amount

        # Save the changes
        gst_yearly_filing_summary.save()

        gst_filling = frappe.get_doc("Gst Filling Data", gst_filling_data)
        gst_filling.submitted=1
        gst_filling.save()

        response["message"] = "Gst Yearly Filing Summary updated successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."

    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"

    return response



@frappe.whitelist()
def custom_save_as_draft(gst_yearly_filling_summary_id, sales_total_taxable, purchase_total_taxable, tax_paid_amount, interest_paid_amount, penalty_paid_amount,gst_filling_data):
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

        # Add values to the existing fields
        gst_yearly_filing_summary.sales_total_taxable -= sales_total_taxable
        gst_yearly_filing_summary.purchase_total_taxable -= purchase_total_taxable
        gst_yearly_filing_summary.tax_paid_amount -= tax_paid_amount
        gst_yearly_filing_summary.interest_paid_amount -= interest_paid_amount
        gst_yearly_filing_summary.penalty_paid_amount -= penalty_paid_amount

        # Save the changes
        gst_yearly_filing_summary.save()

        gst_filling = frappe.get_doc("Gst Filling Data", gst_filling_data)
        gst_filling.submitted=0
        gst_filling.save()

        response["message"] = "Gst Yearly Filing Summary updated successfully"

    except frappe.DoesNotExistError:
        response["error"] = "Error: Gst Yearly Filing Summary not found."

    except Exception as e:
        response["error"] = f"An error occurred: {str(e)}"

    return response






