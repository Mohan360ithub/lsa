######################### Login Instance (connect now button) ###################################

import frappe
import requests
from frappe.model.document import Document
import json
from datetime import datetime

@frappe.whitelist()
def storing_the_qrcode(name=None):
    if True:

        whatsapp_instance_doc = frappe.get_doc("WhatsApp Instance",name)
        base_url = whatsapp_instance_doc.base_url
        instance_id=whatsapp_instance_doc.instance_id
        try:
            
            api_endpoint = base_url+'qrCodeLink?token='+instance_id

            # Make a GET request to the API endpoint
            response = requests.get(api_endpoint)
            response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)

            # Parse the JSON response
            json_data = response.json()
            qr_code_url = json_data.get('data')

            return qr_code_url  # Return the URL
        except requests.RequestException as e:
            frappe.log_error(f"Error generating QR code link: {e}")
            return None
        
################################# Syncing Instance #################################


@frappe.whitelist()
def sync_instance_data(name):
    try:
        whatsapp_instance_doc = frappe.get_doc("WhatsApp Instance",name)
        instance_id=whatsapp_instance_doc.instance_id
        base_url = whatsapp_instance_doc.base_url

        api_endpoint = base_url+'qrCodeLink?token='+instance_id

        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)

        # Parse the JSON response
        json_data = response.json()
        instance_data = json_data['data']

        # Convert the datetime string to the correct format
        if (type(instance_data) == dict):
            creation_time = datetime.strptime(instance_data['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
            creation_time_formatted = creation_time.strftime('%Y-%m-%d %H:%M:%S')
            expiry_date = datetime.strptime(instance_data['quotaValidity'], '%Y-%m-%dT%H:%M:%S.%fZ')
            expiry_date_formatted = expiry_date.strftime('%Y-%m-%d %H:%M:%S')

            whatsapp_instance_doc.connected_number = instance_data['connectedNumeber'] ##
            if whatsapp_instance_doc.connected_number != whatsapp_instance_doc.assigned_mobile_number:
                instance_id=whatsapp_instance_doc.instance_id

                # Attempt to disconnect the instance
                url = base_url+"logout"
                params = {"token": instance_id}
                response = requests.post(url, params=params)
                return {'status':False,"error": "You are connecting WhatsApp API with Invalid Number."}
            
            whatsapp_instance_doc.instance_name = instance_data['name']  ##
            whatsapp_instance_doc.remaining_credits = instance_data['quota'] ##
            whatsapp_instance_doc.webhook = instance_data['webhookEnabled'] ##
            whatsapp_instance_doc.expiry_date = expiry_date_formatted ##
            whatsapp_instance_doc.creation_time = creation_time_formatted ##
            whatsapp_instance_doc.credits_usage = instance_data['instanceUsage'] ##
            whatsapp_instance_doc.connection_status = instance_data['isLoggedIn'] ##
            whatsapp_instance_doc.today_credits_usage = instance_data['todayUsage'] ##
            whatsapp_instance_doc.save()
        else:
            whatsapp_instance_doc.connection_status = 0 ##
            whatsapp_instance_doc.save()


        return {'status':True,"msg": "WhatsApp Instance data stored successfully."}
    except requests.RequestException as e:
        frappe.log_error(f"Error in a storing data: {e}")
        return {'status':False,"msg": f"Failed to store WhatsApp Instance data.{e}"}


############################## Logout Instance code (Disconnect Now Button)#######################################



@frappe.whitelist()
def logout_instance(name):
    try:
        whatsapp_instance_doc = frappe.get_doc("WhatsApp Instance",name)
        instance_id=whatsapp_instance_doc.instance_id
        base_url = whatsapp_instance_doc.base_url

        # Attempt to disconnect the instance
        url = base_url = base_url+"/logout"
        params = {"token": instance_id}
        response = requests.post(url, params=params)
        
        response.raise_for_status() # Raise an error for HTTP errors (status codes other than 2xx)
        response=response.json()

        if "disconnected successfully" in response["message"]:
            whatsapp_instance_doc.connection_status = 0
            whatsapp_instance_doc.save()
            return {"message": "Instance disconnected successfully."}
        else:
            return {"message": "Error disconnecting."}
    
    except requests.RequestException as e:
        frappe.logger().error(f"Error sending WhatsApp message: {e}")
        raise


####################################################### Validating Instance #####################################################

# @frappe.whitelist()
def validate_whatsapp_instance(instance_name):
    try:
        whatsapp_instance_exists = frappe.db.exists('WhatsApp Instance', {'name': instance_name})
        if not whatsapp_instance_exists:
            return {"status": False, "msg": f"No WhatsApp instance found for {instance_name}"}
        
        
        

        sync_resp=sync_instance_data(instance_name)
        if not sync_resp["status"]:
            return {"status":False,"msg":f"An error occurred while syncing Whatsapp instance{instance_name}:{sync_resp['msg']}"}
        
        whatsapp_instance_doc = frappe.get_doc('WhatsApp Instance', instance_name)

        if not whatsapp_instance_doc.connection_status:
            return {"status": False, "msg": "Your WhatsApp Instance is not connected to the API server, please contact admin to connect it"}
        
        if not whatsapp_instance_doc.active:
            return {"status": False, "msg": "Your WhatsApp Instance is not Active, please contact admin to activate it"}
        
        return {"status": True, "msg": "WhatsApp instance is valid and active.", "whatsapp_instance_doc": whatsapp_instance_doc}
    except Exception as e:
        return {"status": False, "msg": f"An error occurred while validating Whatsapp instance{instance_name}: {e}"}
    
################################### WhatsApp Custom Message ######################################################################

def send_custom_whatsapp_message(whatsapp_instance_doc, mobile_number, message):

    if not mobile_number or not mobile_number.isnumeric() or len(mobile_number)!=10:
        return {"status": False, "msg": "Invalid mobile number"}
    
    url = whatsapp_instance_doc.base_url+"sendText"
        
    params = {
        "token": whatsapp_instance_doc.instance_id,
        "phone": f"91{mobile_number}",
        "message": message,
    }
    
    try:
        message_id=""
        response = requests.post(url, params=params)
        response.raise_for_status()
        response_data = response.json()
        message_id = response_data['data']['messageIDs'][0]

        if response_data.get('status') == 'success':
            
            return {"status": True, "msg": "WhatsApp message sent successfully", "message_id": message_id}
        else:
            return {"status": False, "msg": f"An error occurred while sending the WhatsApp message: {response_data}"}

    except requests.exceptions.RequestException as e:
        # frappe.log_error("An error occurred while sending the WhatsApp message. For {m_no}",f"{e}")
        return {"status": False, "msg": f"An error occurred while sending the WhatsApp message. For {mobile_number}: {e}"}

