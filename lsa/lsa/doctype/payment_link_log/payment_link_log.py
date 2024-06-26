# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe,json
import requests,re,razorpay
from frappe.model.document import Document

class PaymentLinkLog(Document):
    pass

@frappe.whitelist()
def cancel_link(p_id=None):
    if p_id:
        payment_link = frappe.get_doc('Payment Link Log',p_id)
        razorpay_api_cancel = frappe.get_doc('Razorpay Api to cancel link')

        razorpay_api_key = razorpay_api_cancel.razorpay_api_key
        razorpay_api_secret = razorpay_api_cancel.razorpay_secret
        razorpay_api_key = razorpay_api_cancel.razorpay_api_key
        razorpay_api_secret = razorpay_api_cancel.razorpay_secret

        # Razorpay API endpoint for canceling a payment link
        api_url = razorpay_api_cancel.razorpay_url
        new_api_url = api_url.replace("link_id", payment_link.link_id)

        # # Set up headers with your API key and secret
        # headers = {
        #     'Content-Type': 'application/json',
        #     'Authorization': f'Basic {razorpay_api_key}:{razorpay_api_secret}'
        # }
        try:
            # Make a POST request to cancel the payment link
            # # response = requests.post(new_api_url, headers=headers)
            response = requests.post(new_api_url, 
                                        auth=(razorpay_api_key, razorpay_api_secret))

            # Check if the request was successful (HTTP status code 200)
            # client = razorpay.Client(auth=(razorpay_api_key, razorpay_api_secret))
            # print(client)
            # response=client.payment_link.cancel(id)

            # print(self.link_id)
            # response=client.payment.fetch(self.link_id)
            response_dict = response.json() 
            if response.status_code == 200:
                payment_link.enabled=0
                payment_link.save()
                
                sales_order_doc = frappe.get_doc('Sales Order',payment_link.sales_order)
                sales_order_doc.custom_razorpay_payment_url=None
                sales_order_doc.save()
                return "Payment link canceled successfully:"
            else:
                return f"Error canceling payment link. Status code: {response.status_code},{response_dict['error']['description']}"

        except requests.exceptions.RequestException as e:
            return "Error in Payment Link Log"



