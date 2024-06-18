# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt
import frappe, os,csv,requests,boto3
from frappe.model.document import Document
from datetime import datetime,timedelta
import datetime as dt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from frappe.utils.print_format import download_pdf




class RecurringServicePricing(Document):

    def on_update(self):
        if self.status == "Approved" :
            # print(type(self.effective_from))
            # print(self.effective_from)
            all_active_service_prices = frappe.get_all("Recurring Service Pricing",
                                               filters={"customer_id": self.customer_id,
                                                        "status": "Approved",
                                                        "name": ("not in", [self.name])})
            if all_active_service_prices:
                # frappe.throw(f"An Active Pricing {all_active_service_prices[0].name} for the customer Already Exist, first Discontinue it")
                for rsp in all_active_service_prices:
                    rsp_doc= frappe.get_doc("Recurring Service Pricing",rsp.name)
                    rsp_doc.effective_to=datetime.strptime(str(self.effective_from), '%Y-%m-%d').date()- timedelta(days=1)
                    rsp_doc.status = "Discontinued"
                    rsp_doc.save()
            elif not self.effective_from:
                frappe.throw("Effective From date is necessary before setting the doc status to 'Approved'")
            elif not self.mode_of_approval:
                frappe.throw("Mode of Approval is necessary before setting the doc status to 'Approved'")
            elif not self.approval_doc:
                pass
                #frappe.throw("Approval Attachment is necessary before setting the doc status to 'Approved'")

            all_inactive_service_prices = frappe.get_all("Recurring Service Pricing",
                                                        filters={"customer_id": self.customer_id,
                                                                "status": "Discontinued",
                                                                "name": ("not in", [self.name])},
                                                        fields=["effective_to"])
            doc_frm_dt=datetime.strptime(str(self.effective_from), '%Y-%m-%d').date()
            for pr in all_inactive_service_prices:
                # frappe.msgprint(str(pr["effective_to"]))
                # print(doc_frm_dt,pr["effective_to"])
                if doc_frm_dt <= pr["effective_to"]:
                    pass
                    # frappe.throw("Pricing for selected Effective From Date already exists")


            ##############################################################################

            service_ids=[i.service_id for i in self.recurring_services if i.price_revised=="Yes"]
            last_active_service_prices = frappe.get_all("Recurring Service Pricing",
                                                        filters={"customer_id":self.customer_id,
                                                                    "status":"Discontinued",},
                                                        order_by="effective_to desc",
                                                        limit=1)
            
            old_service_id_effective_date={}
            prev_price_doc=self.name
            if last_active_service_prices:
                price_doc = frappe.get_doc("Recurring Service Pricing",last_active_service_prices[0].name)
                for price_item in price_doc.recurring_services:
                    old_service_id_effective_date[price_item.service_id]=price_item.effective_from
                price_doc.next_pricing=self.name
                price_doc.save()
                prev_price_doc=price_doc.name
            if self.service_active==0:       
                for item in self.recurring_services:
                    if item.price_revised=="Yes":
                        item.effective_from = self.effective_from
                    elif item.service_id in old_service_id_effective_date:
                        item.effective_from = old_service_id_effective_date[item.service_id]
                    else:
                        item.effective_from = self.effective_from
                    item.enabled = 1
                    item.save()
                    master_service_doc = frappe.get_doc(item.service_type,item.service_id)
                    if master_service_doc.current_recurring_fees!=item.revised_charges:
                        master_service_doc.current_recurring_fees=item.revised_charges
                    master_service_doc.save()
                self.service_active=1
                self.previous_pricing=prev_price_doc
                self.save()
        elif self.status == "Discontinued" :
            
            if not self.effective_to:
                frappe.throw("Effective To date is necessary before setting the doc status to 'Discontinued'")
            doc_frm_dt=datetime.strptime(str(self.effective_from), '%Y-%m-%d').date()
            doc_to_dt=datetime.strptime(str(self.effective_to), '%Y-%m-%d').date()
            if doc_frm_dt >= doc_to_dt:
                frappe.throw(f"Invalid Effective To Date {self.customer_id}")

            for item in self.recurring_services:
                # print(self.effective_to)
                item.effective_to=self.effective_to
                item.enabled=0
                item.save()
            if self.service_active!=0:
                self.service_active=0
                self.save()
            



