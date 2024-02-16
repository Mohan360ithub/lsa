import frappe
import requests
from frappe import _
from frappe.utils import today


@frappe.whitelist()
def fetch_sales_orders(cid=None):
    # Fetch sales orders based on the customer ID and docstatus
    sales_orders = frappe.get_list(
        'Sales Order',
        filters={'customer': cid, 'status': ('in', ["Draft", "On Hold", "To Deliver and Bill", "To Bill", "To Deliver"])},
        fields=['name', 'transaction_date', 'advance_paid', 'grand_total', 'customer', 'customer_name', 'status']
    )

    # Return a list of dictionaries with sales order details
    return [
        {
            'sales_order': so.name,
            'transaction_date': so.transaction_date,
            'advance_paid': so.advance_paid,
            'total': so.grand_total,
            'cid': so.customer,
            'customer_name': so.customer_name,
            'sales_status': so.status
        }
        for so in sales_orders
        if so.grand_total != so.advance_paid
    ]

#############################################################################################################################


# # Aisensy integration for Sales Invoice

# @frappe.whitelist(allow_guest=True)
# def aisensy(docname, customer,from_date,to_date,total,new_mobile,razorpay_payment_link):
#     try:
#         ai_sensy_api = frappe.get_doc('Ai Sensy Api')

#         application_url = ai_sensy_api.application_url
#         ai_sensy_url = ai_sensy_api.ai_sensy_url
#         ai_sensy_api1 = ai_sensy_api.ai_sensy_api
#         # Check if Sales Invoice exists
#         if not frappe.get_value('Sales Invoice', docname):
#             frappe.msgprint(_("Sales Invoice {0} not found.").format(docname))
#             return

#         # Fetch the Sales Invoice document
#         sales_invoice = frappe.get_doc('Sales Invoice', docname)
#         erpnext_url = application_url
#         # Replace the following URL with the actual AI Sensy API endpoint
#         sensy_api_url = ai_sensy_url

#         sales_invoice_url = frappe.utils.get_url(
#             f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en"
#         )
#         pdf_url = f"{erpnext_url}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format=Standard"

#         # pdf_url1 = frappe.utils.get_url(
#         #     f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format=Standard"
#         # )

#         # Example payload to send to the AI Sensy API
#         payload = {
#             "apiKey": ai_sensy_api1,  # Replace with your actual API key
#             "campaignName": "lsa_saleorder_invoice_with_payment_link",
#             "destination": new_mobile,
#             "userName": customer,
#             "templateParams": [
#                 customer,
#                 from_date,
#                 to_date,
#                 total,
#                 razorpay_payment_link
#             ],
#             "media": {
#                 "url": sales_invoice_url,
#                 "filename": docname
#             }
#         }

#         # Make a POST request to the AI Sensy API
#         response = requests.post(sensy_api_url, json=payload)

#         # Check if the request was successful (status code 200)
#         if response.status_code == 200:
#             # Log the API response for reference
#             frappe.logger().info(f"AI Sensy response: {response.text}")

#             # You can update the Sales Invoice or perform other actions based on the API response
#             # sales_invoice.custom_field = response.json().get('result')
#             # sales_invoice.save()

#             frappe.msgprint(_("WhatsApp Message Sent successfully : {0}").format(response.text))
#         else:
#             # Log the error and provide feedback to the user
#             frappe.logger().error(f"Sensy API Error: {response.text}")
#             frappe.msgprint(_("WhatsApp message failed to send!. Please try again Later."))

#     except requests.exceptions.RequestException as e:
#         # Log the exception and provide feedback to the user
#         frappe.logger().error(f"Network error: {e}")
#         frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later."))

#     except Exception as e:
#         # Log the exception and provide feedback to the user
#         frappe.logger().error(f"Custom Button Script Error: {e}")
#         frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later."))



# ##########################################################################################
# #Razorpay Payment Link For Sales Invoice
# import razorpay


# @frappe.whitelist()
# def create_razorpay_order(amount, invoice_name,customer,customer_name):
#     # Your Razorpay API key and secret
#     razorpay_api = frappe.get_doc('Razorpay Api')

