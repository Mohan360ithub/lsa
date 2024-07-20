# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe,json
import requests,re,razorpay
from frappe.model.document import Document

class PaymentLinkLog(Document):
    pass



@frappe.whitelist()
def sync_payment_details(link_id,p_id):
    try:
        # Fetch Razorpay API credentials from the Razorpay Api doctype
        admin_settings = frappe.get_doc('Admin Settings')
        razorpay_base_url = admin_settings.razorpay_base_url
        razorpay_key_id = admin_settings.razorpay_api_key
        razorpay_key_secret = admin_settings.get_password('razorpay_secret')
        razorpay_api_url=razorpay_base_url+"payment_links/"+link_id
        
        # Make a request to the Razorpay API to get the payment details
        response = requests.get(razorpay_api_url, auth=(razorpay_key_id, razorpay_key_secret))
        data = response.json()

        # Fetch the payment link document in Frappe
        payment_link_doc = frappe.get_doc('Payment Link Log', p_id)
        
        # Extract the relevant details from the response
        balance_amount = float(data.get('amount')) - float(data.get('amount_paid'))
        received_amount = data.get('amount_paid')
        payment_status = data.get('status')

        # Update the payment link document in Frappe
        payment_link_doc.received_amount = float(received_amount)/100
        payment_link_doc.balance_amount = payment_link_doc.link_total_amount - (float(received_amount)/100)
        
        # Update payment status based on the status from Razorpay
        if payment_status == 'paid':
            payment_link_doc.payment_status = "Paid"
        elif payment_status == 'partially_paid':
            payment_link_doc.payment_status = "Partially Paid"
        elif payment_status == 'cancelled':
            payment_link_doc.payment_status = "Cancelled"
        elif payment_status == 'expired':
            payment_link_doc.payment_status = "Expired"
            

        # Save the changes to the document
        payment_link_doc.save()

        # Return the details to the client script
        return {"status":True,"msg":"Payment Link status synced successfully"}
    except Exception as e:
        return {"status":False,"msg":f"Error syncing payment details: {str(e)}"}

@frappe.whitelist()
def sync_all_payment_details():
    payment_link_list = frappe.get_all('Payment Link Log', 
                                       filters={
                                                'payment_status':("in",["Created","Partially Paid"])
                                                },
                                        fields=["link_id","name"])
    count=0
    for payment_link in payment_link_list:
        resp=sync_payment_details(payment_link.link_id,payment_link.name)
        if resp.get('status'):
            count+=1
    msg="All Payment Link status synced successfully"
    if count!=len(payment_link_list):
        msg=f"{count} out of {len(payment_link_list)} Payment Link status synced successfully"
    return {"status":True,"msg":msg}

@frappe.whitelist()
def cancel_link(p_id=None):
    if p_id:
        payment_link = frappe.get_doc('Payment Link Log',p_id)

        admin_settings = frappe.get_doc('Admin Settings')
        razorpay_base_url = admin_settings.razorpay_base_url
        razorpay_key_id = admin_settings.razorpay_api_key
        razorpay_key_secret = admin_settings.get_password('razorpay_secret')
        razorpay_api_url=razorpay_base_url+"payment_links/"+payment_link.link_id+"/cancel"


        try:
            response = requests.post(razorpay_api_url, 
                                        auth=(razorpay_key_id, razorpay_key_secret))

            response_dict = response.json() 
            if response.status_code == 200:
                payment_link.payment_status="Cancelled"
                payment_link.save()
                
                sales_order_doc = frappe.get_doc('Sales Order',payment_link.sales_order)
                sales_order_doc.custom_razorpay_payment_url=None
                sales_order_doc.save()
                return "Payment link canceled successfully:"
            else:
                return f"Error canceling payment link. Status code: {response.status_code},{response_dict['error']['description']}"

        except requests.exceptions.RequestException as e:
            return "Error in Payment Link Log"