@frappe.whitelist()
def fetch_services(customer_id=None):
    frequency_map={"M":"Monthly","Q":"Quarterly","H":"Half-yearly","Y":"Yearly"}
    all_services = frappe.get_all("Customer Chargeable Doctypes")
    existing_pricing=frappe.get_all("Recurring Service Pricing",
                                    filters={"customer_id":customer_id,
                                             "status":"Approved"},)
    existing_pricing_items={}
    if existing_pricing and len(existing_pricing)==1:
        existing_pricing=frappe.get_doc("Recurring Service Pricing",existing_pricing[0].name)
        for row in existing_pricing.recurring_services:
            existing_pricing_items[row.service_id]=row.revised_charges

    # print(existing_pricing_items)
    c_services=[]
    for service in all_services:
        # print(service["name"])
        # if service["name"] in ("IT Assessee File","Gstfile"):
            # print(service["name"])
        c_services_n= (frappe.get_all(service["name"], 
                                        filters={'customer_id': customer_id,"enabled":1},
                                        fields=["name","description","current_recurring_fees","enabled","frequency"]))
        for c_service in c_services_n:
            c_service["service_type"]=service["name"]
            # print(c_service["name"])
            c_service["frequency"]=frequency_map[c_service["frequency"]]
            if c_service["name"] in existing_pricing_items:
                c_service["current_recurring_fees"]=existing_pricing_items[c_service["name"]]
            else:
                c_service["current_recurring_fees"]=c_service["current_recurring_fees"]
        c_services+=list(c_services_n)
            # for c_service in c_services_n:
            #   pass
    
    if c_services:
        # For demonstration purposes, let's just send back a response.
        data = c_services
        return data
    else:
        return "No data found for the given parameters."


@frappe.whitelist()
def fetch_price_revisions(customer_id=None,cur_pricing=None):
    pricings=frappe.get_all("Recurring Service Pricing",
                            filters={"customer_id":customer_id,
                                     "name":("not in",[cur_pricing])},
                            fields=["customer_id","name","effective_from","effective_to","status","fy"])
    cur_pricings=frappe.get_doc("Recurring Service Pricing",cur_pricing)
    old_pricings=[]
    new_pricings=[]
    for pricing in pricings:
        if (cur_pricings.effective_from is None) or (cur_pricings.effective_to is None and pricing.effective_from is not None) \
            or ( pricing.effective_to is not None and pricing.effective_to <=cur_pricings.effective_from):
            old_pricings.append(pricing)
        else:
            new_pricings.append(pricing)
    return {"old_pricings":old_pricings,"new_pricings":new_pricings,}

    
@frappe.whitelist()
def fetch_recent_pricings(customer_id=None):
    pricings=frappe.get_all("Recurring Service Pricing",
                            filters={"customer_id":customer_id},
                            fields=["name","effective_from","effective_to"],
                            order_by="effective_from desc",
                            limit=4)
    return [(f"{i.name}({i.effective_from}-{i.effective_to})",) for i in pricings]

@frappe.whitelist()
def fetch_service_pricing(customer_id=None,service_id=None):

    pr_rev=[]

    pricing_approved=frappe.get_all("Recurring Service Pricing",
                            filters={"customer_id":customer_id,
                                     "status":"Approved"},
                            order_by="effective_from desc",)
    if pricing_approved:
        pr_doc_ap=frappe.get_doc("Recurring Service Pricing",pricing_approved[0].name)
        for item in pr_doc_ap.recurring_services:
            if item.service_id==service_id:
                pr_rev.append({"name":pr_doc_ap.name,"status":pr_doc_ap.status,"current_charges":item.current_charges,"revised_charges":item.revised_charges,
                               "effective_from":item.effective_from,"effective_to":item.effective_to})
                
    pricings=frappe.get_all("Recurring Service Pricing",
                        filters={"customer_id":customer_id,
                                    "status":"Discontinued"},
                        order_by="effective_from desc",)
    for pr in pricings:
        pr_doc=frappe.get_doc("Recurring Service Pricing",pr.name)
        for item in pr_doc.recurring_services:
            # print(item.service_id,service_id ,item.price_revised)
            if item.service_id==service_id and item.price_revised=="Yes":
                pr_rev.append({"name":pr_doc.name,"status":pr_doc.status,"current_charges":item.current_charges,"revised_charges":item.revised_charges,
                               "effective_from":item.effective_from,"effective_to":item.effective_to})
    
    return {"pricing_revision":pr_rev}