#     razorpay_api_url = razorpay_api.razorpay_api_url
#     razorpay_api_key = razorpay_api.razorpay_api_key
#     razorpay_api_secret = razorpay_api.razorpay_secret
    
    
#     razorpay_key_id = razorpay_api_key
#     razorpay_key_secret = razorpay_api_secret

#     # Specify the custom Razorpay API URL
#     custom_razorpay_api_url = razorpay_api_url

#     # Convert the amount to an integer (representing paise)
#     amount_in_paise = int(float(amount) * 100)

#     # Create a Razorpay order
#     order_params = {
#         "amount": amount_in_paise,
#         "currency": "INR",
#         "accept_partial": True,
#         "first_min_partial_amount": 100,
#         "description": invoice_name,
#         "notes": {
#             "invoice_name": invoice_name
#         },
#         # "accept_partial": True,
#         # "expire_by": 1691097057,
#         "reference_id": invoice_name
#     }
 
#     try:
#         # Use the requests library to send a POST request
#         order = requests.post(
#             custom_razorpay_api_url,
#             json=order_params,
#             auth=(razorpay_key_id, razorpay_key_secret)  # Add authentication here
#         )

#         # Check if the request was successful (status code 2xx)
#         order.raise_for_status()

#         # Get the JSON response
#         response_json = order.json()

#         # Extract short_url from the response
#         short_url = response_json.get('short_url')

#         # Optionally, you can store custom_payment_link in a database or use it as needed

#         # Update the Sales Invoice document with the short_url
#         doc = frappe.get_doc('Sales Invoice', invoice_name)
#         doc.razorpay_payment_url = short_url
#         doc.save()

#         frappe.msgprint(f'Successfully created Razorpay order. Short URL: {short_url}')

#     except requests.exceptions.HTTPError as errh:
#         frappe.msgprint(f'HTTP Error: {errh}')
#     except requests.exceptions.ConnectionError as errc:
#         frappe.msgprint(f'Error Connecting: {errc}')
#     except requests.exceptions.Timeout as errt:
#         frappe.msgprint(f'Timeout Error: {errt}')
#     except requests.exceptions.RequestException as err:
#         frappe.msgprint(f'Request Exception: {err}')



####################################################################################################################

# Aisensy integration for Sales Order


@frappe.whitelist(allow_guest=True)
def aisensy_sales_order(docname,customer_id, customer,from_date,to_date,total,new_mobile,razorpay_payment_link):
    try:
        # frappe.msgprint(from_date)
        # pass
        ai_sensy_api = frappe.get_doc('Ai Sensy Api')

        application_url = ai_sensy_api.application_url
        ai_sensy_url = ai_sensy_api.ai_sensy_url
        ai_sensy_api1 = ai_sensy_api.ai_sensy_api
        # Check if Sales Order exists
        if not frappe.get_value('Sales Order', docname):
            frappe.msgprint(_("Sales Order {0} not found.").format(docname))
            return

        # Fetch the Sales Order document
        sales_invoice = frappe.get_doc('Sales Order', docname)
        erpnext_url = application_url
        # Replace the following URL with the actual AI Sensy API endpoint
        sensy_api_url = ai_sensy_url

        sales_order_url = frappe.utils.get_url(
            f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en"
        )
        
        # pdf_url = f"{erpnext_url}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format=Standard"

        # pdf_url1 = frappe.utils.get_url(
        #     f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format=Standard"
        # )

        # Example payload to send to the AI Sensy API
        payload = {
            "apiKey": ai_sensy_api1,  # Replace with your actual API key
            "campaignName": "lsa_saleorder_invoice_with_payment_link",
            "destination": new_mobile,
            "userName": customer,
            "templateParams": [
                customer,
                from_date,
                to_date,
                # format_date(from_date, "dd-mmm-yyyy"),  # Format from_date
                # format_date(to_date, "dd-mmm-yyyy"),
                total,
                razorpay_payment_link
            ],
            "media": {
                "url": sales_order_url,
                # "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "filename": docname
            }
        }

        # Make a POST request to the AI Sensy API
        response = requests.post(sensy_api_url, json=payload)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Log the API response for reference
            frappe.logger().info(f"AI Sensy response: {response.text}")

            # You can update the Sales Invoice or perform other actions based on the API response
            # sales_invoice.custom_field = response.json().get('result')
            # sales_invoice.save()

            frappe.msgprint(_("WhatsApp Message Sent successfully : {0}").format(response.text))
            whatsapp_message_log = frappe.new_doc('WhatsApp Message Log')
            whatsapp_message_log.sales_order = docname
            whatsapp_message_log.customer = customer_id
            whatsapp_message_log.sender = frappe.session.user  # Add the sender information
            whatsapp_message_log.send_date = frappe.utils.now_datetime()
            # whatsapp_message_log.from_date = from_date
            # whatsapp_message_log.to_date = to_date
            whatsapp_message_log.total_amount = total
            whatsapp_message_log.mobile_no = new_mobile
            whatsapp_message_log.razorpay_payment_link = razorpay_payment_link
            whatsapp_message_log.insert(ignore_permissions=True)
        else:
            # Log the error and provide feedback to the user
            frappe.logger().error(f"Sensy API Error: {response.text}")
            frappe.msgprint(_("WhatsApp message failed to send!. Please try again Later."))

    except requests.exceptions.RequestException as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Network error: {e}")
        frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later."))

    except Exception as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Custom Button Script Error: {e}")
        frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later."))


