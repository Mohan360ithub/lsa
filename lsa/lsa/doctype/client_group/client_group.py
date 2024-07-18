# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


 
class ClientGroup(Document):
    def before_insert(self):
        response = customer_validation(self.is_primary)
        if not response["status"]:
            frappe.throw(f"{response['msg']}")
 
    def after_insert(self):
        cust = frappe.get_doc("Customer", self.is_primary)
        cust.custom_client_group = self.name
        cust.save()
 
def customer_validation(customer_id):
    try:
        # Get Customer document
        customer = frappe.get_doc('Customer', customer_id)
 
        # Check if custom_client_group field exists, create if it doesn't
        if customer.custom_client_group:
            # Check if customer is already linked to another group
            if customer.custom_client_group:
                # Throw an error if customer is linked to another group
                return {"status":False,"msg":f"The Customer is already Linked with Group ID {customer.custom_client_group}"}
        return {"status":True,"msg":"Customer added to group successfully."}
    
    except Exception as e:
        frappe.log_error(f"Error adding customer to group: {e}")
        return {"status":False,"msg":f"Error adding customer to group: {e}"}
 
############################ Below code is Add customer button server script ###################
 
import frappe
from frappe import _
 
@frappe.whitelist()
def add_customer_to_group(customer_id, group_name):
    try:
        # Get Customer document
        customer = frappe.get_doc('Customer', customer_id)
 
        # Check if custom_client_group field exists, create if it doesn't
        if customer.custom_client_group:
                frappe.throw(_(f"The Customer is already Linked with Group ID {customer.custom_client_group}"))
 
        # Set the group_name for custom_client_group
        customer.custom_client_group = group_name
 
        # Save customer document
        customer.save()
 
        return _("Customer added to group successfully.")
    
    except Exception as e:
        frappe.log_error(f"Error adding customer to group: {e}")
        raise
 
################# Below code is make Ajax call to get the HTML table #########################
import frappe
 
@frappe.whitelist()
def fetch_customer_details(name):
    customers = frappe.get_all('Customer', 
                               filters={'custom_client_group': name}, 
                               fields=['customer_name', 'custom_customer_status_', 'name'])
    return customers


############################## Below code is validating current customer is not primary in client group ####################################################################
@frappe.whitelist()
def check_is_primary(customer_name,customer_groups):
    customer_groups_list = frappe.get_all('Client Group',filters={"is_primary":customer_name}, fields=['name', 'is_primary'])
    if customer_groups_list and customer_groups!=customer_groups_list[0].name:
        return True
    return False
 
