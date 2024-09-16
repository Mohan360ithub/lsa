# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from lsa.custom_sales_order import so_payment_status
from lsa.custom_customer import get_customer_annual_fees


 
class ClientGroup(Document):
    def before_insert(self):
        response = customer_validation(self.is_primary)
        if not response["status"]:
            frappe.throw(f"{response['msg']}")
 
    def after_insert(self):
        cust = frappe.get_doc("Customer", self.is_primary)
        cust.custom_client_group = self.name
        cust.save()
    def before_save(self):
        if frappe.db.exists("Client Group",self.name):
            old_doc = frappe.get_doc("Client Group", self.name)
            if self.is_primary != old_doc.is_primary and self.enabled:
                customer = frappe.get_all("Customer",
                                        filters={"name": self.is_primary, "custom_client_group": self.name},
                                        )
                
                if not customer:
                    frappe.throw(f"The primary customer {self.is_primary} does not belong to the specified group {self.group_name}.")
            if not self.enabled :
                self.is_primary=None
                customer_in_group = frappe.get_all("Customer",
                                        filters={ "custom_client_group": self.name},
                                        )
                for customer in customer_in_group:
                    frappe.db.set_value('Customer', customer.name, 'custom_client_group', None)
        
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

 
# @frappe.whitelist()
# def fetch_customer_details(name):
#     customers = frappe.get_all('Customer', 
#                                filters={'custom_client_group': name}, 
#                                fields=['customer_name', 'custom_customer_status_', 'name'])
#     return customers


############################## Below code is validating current customer is not primary in client group ####################################################################
@frappe.whitelist()
def check_is_primary(customer_name,customer_groups):
    customer_groups_list = frappe.get_all('Client Group',filters={"is_primary":customer_name}, fields=['name', 'is_primary'])
    if customer_groups_list and customer_groups!=customer_groups_list[0].name:
        return True
    return False
 
################################################### Vatsal Code Start ################################################################

@frappe.whitelist()
def get_client_group_summary(group_id,customer_id=None):
    try:
        client_group = frappe.get_doc("Client Group", group_id)
        group_name = client_group.group_name if client_group else "Unknown Group"

        # Get all the client groups
        client_group_customers = frappe.get_all("Customer",filters={
                                                                    "custom_client_group":group_id,
                                                                    # "name":("not in",[customer_id]),
                                                                    },
                                                            fields=["name","customer_name","custom_customer_status_","custom_contact_person","custom_primary_mobile_no"],        
                                                            )

        # Initialize a dictionary to store the client group summary
        client_group_summary = {}

        # Loop through each client group
        for customer in client_group_customers:
            so_list = frappe.get_all("Sales Order",filters={
                                                            "customer":customer.name,
                                                            "docstatus":("not in",[2])
                                                            },)
            due_so_count=0
            due_so_amount=0.00
            for so in so_list:
                so_status=so_payment_status(so.name)
                if so_status["payment_status"]!="Cleared":
                    due_so_count+=1
                    due_so_amount+=so_status["balance_amount"]
            annual_fees=get_customer_annual_fees(customer.name)
            client_group_summary[customer.name] = {"customer_name":customer.customer_name,
                                                   "custom_contact_person":customer.custom_contact_person,
                                                   "custom_primary_mobile_no":customer.custom_primary_mobile_no,
                                                   "customer_status":customer.custom_customer_status_,
                                                   "due_so_count":due_so_count,
                                                   "due_so_amount":due_so_amount,
                                                   "annual_fees":annual_fees
                                                   }
        return {"status":True,"msg":"Client Group data fetched successfully!","client_group_summary":client_group_summary,"group_id": group_id,
            "group_name": group_name}
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to fetch client group summary")
        return {"status":False,"msg": f"Failed to fetch client group summary:{e}"}
    
################################################### Vatsal Code End ###################################################


