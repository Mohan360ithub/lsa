# Copyright (c) 2023, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WhatsAppMessageLog(Document):
	pass


def wa_history_for_doctype_records(doctype, doc_id):
    try:
        # Fetching message details from 'Message Detail' doctype
        message_details = frappe.get_all(
            'Message Detail',
            filters={'type': doctype, 'document_id': doc_id},
            fields=['name', 'parent', 'mobile_number']
        )

        # Create a dictionary mapping parents to message details
        message_parent = {i.parent: (i.name, i.mobile_number) for i in message_details}

        # Fetching WhatsApp message log details
        message_parent_details = frappe.get_all(
            'WhatsApp Message Log',
            filters={'name': ('in', list(message_parent.keys()))},
            fields=['name', 'sender', 'send_date', 'message_type']
        )

        # Prepare the final list of message details
        doc_messages_details = []
        for msg_detail in message_parent_details:
            doc_messages_details.append({
                "whatsapp_message_log": msg_detail.name,
                "sender": msg_detail.sender,
                "send_date": msg_detail.send_date,
                "mobile_number": message_parent[str(msg_detail.name)][1],
                "message_type": msg_detail.message_type,
                "child_table_ref": message_parent[str(msg_detail.name)][0],
            })

        return {"status": True, "doc_messages_details": doc_messages_details}

    except Exception as e:
        frappe.log_error(f"Failed to get WhatsApp Message Log for doctype: {doctype}, doc_id: {doc_id}", str(e))
        return {
            "status": False,
            "msg": f"Failed to get WhatsApp Message Log for doctype: {doctype}, doc_id: {doc_id}. Error: {e}"
        }