# @frappe.whitelist()
# def bulk_first_pricing(customer_id=None,service_id=None):
#     customer_list=frappe.get_all("Customer",
#                                 #  filters={'name': "20130009"},
#                                  fields=["name","disabled"])
#     count=1
#     customer_count=1
#     error_count=1
#     customer_service_list={}
#     for customer in customer_list:
#         exceptions=[]
#         # print(customer)
#         try:
            
#             customer_service=fetch_services(customer.name)
#             # print(customer_service)

#             new_doc = frappe.new_doc('Recurring Service Pricing')

#             new_doc.customer_id = customer.name
#             new_doc.service_active = 1



#             new_doc.status = "Need to Revise"

#             effective_from_date = dt.date(2024, 4, 1)

#             for service in customer_service:
#                 service_item = new_doc.append("recurring_services")
#                 service_item.service_type=service["service_type"]
#                 service_item.service_id = service.name
#                 service_item.company_name=service.description.split("-")[0]
#                 service_item.effective_from=effective_from_date
#                 service_item.current_charges=service.current_recurring_fees
#                 service_item.revised_charges=service.current_recurring_fees
#                 service_item.enabled = 1
#                 service_item.price_revised="Yes"
#                 service_item.frequency=""
#                 service_item.service_enabled=service.enabled
#                 # print("Service Count: ",count)
#                 count+=1
#             # print("Customer Count: ",customer_count)
#             customer_count+=1
#             new_doc.effective_from = effective_from_date
            
#             new_doc.fy = "2023-2024"
#             new_doc.save()

#             new_doc.status = "Revised"
#             new_doc.save()

#             new_doc.status = "Informed to Client"
#             new_doc.save()

#             new_doc.mode_of_approval = "Meeting"
#             # new_doc.status = "Approved"
#             # new_doc.previous_pricing=new_doc.name
#             # new_doc.save()
#         except Exception as e:
#             exceptions.append(e)
#             # print("Error Count: ",error_count)
#             error_count+=1
#             # print(e)
#     return {"msg":"Pricing Created","errors":exceptions}
        

    

    

# @frappe.whitelist()
# def bulk_price_revision_from_excel():
#     file_path = "/home/frappeuser/bench-lsa/apps/lsa/lsa/modified_15_May.csv"
#     customer_list = []
#     service_price_map = {}
#     exceptions = []
#     exception_record = []

#     # Read the CSV file
#     try:
#         with open(file_path, mode='r') as file:
#             csv_reader = csv.reader(file)
#             next(csv_reader)  # Skip the header row if there is one
#             for row in csv_reader:
#                 try:
#                     if row[3].strip().isnumeric():
#                         price = float(row[3].strip())
#                         service_price_map[(row[0].strip(), row[1].strip(), row[2].strip())] = price
#                         if row[0].strip() not in customer_list:
#                             customer_list.append(row[0].strip())
#                     else:
#                         exception_record.append(row)
#                         frappe.log_error(f"Non-numeric price found: {row}", "CSV Parsing Error")
#                 except Exception as er:
#                     exception_record.append(row)
#                     frappe.log_error(f"Error processing row: {row} - {str(er)}", "CSV Row Processing Error")
#     except Exception as e:
#         frappe.log_error(f"Error opening file: {str(e)}", "File Read Error")
#         return {"status": False, "message": "File read error", "error": str(e)}

#     count = 0
#     customer_count = 0
#     error_count = 1
#     old_serv_count = 0
#     new_serv_count = 0

#     for customer in customer_list:
#         try:
#             customer_service = fetch_services(customer)
#             if customer_service:
#                 new_doc = frappe.new_doc('Recurring Service Pricing')
#                 new_doc.customer_id = customer
#                 new_doc.status = "Need to Revise"
#                 effective_from_date = dt.date(2024, 4, 1)
#                 new_doc.effective_from = effective_from_date
#                 new_doc.fy = "2024-2025"