###########################################################################################################################


    #Razorpay Payment Link For Sales Order
import razorpay


@frappe.whitelist()
def create_razorpay_payment_link_sales_order(amount, invoice_name,customer,customer_name,from_date,to_date,actual_amount):
    # Your Razorpay API key and secret
    razorpay_api = frappe.get_doc('Razorpay Api')

    razorpay_api_url = razorpay_api.razorpay_api_url
    razorpay_api_key = razorpay_api.razorpay_api_key
    razorpay_api_secret = razorpay_api.razorpay_secret
    
    
    razorpay_key_id = razorpay_api_key
    razorpay_key_secret = razorpay_api_secret

    # Specify the custom Razorpay API URL
    custom_razorpay_api_url = razorpay_api_url

    # Convert the amount to an integer (representing paise)
    amount_in_paise = int(float(amount) * 100)
    # print("Testing==============")
    # Create a Razorpay order
    order_params = {
        "amount": amount_in_paise,
        "currency": "INR",
        # "accept_partial": "0",
        # "first_min_partial_amount": 100,
        "description": f"Sales order for the period from {from_date} to {to_date}",
        "notes": {
            "invoice_name": invoice_name
        },
        # "accept_partial": False,
        # "expire_by": 1691097057,
        "reference_id": invoice_name,
        "callback_url": f"https://online.lsaoffice.com/api/method/lsa.pankaj1.get_razorpay_payment_details?customer={customer}&actual_amount={actual_amount}",
        "callback_method": "get"
    }
 
    try:
        # Use the requests library to send a POST request
        order = requests.post(
            custom_razorpay_api_url,
            json=order_params,
            auth=(razorpay_key_id, razorpay_key_secret)  # Add authentication here
        )

        # Check if the request was successful (status code 2xx)
        order.raise_for_status()

        # Get the JSON response
        response_json = order.json()

        # Extract short_url from the response
        short_url = response_json.get('short_url')

        # Optionally, you can store custom_payment_link in a database or use it as needed

        # Update the Sales Invoice document with the short_url
        doc = frappe.get_doc('Sales Order', invoice_name)
        doc.custom_razorpay_payment_url = short_url
        doc.save()

        frappe.msgprint(f'Successfully created Razorpay order. Short URL: {short_url}')
       

    except requests.exceptions.HTTPError as errh:
        #frappe.msgprint(f'HTTP Error: {errh}')
        frappe.msgprint('Failed to generate the Razorpay payment link.')
    except requests.exceptions.ConnectionError as errc:
        #frappe.msgprint(f'Error Connecting: {errc}')
        frappe.msgprint('Failed to generate the Razorpay payment link.')
    except requests.exceptions.Timeout as errt:
        #frappe.msgprint(f'Timeout Error: {errt}')
        frappe.msgprint('Failed to generate the Razorpay payment link.')
    except requests.exceptions.RequestException as err:
        #frappe.msgprint(f'Request Exception: {err}')
        frappe.msgprint('Failed to generate the Razorpay payment link.')




