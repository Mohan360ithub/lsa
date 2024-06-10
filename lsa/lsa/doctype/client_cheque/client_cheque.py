# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime,timedelta
import json


class ClientCheque(Document):
	def on_update(self):
		if self.total_amt!=(self.fees+self.others+self.tax):
			self.total_amt=(self.fees+self.others+self.tax)
			self.save()
		# elif self.bounced!=1 and self.total_amt!=(self.fees+self.others+self.tax):
		# 	self.total_amt=(self.fees+self.others+self.tax+self.bounce_charges)
		# 	self.save()

		if self.cheque_status=="Received" and (not self.calendar_date or not self.calendar_field):
			self.calendar_date=self.cheque_date
			self.calendar_field=f"{self.customer_id}\nTo Present"
			# self.calendar_field=f"<p style='color:blue;'>{self.customer_id}<br>To Present</p>"
			self.save()
		elif self.cheque_status=="Presented" and self.calendar_date==self.cheque_date:
			self.calendar_date=self.cheque_date + timedelta(3)
			self.calendar_field=f"{self.customer_id}\nTo check Credit"
			# self.calendar_field=f"<p style='color:red;'>{self.customer_id}<br>To check Credit</p>"
			self.save()
		elif self.cheque_status=="Cleared":
			self.calendar_date=datetime.now().date()
			self.calendar_field=f"{self.customer_id}\nCleared"
			# self.calendar_field=f"<p style='color:green;'>{self.customer_id}<br>Cleared</p>"
			self.save()
		elif self.cheque_status=="Bounced" and self.bounced!=1:
			self.bounced=1
			self.calendar_date=datetime.now().date()
			self.calendar_field=f"{self.customer_id}\nBounced"
			# self.calendar_field=f"<p style='color:green;'>{self.customer_id}<br>Cleared</p>"
			self.save()
		
		if self.cheque_status=="Bounced" and self.bounced==1 and self.cheque_submission_date_post_bounce and self.cheque_submission_date_post_bounce!=self.calendar_date:
			self.calendar_date=self.cheque_submission_date_post_bounce
			self.calendar_field=f"{self.customer_id}\nPresent Bounced"
			# self.calendar_field=f"<p style='color:green;'>{self.customer_id}<br>Cleared</p>"
			self.save()
		elif self.cheque_status=="Presented" and self.bounced==1 and self.cheque_submission_date_post_bounce and self.cheque_submission_date_post_bounce==self.calendar_date:
			self.calendar_date=self.cheque_submission_date_post_bounce + timedelta(3)
			self.calendar_field=f"{self.customer_id}\nTo check Bounced Credit"
			# self.calendar_field=f"<p style='color:green;'>{self.customer_id}<br>Cleared</p>"
			self.save()



@frappe.whitelist()
def get_client_cheque_events(start, end, filters=None):
    filters = json.loads(filters) if filters else []
    
    # Fetch events from Client Cheque doctype
    events = frappe.get_list('Client Cheque', fields=['name', 'calendar_field', 'calendar_date', 'cheque_status'])
    
    # Update each event with calendar specific fields
    for event in events:
        event.update({
            'title': event['calendar_field'],
            'start': event['calendar_date'],
            'end': event['calendar_date'],
            'status': event['cheque_status']
        })
    
    return events