#                 for service in customer_service:
#                     service_item = new_doc.append("recurring_services")
#                     service_item.service_type = service["service_type"]
#                     service_item.service_id = service["name"]
#                     service_item.company_name = service["description"].split("-")[0]
#                     service_item.frequency = service.frequency
#                     service_item.current_charges = service.current_recurring_fees

#                     key = (customer, service["service_type"], service["name"])
#                     if key in service_price_map:
#                         service_item.revised_charges = service_price_map[key]
#                         new_serv_count += 1
#                         del service_price_map[key]
#                     else:
#                         service_item.revised_charges = service.current_recurring_fees
#                         old_serv_count += 1

#                     service_item.enabled = 1
#                     service_item.price_revised = "Yes" if service_item.revised_charges != service_item.current_charges else "No"
#                     service_item.service_enabled = service.enabled
#                     count += 1

#                 new_doc.save()
#                 frappe.db.commit()
#                 customer_count += 1

#         except Exception as e:
#             frappe.log_error(f"Error processing customer: {customer} - {str(e)}", "Customer Processing Error")
#             exceptions.append(str(e))
#             error_count += 1

#     return {
#         "msg": "Pricing Created",
#         "errors": exceptions,
#         "exception_record": exception_record,
#         "customer_count": customer_count,
#         "service_count": count,
#         "old_service_count": old_serv_count,
#         "new_service_count": new_serv_count,
#         "remaining_service_price_map": service_price_map
#     }






@frappe.whitelist()
def rsp_revision_mail(rsp_id=None, recipient=None, subject=None, bodyh=None,bodyf=None):
    if rsp_id and recipient and subject and bodyh and bodyf:
        rsp_doc = frappe.get_doc("Recurring Service Pricing", rsp_id)

        email_account = frappe.get_doc("Email Account", "LSA Accounts")
        sender_email = email_account.email_id
        sender_password = email_account.get_password()
        # cc_email = "360ithub.developers@gmail.com"
        
        body=""
        for i in (bodyh.split("\n")):
            
            if i:
                body+=f'<pre style="font-family: Arial, sans-serif;margin: 0; padding: 0;">{i}</pre>'
            else:
                body+='<br>'

            # print(i1)

        body += """
                <br><table class="table table-bordered" style="border-color: #444444; border-collapse: collapse; width: 100%;">
                    <thead>
                        <tr style="background-color:#3498DB;color:white;text-align: left;">
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">S. No.</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service Type</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Service ID</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 35%;">Company Name</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 15%;">Revised Charges(INR)</th>
                            <th style="vertical-align: middle;border: solid 2px #bcb9b4; width: 10%;">Payment Terms</th>
                        </tr>
                    </thead>
                    <tbody>
                """
        count=1
        for service in rsp_doc.recurring_services:
            body += f"""
                <tr>
                    <td style="border: solid 2px #bcb9b4;">{count}</td>
                    <td style="border: solid 2px #bcb9b4;">{service.service_type}</td>
                    <td style="border: solid 2px #bcb9b4;">{service.service_id}</td>
                    <td style="border: solid 2px #bcb9b4;">{service.company_name}</td>
                    <td style="border: solid 2px #bcb9b4;">{service.revised_charges}</td>
                    <td style="border: solid 2px #bcb9b4;">{service.frequency}</td>
                </tr>
            """
            count+=1

        body += """
                    </tbody>
                </table><br>

        """



        for j in (bodyf.split("\n")):
            if j:
                body+=f'<pre style="font-family: Arial, sans-serif;margin: 0; padding: 0;">{j}</pre>'
            else:
                body+='<br>'

        # print(body)
        # Create the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        # message['Cc'] = cc_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))

        # Attach the PDF file
        pdf_link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name={rsp_id}&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{rsp_id}.pdf"
        pdf_filename = "quotation_service_price_revision.pdf"
        attachment = get_file_from_link(pdf_link)
        if attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {pdf_filename}",
            )
            message.attach(part)

        # Connect to the SMTP server and send the email
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            try:
                # Send email
                server.sendmail(sender_email, recipient.split(',') , message.as_string())
                return "Email sent successfully!"
            except Exception as e:
                print(f"Failed to send email. Error: {e}")
                return "Failed to send email."
    else:
        return "Invalid parameters passed."
    
