# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FilingWorkingNote(Document):
	pass
@frappe.whitelist()
def update_filing_note(note_id, notes, updated_at):
    # Fetch the existing note
    note = frappe.get_doc('Filing Working Note', note_id)
    
    # Update the note and the updated_at field
    note.notes = notes
    note.updated_at = updated_at
    note.save()
    return 'Filing note updated successfully!'