@frappe.whitelist(allow_guest=True)
def get_razorpay_payment_details(razorpay_payment_link_id,razorpay_payment_link_reference_id,customer,actual_amount):
    try:
        razorpay_api = frappe.get_doc('Razorpay Api')

        # razorpay_api_url = razorpay_api.razorpay_api_url
        razorpay_api_key = razorpay_api.razorpay_api_key
        razorpay_api_secret = razorpay_api.razorpay_secret
        
        
        razorpay_key_id = razorpay_api_key
        razorpay_key_secret = razorpay_api_secret

        # Specify the custom Razorpay API URL
        custom_razorpay_api_url = f'https://api.razorpay.com/v1/payment_links/{razorpay_payment_link_id}'

        # Make a request to the custom Razorpay API URL
        response = requests.get(
            custom_razorpay_api_url,
            auth=(razorpay_key_id, razorpay_key_secret)  # Add authentication here
        )

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            razorpay_response = response.json()
            # Navigate through the JSON structure to extract amount_paid
            # amount_paid = razorpay_response.get('amount_paid')
            # final_amount = int(float(amount_paid) / 100)
            payments = razorpay_response.get('payments')
            if payments:
                most_recent_payment = max(payments, key=lambda x: x['created_at'])
                # payment_id = most_recent_payment.get('payment_id')
                payment_amount = most_recent_payment.get('amount')
                # payment_status = most_recent_payment.get('status')
                final_amount = int(float(payment_amount) / 100)
                # print(final_amount)
                # frappe.msgprint(final_amount)
                create_payment_entry(final_amount,razorpay_payment_link_reference_id,customer,razorpay_payment_link_id,actual_amount)
                return render_payment_success_page(final_amount,razorpay_payment_link_id)
                # You can now use this information as needed, such as updating your database, notifying users, etc.
            else:
                frappe.msgprint('Amount Paid not found in the response.')
                
        else:
            frappe.msgprint(f'Request failed with status code: {response.status_code}')
            frappe.msgprint(f'Response text: {response.text}')
    except Exception as e:
        frappe.msgprint(f'Error: {e}')


def render_payment_success_page(final_amount,razorpay_payment_link_id):
    # HTML template for the success page
    success_html = f"""
    <html>
        <head>
            <title>Payment Success!!!!</title>
            <style>
                .btn.btn-primary.btn-sm.btn-block {{
                    display: none !important;
                }}
                
            </style>
        </head>
        <body>
            <h1>Payment Successful</h1>
            <p>Transaction: {razorpay_payment_link_id}</p>
            <p>Amount: {final_amount}</p>
            <!-- Add any additional information you want to display -->
        </body>
    </html>
    """
    
    
    frappe.respond_as_web_page("Payment Success", success_html)






# @frappe.whitelist(allow_guest=True)
def create_payment_entry(final_amount, razorpay_payment_link_reference_id, customer, razorpay_payment_link_id, actual_amount):
    try:
        # print("actual_amount=", actual_amount)
        # print("customer=", customer)
        # print("razorpay_payment_link_reference_id=", razorpay_payment_link_reference_id)
        # print("===========")
        # print(f"User: {frappe.session.user}")
        # print(f"User Roles: {frappe.get_roles(frappe.session.user)}")
        frappe.set_user("Administrator")
        
        # Check if entry exists in the database. If yes, directly return.
        if is_payment_entry_exists(razorpay_payment_link_id):
            frappe.msgprint(_('Payment Entry already exists. Skipping creation.'))
            return
            
        # Create a Payment Entry
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "paid_from": "Debtors - IND",
            "paid_to": "Razorpay - IND",
            "received_amount": "INR",
            "base_received_amount": "INR",
            "paid_amount": int(final_amount),
            "references": [
                {
                    "reference_doctype": "Sales Order",
                    "reference_name": razorpay_payment_link_reference_id,
                    "allocated_amount": int(actual_amount)
                }
            ],
            "reference_date": today(),
            "account": "Accounts Receivable",
            "party_type": "Customer",
            "party": customer,
            "mode_of_payment": "Razorpay",
            "reference_no": razorpay_payment_link_id
        }, ignore_permissions=True)
        
        # print("=============STARTED=============")

        # Save the Payment Entry
        payment_entry.insert(ignore_permissions=True)
        frappe.db.commit()
        # print("=============ENDED=============")
        frappe.set_user("Guest")

    except frappe.exceptions.ValidationError as e:
        frappe.msgprint(_('Error creating Payment Entry: {0}').format(str(e)))