def get_file_from_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch file from link. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching file from link: {e}")
        return None
    


@frappe.whitelist()
def store_rsp_in_s3(rsp_id=None):
    rsp_doc = frappe.get_doc("Recurring Service Pricing", rsp_id)
    # Configure boto3 client
    s3_doc=frappe.get_doc("S3 360 Dev Test")
    # Configure boto3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=s3_doc.access_key,
        aws_secret_access_key=s3_doc.secret_key,
        region_name=s3_doc.region_name,
    )

    file_link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name={rsp_id}&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{rsp_id}.pdf"

    # Fetch file content from link
    file_content = get_pdf_for_record(rsp_id)

    if file_content:
        # Bucket name and file name
        bucket_name = 'devbucketindia'
        folder_name = f'vatsal_test/CID/{rsp_doc.customer_id}'
        file_name = f'{rsp_id}.pdf'
        # print(file_content)
        # Upload file to S3
        try:
            response = s3_client.put_object(Bucket=bucket_name, Key=f"{folder_name}/{file_name}", Body=file_content)
            print(response)
            # print(response.json())
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                return "File uploaded successfully"
            else:
                return f"Failed to upload file to S3: {response['ResponseMetadata']['HTTPStatusCode']}"
        except Exception as e:
            # print(e)
            return f"Error uploading file to S3: {e}"
    else:
        return f"Failed to fetch file from link."



def get_pdf_for_record(rsp_id):
    try:
        doc=frappe.get_doc("Recurring Service Pricing",rsp_id)
        # pdf_file = download_pdf(
        doctype="Recurring Service Pricing"
        name=rsp_id
        format="Recurring Service Pricing default"
        doc=doc
        no_letterhead=0
        letterhead="LSA"
        # )
        pdf_file = frappe.get_print(
			doctype, name, format, doc=doc, as_pdf=True, letterhead=letterhead, no_letterhead=no_letterhead
		)
        # print(pdf_file)
        return pdf_file
    except Exception as er:
        print(er)
        frappe.msgprint(f"Error fetching file: {er}")

# def get_file_from_link(link):
#     try:
#         response = requests.get(link)
#         if response.status_code == 200:
#             return response.status_code, response.content
#         else:
#             print(f"Failed to fetch file from link. Status code: {response.status_code}")
#             return response.status_code, None
#     except Exception as e:
#         print(f"Error fetching file from link: {e}")
#         return 404, None

    

# @frappe.whitelist()
# def rsp_revision_mail_0(rsp_id=None, recipient=None, subject=None, body=None):
#     if rsp_id and recipient and subject and body:
#         emp_ls = frappe.get_doc("Recurring Service Pricing", rsp_id)

#         email_account = frappe.get_doc("Email Account", "LSA OFFICE")
#         sender_email = email_account.email_id
#         sender_password = email_account.get_password()

#         cc_email = "360ithub.developers@gmail.com"

#         # Create the email message
#         message = MIMEMultipart()
#         message['From'] = sender_email
#         message['To'] = recipient
#         message['Cc'] = cc_email
#         message['Subject'] = subject
#         message.attach(MIMEText(body, 'plain'))

#         # Attach the PDF file
#         pdf_link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name=PR-2024-2025-20131037-03&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/PR-2024-2025-20131037-03.pdf"
#         pdf_filename = "quotation_service_price_revision.pdf"
#         attachment = get_file_from_link(pdf_link)
#         if attachment:
#             part = MIMEBase("application", "octet-stream")
#             part.set_payload(attachment)
#             encoders.encode_base64(part)
#             part.add_header(
#                 "Content-Disposition",
#                 f"attachment; filename= {pdf_filename}",
#             )
#             message.attach(part)

#         # Connect to the SMTP server and send the email
#         smtp_server = 'smtp.gmail.com'
#         smtp_port = 587
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             try:
#                 # Send email
#                 server.sendmail(sender_email, recipient.split(',') + cc_email.split(','), message.as_string())
#                 return "Email sent successfully!"
#             except Exception as e:
#                 print(f"Failed to send email. Error: {e}")
#                 return "Failed to send email."
#     else:
#         return "Invalid parameters passed."
    


