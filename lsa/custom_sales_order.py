import frappe
import requests
from frappe import _
from frappe.utils import today
from datetime import datetime



@frappe.whitelist()
def sync_sales_orders_followup(so_id=None):
    try:
        
        followup_values={"values":[],}
        if so_id:
            existing_followups=frappe.get_all("Customer Followup",
                                    fields=["name","sales_order_summary"])
            existing_so_followups=[i.name for i in existing_followups if so_id in i.sales_order_summary]
            # print(existing_sales_orders)
            if existing_so_followups:
                for existing_so_followup in existing_so_followups:
                    # print(existing_sales_order)
                    followup=frappe.get_doc("Customer Followup",existing_so_followup)


                    followup_values["values"]+=[[followup.customer_id,followup.name,
                                                followup.status,followup.total_remaining_balance,
                                                followup.followup_date,followup.next_followup_date,
                                                followup.executive_name,followup.followup_note]]
            #############################################################################################
            existing_payments=frappe.get_all("Payment Entry Reference",
                                              filters={"reference_name":so_id,"docstatus":1},
                                                fields=["name","creation","parent","total_amount","outstanding_amount",
                                                        "allocated_amount"])

            
            so_doc=frappe.get_doc("Sales Order",so_id)
            so_balance=so_doc.rounded_total
            payment_status = "Unpaid"
            existing_payments_list=[]
            for existing_payment in existing_payments:

                reference_date=''
                mode_of_payment=''
                existing_payment_entry=frappe.get_all("Payment Entry",
                                              filters={"name":existing_payment.parent},
                                                fields=["name","reference_date","mode_of_payment"])
                reference_date=existing_payment_entry[0].reference_date
                mode_of_payment=existing_payment_entry[0].mode_of_payment

                existing_payment_list=[existing_payment.parent,existing_payment.total_amount,
                                       existing_payment.outstanding_amount,existing_payment.allocated_amount,
                                       existing_payment.creation,reference_date,mode_of_payment]
                so_balance-=existing_payment.allocated_amount
                existing_payments_list.append(existing_payment_list)


            if so_balance == 0:
                payment_status = "Cleared"
            elif so_doc.rounded_total>so_balance > 0:
                payment_status = "Partially Paid"
            # print(existing_payments_list)
            return {"status":"Synced successfully.","followup_values":followup_values,"payment_values":existing_payments_list,"so_balance":so_balance,"payment_status":payment_status}
        # else:
        #     return {"status":"Synced successfully."}
    except Exception as e:
        frappe.msgprint(f"Error: {e}")
        return False


@frappe.whitelist()
def whatsapp_button(user_email=None):
    try:
        status = False
        user_roles = frappe.get_all('Has Role', filters={'parent': user_email}, fields=['role'])

        if user_email=="pankajsankhla90@gmail.com":
            user_roles = frappe.get_all('Has Role', filters={'parent': "Administrator"}, fields=['role'])

        # Extract roles from the result
        roles = [role.get('role') for role in user_roles]
        doc_perm_roles = ["LSA Accounts Manager","LSA Account Executive"]

        for role in roles:
            if role in doc_perm_roles:
                status = True
                break

        return {"status": status, "value": [roles]}

    except Exception as e:
        print(e)
        return {"status": "Failed"}