# Rest of your code...


def is_payment_entry_exists(reference_id):
    # Check if a Payment Entry with the given reference already exists
    # Replace with your actual logic to check if a Payment Entry exists
    # For example, you can use frappe.get_value to check if a record with the given reference exists
    existing_payment_entry = frappe.get_value("Payment Entry", {"reference_no": reference_id})

    return bool(existing_payment_entry)






##################################################################

# Gst monthly filling


# from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def fetch_gstfile_records():
    try:
        # Fetch records from Gstfile with filter gst_type = 'regular'
        records = frappe.get_all("Gstfile", filters={"gst_type": "regular"}, fields=["gst_number"])
        # frappe.msgprint(records)
        return records
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in fetch_gstfile_records")
        return None
    
    
##############################################################################

# IT Assessess Create manual Record


# from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def create_it_assessee_manual_record(yearly_report, current_form_name):
    try:
        # Your logic to create a new record in 'IT Assessee Filing Data'
        filing_data_doc = frappe.new_doc('IT Assessee Filing Data')
        filing_data_doc.ay = yearly_report
        filing_data_doc.it_assessee_file = current_form_name
        filing_data_doc.save()

        return True  # Return True if the operation is successful
    except Exception as e:
        frappe.log_error(f"Error in creating IT Assessee Filing Data: {str(e)}")
        return False  # Return False if there's an error
    
    
    
##############################################################################

# In sales order Fetch service from master




@frappe.whitelist()
def fetch_services(c_id=None):
    all_services = frappe.get_all("Customer Chargeable Doctypes")
    c_services=[]
    for service in all_services:
        # print(service["name"])
        # if service["name"] in ("IT Assessee File","Gstfile"):
            # print(service["name"])
        c_services_n= (frappe.get_all(
            service["name"], 
            filters={'customer_id': c_id,"enabled":1},
            fields=["name","service_name","hsn_code","description","customer_id","current_recurring_fees"]))
        c_services+=list(c_services_n)
            # for c_service in c_services_n:
            #   pass
    print(c_services)
    
    if c_services:
        # For demonstration purposes, let's just send back a response.
        data = c_services
        return data
    else:
        return "No data found for the given parameters."



#############################################################################################

import frappe
from datetime import datetime
import calendar
 
 
 
 
def cron():
    auto_gen_so_for_subscribers()
    # pass
    
        
 
        
        
def auto_gen_so_for_subscribers():
 
    subscriptions = frappe.get_all("Customer Subscriptions Plan",
    filters={"status":"Active"},
    fields=["name","customer_id","subscription_start_date","action_frequency","notification","whatsapp","email"])
 
    monthly_subscriptions=[i for i in subscriptions if i["action_frequency"]=="Monthly"]
 
    for subscriber in monthly_subscriptions:
        c_id=subscriber["customer_id"]
 
        current_date = datetime.now().date()
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        last_day_of_month = datetime(current_date.year, current_date.month, last_day)
 
        s_id=subscriber["name"]
        subscription_services = frappe.get_all("Subscription Item",
            filters={"parent":s_id},
            fields=["services_name","hsn_code","qty","rate"])
 
        items_list=[]
        qtyy=0
        amt=0.00
        for service in subscription_services:
            items_list+=[
                    {
                    "item_code": service["services_name"],
                    "gst_hsn_code": service["hsn_code"],
                    "qty": service["qty"],
                    "rate":service["rate"]
                    }
                    ]
            qtyy+=service["qty"]
            amt+=service["rate"]
     
 
        sales_order = frappe.get_doc({"doctype": "Sales Order", "customer": c_id,
        "transaction_date":current_date,"custom_so_from_date":current_date,
        "custom_so_to_date":last_day_of_month,"total_qty":qtyy,"total":amt,
        "items": items_list
        })
        sales_order.insert()
 
  
  
  
  ###############################################################################################
  
  # Issue to Task Creation