######################################### WhatsApp #####################################################



########################################Single RSP template with PDF###########################################################

@frappe.whitelist()
def whatsapp_RSP_template(docname,new_mobile):
    #new_mobile="9098543046"

    whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
    if whatsapp_demo:
        sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
        whatsapp_items = []

        invoice_doc = frappe.get_doc('Recurring Service Pricing', docname)
        customer = invoice_doc.customer_id
        effective_from = invoice_doc.effective_from
        customer_name = invoice_doc.customer_name
        docname = invoice_doc.name

        instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
        ins_id = instance.instance_id


        try:
            # Check if the mobile number has 10 digits
            if len(new_mobile) != 10:
                frappe.msgprint("Please provide a valid 10-digit mobile number.")
                return
            parsed_date = datetime.strptime(str(effective_from), '%Y-%m-%d')
            formatted_effective_from = parsed_date.strftime('%B %d, %Y')
            
            message = f'''Dear Sir/Madam,

Please be informed that there will be a revision in pricing effective from {formatted_effective_from}. Should you have any questions or require further discussion, please do not hesitate to contact us.

For continued service, kindly acknowledge this notice by taking a printout, signing it, and returning the signed copy to our office. Alternatively, you may email a scanned copy to accounts@lsaoffice.com at your earliest convenience.

Thank you for your attention to this matter.

Regards
Accounts Team
LSA Office
8951692788'''
            
            ########################### Below commented link is work on Live #######################
            link=f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Recurring%20Service%20Pricing&name={docname}&format=Recurring%20Service%20Pricing%20default&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            # link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{docname}.pdf"
            # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"

            url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
            params_1 = {
                "token": ins_id,
                "phone": f"91{new_mobile}",
                "message": message,
                "link": link
            }

            whatsapp_items.append( {"type": "Sales Order",
                                    "document_id": invoice_doc.name,
                                    "mobile_number": new_mobile,
                                    "customer":customer,})
            
            response = requests.post(url, params=params_1)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
            response_data = response.json()
            message_id = response_data['data']['messageIDs'][0]


            # Check if the response status is 'success'
            if response_data.get('status') == 'success':
                # Log the success

                frappe.logger().info("WhatsApp message sent successfully")
                sales_invoice_whatsapp_log.append("details", {
                                                "type": "Recurring Service Pricing",
                                                "document_id": invoice_doc.name,
                                                "mobile_number": new_mobile,
                                                "customer":customer,
                                                "message_id":message_id
                                                            
                                                # Add other fields of the child table row as needed
                                            })
                sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
                sales_invoice_whatsapp_log.sender = frappe.session.user
                sales_invoice_whatsapp_log.type = "Template"
                sales_invoice_whatsapp_log.message = message
                sales_invoice_whatsapp_log.insert()
                return {"status":True,"msg":"WhatsApp message sent successfully"}
            else:
                return {"status":False,"error":f"{response.json()}","msg":"An error occurred while sending the WhatsApp message."}
            # return {"status":True,"msg":f"{invoice_doc.effective_from},{formatted_effective_from}","template":message}

        except requests.exceptions.RequestException as e:
            # Log the exception and provide feedback to the user
            frappe.logger().error(f"Network error: {e}")
            return {"status":False,"error":e,"msg":"An error occurred while sending the WhatsApp message. Please try again later."}
        except Exception as er:
            # Log the exception and provide feedback to the user
            frappe.logger().error(f"Error: {er}")
            return {"status":False,"error":er,"msg":"An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator."}
    else:
        return {"status":False,"msg":"Your WhatApp API instance is not connected"}


#####################################################################################################
########################## Selected RSP Whatsapp(BULK)  ##################
################################## (RSP with PDF Button)###########################


@frappe.whitelist()
def send_rsp_whatsapp_bulk(new_mobile):
    pass
#     new_mobile_dict = json.loads(new_mobile)
#     count = 0
#     success_number = []
#     success_sales_invoices = []
#     whatsapp_items = []
#     # instance_id=whatsapp_demo.instance_id
#     whatsapp_demo = frappe.get_all('WhatsApp Instance',filters={'module':'Accounts','connection_status':1,'active':1})
#     if whatsapp_demo:
#         whatsapp_demo_doc = instance = frappe.get_doc('WhatsApp Instance',whatsapp_demo[0].name)
#         connection_status = whatsapp_demo_doc.connection_status
#         mobile_numbers =[]
        
