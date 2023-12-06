import frappe
import requests
from frappe import _



@frappe.whitelist()
def fetch_sales_orders(cid):
    # Fetch sales orders based on the customer ID and docstatus
    sales_orders = frappe.get_list(
        'Sales Order',
        filters={'customer': cid, 'docstatus': ('in', ['0', '1'])},
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
def aisensy_sales_order(docname, customer,from_date,to_date,total,new_mobile,razorpay_payment_link):
    try:
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
                total,
                razorpay_payment_link
            ],
            "media": {
                "url": sales_order_url,
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
def create_razorpay_payment_link_sales_order(amount, invoice_name,customer,customer_name,from_date,to_date):
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

    # Create a Razorpay order
    order_params = {
        "amount": amount_in_paise,
        "currency": "INR",
        "accept_partial": True,
        "first_min_partial_amount": 100,
        "description": f"Sales order for the period from {from_date} to {to_date}",
        "notes": {
            "invoice_name": invoice_name
        },
        "accept_partial": True,
        # "expire_by": 1691097057,
        "reference_id": invoice_name,
        "callback_url": f"https://online.lsaoffice.com/api/method/lsa.pankaj1.get_razorpay_payment_details?customer={customer}",
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


# @frappe.whitelist(allow_guest=True)
# def razorpay_payment_callback():
#     try:
#         # You can validate the request, check the payment status, and extract necessary details
#         #data = frappe.local.request.form
#         data = {
#                 'status': 'captured',
#                 'razorpay_payment_link_id': razorpay_payment_link_id,  
#                 'short_url': 'https://example.com/razorpay-link',
            
#             }
#         # Check if the payment was successful (you need to customize this based on Razorpay response)
#         if data.get('status') == 'captured':
#             invoice_name = data.get('reference_id')  # Assuming reference_id contains the invoice_name
#             razorpay_payment_link_id = data.get('razorpay_payment_link_id')  # Assuming short_url is returned by Razorpay

#             # Call create_payment_entry only if the payment is successful
#             create_payment_entry(razorpay_payment_link_id)
#     except Exception as e:
#         frappe.logger().error(f'Razorpay callback error: {e}')



@frappe.whitelist()
def get_razorpay_payment_details(razorpay_payment_link_id,razorpay_payment_link_reference_id,customer):
    try:
        # Your Razorpay API key and secret
        razorpay_key_id = 'rzp_test_e664V0FP0zQy7N'
        razorpay_key_secret = 'QdnuRxUHrPGeiJc9lDTXYPO7'

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
            amount_paid = razorpay_response.get('amount_paid')
            final_amount = int(float(amount_paid) / 100)
            if amount_paid is not None:
                frappe.msgprint(final_amount)
                create_payment_entry(final_amount,razorpay_payment_link_reference_id,customer,razorpay_payment_link_id)
            else:
                frappe.msgprint('Amount Paid not found in the response.')
        else:
            frappe.msgprint(f'Request failed with status code: {response.status_code}')
            frappe.msgprint(f'Response text: {response.text}')
    except Exception as e:
        frappe.msgprint(f'Error: {e}')



# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_payment_entry(final_amount,razorpay_payment_link_reference_id,customer,razorpay_payment_link_id):
#     try:
#         # Create a Payment Entry
#         payment_entry = frappe.get_doc({
#             "doctype": "Payment Entry",
#             # "payment_type": "Receive",
#             # "posting_date": "2023-12-02",
#             # "company": "360ithub",  # Replace with your company name
#             "paid_from": "Debtors - IND",
#             "paid_to": "Cash - IND",
#             "received_amount":"INR",
#             "base_received_amount":"INR",
#             "paid_amount": final_amount,
#             "references": [
# 		    {
# 		      "reference_doctype": "Sales Order",
# 		      "reference_name": razorpay_payment_link_reference_id,
# 		      #"invoice_amount": 1200.00,
# 		      "allocated_amount": final_amount
# 		    }
# 		  ],
#             "reference_date": "2023-12-01",
#             "account": "Accounts Receivable",
#             "party_type": "Customer",
#             "party": customer,
#             "mode_of_payment": "Cash",
#             "reference_no": razorpay_payment_link_id
#         })

#         # Save the Payment Entry
#         payment_entry.insert(ignore_permissions=True)
#         frappe.db.commit()

#         # frappe.msgprint(_('Payment Entry created successfully for Invoice {0}').format(payment_entry.reference_name))

#     except frappe.exceptions.ValidationError as e:
#         frappe.msgprint(_('Error creating Payment Entry: {0}').format(str(e)))



import frappe
from frappe import _

@frappe.whitelist()
def create_payment_entry(final_amount, razorpay_payment_link_reference_id, customer, razorpay_payment_link_id):
    try:
        # Create a Payment Entry
        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "paid_from": "Debtors - IND",
            "paid_to": "Cash - IND",
            "received_amount": "INR",
            "base_received_amount": "INR",
            "paid_amount": final_amount,
            "references": [
                {
                    "reference_doctype": "Sales Order",
                    "reference_name": razorpay_payment_link_reference_id,
                    "allocated_amount": final_amount
                }
            ],
            "reference_date": "2023-12-01",
            "account": "Accounts Receivable",
            "party_type": "Customer",
            "party": customer,
            "mode_of_payment": "Cash",
            "reference_no": razorpay_payment_link_id
        })

        # Save the Payment Entry
        payment_entry.insert(ignore_permissions=True)
        frappe.db.commit()

        # Format success message in HTML
        success_message = """
            Payment Entry created successfully for Invoice {0}
            <script>
                // Redirect to a new page with the success message
                frappe.msgprint("Payment Entry created successfully", __("Success"));
                setTimeout(function() {{
                    window.location.href = '/payment_success';
                }}, 1000); // Redirect after 2 seconds (adjust the delay as needed)
            </script>
        """

        # Show success message using frappe.msgprint
        frappe.msgprint(success_message)

    except frappe.exceptions.ValidationError as e:
            frappe.msgprint(_('Error creating Payment Entry: {0}').format(str(e)))








# import frappe
# from frappe import _

# @frappe.whitelist()
# def create_payment():
#     try:
#         # Create a Payment Entry
#         payment_entry = frappe.get_doc({
#             "doctype": "Payment Entry",
#             "paid_from": "Debtors - IND",
#             "paid_to": "Cash - IND",
#             "received_amount": "INR",
#             "base_received_amount": "INR",
#             "paid_amount": 10000,
#             "reference_date": "2023-12-01",
#             "account": "Accounts Receivable",
#             "party_type": "Customer",
#             "party": 20131037,
#             "mode_of_payment": "Cash",
#             "reference_no": 10002
#         })

#         # Save the Payment Entry
#         payment_entry.insert(ignore_permissions=True)
#         frappe.db.commit()

#         # Format success message in HTML
#         success_message = """
#             Payment Entry created successfully for Invoice {0}
#             <script>
#                 // Redirect to a new page with the success message
#                 frappe.msgprint("Payment Entry created successfully", __("Success"));
#                 setTimeout(function() {{
#                     window.location.href = '/payment_success';
#                 }}, 2000); // Redirect after 2 seconds (adjust the delay as needed)
#             </script>
#         """

#         # Show success message using frappe.msgprint
#         frappe.msgprint(success_message)

#     except frappe.exceptions.ValidationError as e:
#         # Format error message
#         error_message = """
#             Error creating Payment Entry: {0}
#         """.format(str(e))

#         # Show error message using frappe.msgprint
#         frappe.msgprint(error_message)
