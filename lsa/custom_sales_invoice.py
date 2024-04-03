import frappe
import requests
import time



@frappe.whitelist()
def create_sales_invoice(so_id=None):  
	so_fields=["customer","customer_name","total","total_qty",
				"taxes_and_charges","total_taxes_and_charges","grand_total","rounding_adjustment",
				"rounded_total","in_words","advance_paid","apply_discount_on",
				"additional_discount_percentage","discount_amount"]       
	so_list=frappe.get_all("Sales Order",filters={"name":so_id},fields=so_fields)
	if so_list: 
		# so_doc=frappe.get_doc("Sales Order",so_id)       
		
		
		items_fields=["item_code","item_name","description","gst_hsn_code","qty","uom","rate","amount",
				"gst_treatment","net_rate","taxable_value","net_amount"]

		tax_fields=["charge_type","description","account_head","included_in_print_rate","cost_center",
				"rate","account_currency","base_tax_amount","tax_amount","tax_amount_after_discount_amount",
				"base_total"]

		si_dict={}
		si_dict["doctype"]= "Sales Invoice"
		for so_field in so_fields:
			si_dict[so_field]=so_list[0][so_field] 
		si_dict["outstanding_amount"]=0.00
		
		items_list=[]
		so_items=frappe.get_all("Sales Order Item",filters={"parent":so_id},fields=items_fields)
		for so_item in so_items:
			item_dict={}
			for field in items_fields:
				item_dict[field]=so_item[field]
			item_dict["sales_order"]=so_id
			items_list.append( item_dict)

		tax_items_list=[]
		tax_items=frappe.get_all("Sales Taxes and Charges",filters={"parent":so_id},fields=tax_fields)
		for tax_item in tax_items:
			tax_dict={}
			for field in tax_fields:
				tax_dict[field]=tax_item[field]
			tax_items_list.append(tax_dict)


		
		si_dict["items"]=items_list
		si_dict["taxes"]=tax_items_list

		si_doc = frappe.get_doc(si_dict)
		
		si_doc.insert()


		return "SI created Successfully"
		

 
@frappe.whitelist()
def send_whatsapp_message(sales_invoice,new_mobile):
    try:
        resp={}
        # Check if the mobile number has 10 digits
        if len(new_mobile) != 10:
            frappe.msgprint("Please provide a valid 10-digit mobile number.")
            return
        
        instance_id="609bc2d1392a635870527076"
 
        message = f'''Dear Test,
 
Your Sale Order for [from_date] to [to_date] period is due for amount of Rs [total]/- Kindly pay on below bank amount details
 
Our Bank Account
Lokesh Sankhala and ASSOSCIATES
Account No = 73830200000526
IFSC = BARB0VJJCRO
Bank = Bank of Baroda,JC Road,Bangalore-560002
UPI id = LSABOB@UPI
Gpay / Phonepe no = 9513199200
 
Call us immediately in case of query.
 
Best Regards,
LSA Office Account Team
accounts@lsaoffice.com'''
        
        kvp={"doctype":"Custom DocPerm","parent":"Sales Invoice","parentfield":"permissions","parenttype":"DocType",
             "idx":0,"permlevel":0,"role":"Guest","read":0,"write":0,"submit":0,"cancel":0,
             "delete":0,"amend":0,"create":0,"report":0,"export":0,"import":0,"share":0,"print":1,"email":0,
             "if_owner":0,"select":0,}
        # guest_doc_perm = frappe.get_doc(kvp)
        # guest_doc_perm.insert()
        # time.sleep(5)
        
        if (instance_status(instance_id) ):
            try:
                link = frappe.utils.get_url(f"https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={sales_invoice}&format=Sales%20Order%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/{sales_invoice}.pdf")
                # link = "https://online.lsaoffice.com/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name=LSA%2F23-24%2F000060&format=Sales%20Invoice%20Format&no_letterhead=0&letterhead=LSA&settings=%7B%7D&_lang=en/Invoice.pdf"
    
                url = "https://wts.vision360solutions.co.in/api/sendFileWithCaption"
                params = {
                    "token": instance_id,
                    "phone": f"91{new_mobile}",
                    "message": message,
                    "link": link
                }
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
                response_data = response.json()
                if(True):

                    # print(response_data)
                    frappe.logger().info(f"Sales Invoice response: {response.text}")

                    resp["msg"]="WhatsApp message sent successfully"
                else:
                    resp["msg"]=("API Error sending WhatsApp message")
            except Exception as er:
                 resp["msg"]=str(er)
            # time.sleep(10)
            # per_name=guest_doc_perm.name
            # resp["perm"]=per_name
            # frappe.delete_doc('Custom DocPerm', per_name)
        else:
            resp["msg"]=("WhatsApp API Instance not active")
        return resp
 
 
    except requests.exceptions.RequestException as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Network error: {e}")
        frappe.msgprint(f"Error: {e}")
 
    except Exception as e:
        # Log the exception and provide feedback to the user
        frappe.logger().error(f"Error: {e}")
        frappe.msgprint(f"Error: {e}")
 
 
 
 
def instance_status(instance_id):
    try:
        # Define the API endpoint URL with the token placeholder
        api_endpoint = 'https://wts.vision360solutions.co.in/api/qrCodeLink?token={{instance_id}}'
 
        # Replace {{instance_id}} with the actual token
        api_endpoint = api_endpoint.replace('{{instance_id}}', instance_id)
 
        # Make a GET request to the API endpoint
        response = requests.get(api_endpoint)
        response.raise_for_status()  # Raise an error for HTTP errors (status codes other than 2xx)
 
        # Parse the JSON response
        json_data = response.json()
 
        # Extract data from JSON
        instance_data = json_data.get('data')  # Use .get() to safely get the 'data' key
 
        # Check if instance_data is a dictionary
        return isinstance(instance_data, dict)
 
    except requests.RequestException as e:
        frappe.log_error(f"Error in storing data: {e}")
        return False  # Return False if there's an error

    
 