#         sales_invoice_whatsapp_log = frappe.new_doc('WhatsApp Message Log')
#         for invoice_key in new_mobile_dict:
#                 # Fetch the sales invoice document based on the key
#                 invoice_doc = frappe.get_doc('Sales Order', invoice_key)
                
#                 from_date = invoice_doc.custom_so_from_date
#                 to_date = invoice_doc.custom_so_to_date
#                 customer = invoice_doc.customer
#                 total = invoice_doc.rounded_total
#                 customer_name = invoice_doc.customer_name
#                 docname = invoice_doc.name
                
#                 ins_id = whatsapp_demo_doc.instance_id


#                 try:
#                     # Check if the mobile number has 10 digits
#                     if len(new_mobile_dict[invoice_key]) != 10:
#                         frappe.msgprint("Please provide a valid 10-digit mobile number.")
#                         return
#                     payment_link=""
#                     if (invoice_doc.custom_razorpay_payment_url):
#                         payment_link=f"Payment Link is : {invoice_doc.custom_razorpay_payment_url}"
                    
#                     mobile_numbers.append(new_mobile_dict[invoice_key])


                    
            
#                     message = f'''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {to_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
        
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
# {payment_link}
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
                    
#                     ########################### Below commented link is work on Live #######################
#                     link = f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={invoice_key}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{invoice_key}.pdf"
#                     # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name=SAL-ORD-2023-00262&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
            
#                     url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
#                     params_1 = {
#                         "token": ins_id,
#                         "phone": f"91{new_mobile_dict[invoice_key]}",
#                         "message": message,
#                         "link": link
#                     }
#                     # print(new_mobile_dict[invoice_key])
#                     # whatsapp_items.append( {"type": "Sales Invoice",
#                     #                         "document_id": invoice_doc.name,
#                     #                         "mobile_number": new_mobile_dict[invoice_key],
#                     #                         "customer":invoice_doc.customer,})
                    
#                     response = requests.post(url, params=params_1)
#                     response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
#                     response_data = response.json()

#                     message_id = response_data['data']['messageIDs'][0]

#                     # Check if the response status is 'success'
#                     if response_data.get('status') == 'success':
#                         # Log the success

#                         frappe.logger().info("WhatsApp message sent successfully")
#                         # print("send succesfully")
#                         sales_invoice_whatsapp_log.append("details", {
#                                                         "type": "Sales Order",
#                                                         "document_id": invoice_doc.name,
#                                                         "mobile_number": new_mobile_dict[invoice_key],
#                                                         "customer":invoice_doc.customer,
#                                                         "message_id":message_id
                                                                    
#                                                         # Add other fields of the child table row as needed
#                                                     })
#                     else:
#                         frappe.logger().error(f"Failed to send Whatsapp Message for {invoice_doc.name}")
            
            
#                     frappe.logger().info(f"Sales Order response: {response.text}")
            
#                     # Create a new WhatsApp Message Log document
                    
                    
#                     count += 1 
#                     success_number+=[new_mobile_dict[invoice_key]]
#                     success_sales_invoices+=[invoice_key]

                
            
#                 except requests.exceptions.RequestException as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Network error: {e}")
#                     # frappe.msgprint("An error occurred while sending the WhatsApp message. Please try again later.")
#                 except Exception as e:
#                     # Log the exception and provide feedback to the user
#                     frappe.logger().error(f"Error: {e}")
#                     # frappe.msgprint("An unexpected error occurred while sending the WhatsApp message. Please contact the system administrator.")
#         message = '''Dear {customer_name},
            
# Your Sale Invoice for {from_date} to {due_date} period is due for amount of Rs {total}/- Kindly pay on below bank amount details
            
# Our Bank Account
# Lokesh Sankhala and ASSOSCIATES
# Account No = 73830200000526
# IFSC = BARB0VJJCRO
# Bank = Bank of Baroda,JC Road,Bangalore-560002
# UPI id = LSABOB@UPI
# Gpay / Phonepe no = 9513199200
# {payment_link}
        