@frappe.whitelist()
def task_with_issue_creation(i_id=None):
    issue = frappe.get_last_doc("Issue", filters={"name": i_id})

    if not issue:
        return f"Issue {i_id} not found"

    issue_task = frappe.get_all("Task", filters={"issue": i_id})

    if issue_task:
        return f"Task already created for Issue {i_id}"

    task = frappe.get_doc({
        "doctype": "Task",
        "subject": issue.subject,
        "custom_customer_id": issue.customer,
        "priority": issue.priority,
        "issue": issue.name,
        "project": "PROJ-0019",
        "description": issue.description,
        "custom_task_type": issue.issue_type,
    })

    task.insert()

    print(issue.subject)

    return f"New Task created for Issue {i_id}"
    
    
    
###############################################################################################
  
# Aisensy integration for Sales Order Without Payment Link

@frappe.whitelist(allow_guest=True)
def aisensy_sales_order_wo_link(docname,customer_id, customer,from_date,to_date,total,new_mobile,advance_paid):
    try:
        amount_pending=float(total) - float(advance_paid)
        company_account_details="Template Awaited"
        # frappe.msgprint(from_date)
        # pass
        ai_sensy_api = frappe.get_doc('Ai Sensy Api')

        application_url = ai_sensy_api.application_url
        ai_sensy_url = ai_sensy_api.ai_sensy_url
        ai_sensy_api1 = ai_sensy_api.ai_sensy_api
        # Check if Sales Order exists
        if not frappe.get_value('Sales Order', docname):
            frappe.msgprint(_("Sales Order {0} not found.").format(docname))
            return

        # Fetch the Sales Order document
        # sales_invoice = frappe.get_doc('Sales Order', docname)
        # erpnext_url = application_url

        # Replace the following URL with the actual AI Sensy API endpoint
        sensy_api_url = ai_sensy_url

        sales_order_url = frappe.utils.get_url(
            f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={docname}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en"
        )

        # Example payload to send to the AI Sensy API
        payload = {
            "apiKey": ai_sensy_api1,  # Replace with your actual API key
            "campaignName": "lsa_saleorder_invoice",
            "destination": new_mobile,
            "userName": customer,
            "templateParams": [
                customer,
                from_date,
                to_date,
                # format_date(from_date, "dd-mmm-yyyy"),  # Format from_date
                # format_date(to_date, "dd-mmm-yyyy"),
                total,
                advance_paid,
                amount_pending,
                company_account_details,
            ],
            "media": {
                "url": sales_order_url,
                # "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "filename": docname
            }
        }

        # Make a POST request to the AI Sensy API
        response = requests.post(sensy_api_url, json=payload)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Log the API response for reference
            frappe.logger().info(f"AI Sensy response: {response.text}")

            # You can update the Sales Invoice or perform other actions based on the API response
            # sales_invoice.custom_field = response.json().get('result')
            # sales_invoice.save()

            frappe.msgprint(_("WhatsApp Message Sent successfully : {0}").format(response.text))
            whatsapp_message_log = frappe.new_doc('WhatsApp Message Log')
            whatsapp_message_log.sales_order = docname
            whatsapp_message_log.customer = customer_id
            whatsapp_message_log.sender = frappe.session.user  # Add the sender information
            whatsapp_message_log.send_date = frappe.utils.now_datetime()
            # whatsapp_message_log.from_date = from_date
            # whatsapp_message_log.to_date = to_date
            whatsapp_message_log.total_amount = total
            whatsapp_message_log.mobile_no = new_mobile
            whatsapp_message_log.razorpay_payment_link = "Without Link"
            whatsapp_message_log.insert(ignore_permissions=True)
        else:
            # Log the error and provide feedback to the user
            frappe.logger().error(f"Sensy API Error: {response.text}")
            frappe.msgprint(_("WhatsApp message failed to send!. Please try again Later."))

    except requests.exceptions.RequestException as e:
        # Log the exception and provide feedback to the user
        print(e)
        frappe.logger().error(f"Network error: {e}")
        frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later.",e))

    except Exception as e:
        # Log the exception and provide feedback to the user
        print(e)
        frappe.logger().error(f"Custom Button Script Error: {e}")
        frappe.msgprint(_("An error occurred while WhatsApp Message. Please try again Later.",e))
    
    
    
    
    
    
    


    
    
    
    