# Call us immediately in case of query.
        
# Best Regards,
# LSA Office Account Team
# accounts@lsaoffice.com'''
        
#         # sales_invoice_whatsapp_log.sales_invoice = ",".join(success_sales_invoices)
#         # sales_invoice_whatsapp_log.customer = invoice_doc.customer
#         # sales_invoice_whatsapp_log.posting_date = from_date
#         sales_invoice_whatsapp_log.send_date = frappe.utils.now_datetime()
#         # sales_invoice_whatsapp_log.total_amount = total
#         # sales_invoice_whatsapp_log.mobile_no = ",".join(success_number)
#         sales_invoice_whatsapp_log.sender = frappe.session.user
#         # sales_invoice_whatsapp_log.sales_invoice =  docname
#         sales_invoice_whatsapp_log.type = "Template"
#         sales_invoice_whatsapp_log.message = message
#         # sales_invoice_whatsapp_log.file = link
#         # sales_invoice_whatsapp_log.details = whatsapp_items
#         # print( "Sales Invoice",invoice_salesinvoice,mobile_number,invoice_doc.customer)
#         # print(whatsapp_items)
#         sales_invoice_whatsapp_log.insert()
#         if len(success_number)==len(new_mobile_dict):
#             return {"status":True,"msg":"WhatsApp messages sent successfully"}
#         else:
#             msg=f"{len(success_number)} of {len(new_mobile_dict)} WhatsApp messages sent successfully"
#             return {"status":True,"msg":msg}
       
#     else:
#         return {"status":False,"msg":"Your WhatApp API instance is not connected"}

###################################################### RSP with GST Regular ####################################################

# @frappe.whitelist()
# def mark_gst_regular():
#     try:
#         gst_pricing=frappe.get_all("Recurring Service Item",
#                                 filters={"service_type":"Gstfile"},
#                                 fields=["name","parent","service_id"],)
#         gst_pricing_dict={pr.service_id:pr.parent for pr in gst_pricing}
#         if gst_pricing_dict:
#             gst_reg=frappe.get_all("Gstfile",
#                                 filters={"gst_type":"Regular","enabled":1})
#             gst_reg=[gst.name for gst in gst_reg]
#             for gst_pr in gst_pricing_dict :
#                 if gst_pr in gst_reg:
#                     pr_doc=frappe.get_doc("Recurring Service Pricing",gst_pricing_dict[gst_pr])
#                     pr_doc.gst_type="Regular"
#                     pr_doc.save()
#         return {"status":True,"msg":"RSP with GST Regular have been Marked"}
#     except Exception as er:
#         return {"status":False,"msg":f"Error: {er}"}


####################################Srikanth code start ###############################################################################
##########################################  USER AUTH ######################################
import frappe
 
@frappe.whitelist()
def check_user_permission(service_master):
    try:
        # Print the current user for debugging
        print(frappe.session.user)
        
        # Get all Department Manager documents
        department_managers = frappe.get_all(
            "Department Manager",
            filters={"master_file": service_master},
            fields=["department_head"]
        )
 
        # Check if the department_head matches the current user
        if department_managers and frappe.session.user in [department_managers[0].department_head,"Administrator"] :
            # Conditions met
            return {"status":True,"msg":"Authorised User"}
        elif frappe.session.user in ["Administrator"] :
            # Conditions met
            return {"status":True,"msg":"Authorised User"}
        
        return {"status":False,"msg":"Unauthorised User"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to check user permission")
        return {"status":False,"msg":f"Error authenticating user{e}"}

@frappe.whitelist()
def check_and_send_email(recipients, subject, message):
    try:
        # Check if all necessary fields are provided
        if recipients and subject and message:
            send_email(recipients, subject, message)
            return {"status":True,"msg":"Mail sent successfully"}
        else:
            frappe.throw("Recipients, subject, and message are all required to send an email.")
            return {"status":False,"msg":"Error sending mail"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to check and send email")
        return {"status":False,"msg":f"Error sending mail: {e}"}
 
def send_email(recipients, subject, message):
    frappe.sendmail(
        recipients=recipients.split(','),
        subject=subject,
        message=message,
    )
    frappe.db.commit()
 

#################################################################Srikanth Code End####################################################

