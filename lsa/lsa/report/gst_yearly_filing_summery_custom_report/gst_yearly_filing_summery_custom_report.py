# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	columns = [
        # Customer details columns
       {"label": "CID", "fieldname": "customer_id", "fieldtype": "Link", "options": "Customer", "width": 100},
	   {"label": "ID", "fieldname": "id", "fieldtype": "Link", "options": "Gst Yearly Filing Summery", "width": 100},
	   {"label": "Company", "fieldname": "company", "fieldtype": "Data", "width": 200},
	   {"label": "Contact Person", "fieldname": "contact_person", "fieldtype": "Data", "width": 150},
        {"label": "GSTIN", "fieldname": "gstfile", "fieldtype": "Link", "options": "Gstfile", "width": 150},
		{"label": "GST Type", "fieldname": "gst_type", "fieldtype": "Data", "width": 110},
		{"label": "Non-Compliant", "fieldname": "non_compliant", "fieldtype": "Check", "width": 50},
		
        {"label": "FY", "fieldname": "fy", "fieldtype": "Link", "options": "Gst Yearly Summery Report", "width": 100},
        {"label": "Total Sales Taxable", "fieldname": "sales_total_taxable", "fieldtype": "Currency", "width": 130},
		{"label": "First Month of Filling", "fieldname": "fy_first_month_of_filling", "fieldtype": "Data", "width": 80},
		{"label": "Last Month of Filling", "fieldname": "fy_last_month_of_filling", "fieldtype": "Data", "width": 80},
        {"label": "Total Purchase Taxable", "fieldname": "purchase_total_taxable", "fieldtype": "Currency", "width": 130},
        {"label": "Total Tax Paid Amount", "fieldname": "tax_paid_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Total Interest Paid Amount", "fieldname": "interest_paid_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Total Penalty Paid Amount", "fieldname": "penalty_paid_amount", "fieldtype": "Currency", "width": 100},
		]

	data=get_data(filters)

	html_card=f'''

<script>
        document.addEventListener('click', function(event) {{
            // Check if the clicked element is a cell
            var clickedCell = event.target.closest('.dt-cell__content');
            if (clickedCell) {{
                // Remove highlight from previously highlighted cells
                var previouslyHighlightedCells = document.querySelectorAll('.highlighted-cell');
                previouslyHighlightedCells.forEach(function(cell) {{
                    cell.classList.remove('highlighted-cell');
                    cell.style.backgroundColor = ''; // Remove background color
                    cell.style.border = ''; // Remove border
                    cell.style.fontWeight = '';
                }});
                
                // Highlight the clicked row's cells
                var clickedRow = event.target.closest('.dt-row');
                var cellsInClickedRow = clickedRow.querySelectorAll('.dt-cell__content');
                cellsInClickedRow.forEach(function(cell) {{
                    cell.classList.add('highlighted-cell');
                    cell.style.backgroundColor = '#d7eaf9'; // Light blue background color
                    cell.style.border = '2px solid #90c9e3'; // Border color
                    cell.style.fontWeight = 'bold';
                }});
            }}
        }});



    
    </script>

'''
	return columns, data,html_card

def get_data(filters):
	data = []

	gst_yearly_filling_summery_filter={}
	gstfile_enabled=None
	if (filters.get("gst_status")):
		if (filters.get("gst_status"))=="GST Enabled":
			gstfile_enabled=1
		elif (filters.get("gst_status"))=="GST Disabled":
			gstfile_enabled=0

	if (filters.get("gst_file")):
		gst_yearly_filling_summery_filter["gst_file_id"] = filters["gst_file"]

	if (filters.get("gst_type")):
		gst_yearly_filling_summery_filter["gst_type"] = filters["gst_type"]

	if (filters.get("gst_yearly_summery_report_id")):
		gst_yearly_filling_summery_filter["gst_yearly_summery_report_id"]=filters.get("gst_yearly_summery_report_id")
	
	if (filters.get("customer_id")):
		gst_yearly_filling_summery_filter["customer_id"]=filters.get("customer_id")

	if (filters.get("non_compliant")):
		if (filters.get("non_compliant"))=="Non-Compliant":
			gst_yearly_filling_summery_filter["non_compliant"]=1
		elif (filters.get("non_compliant"))=="Compliant":
			gst_yearly_filling_summery_filter["non_compliant"]=0


	
	gst_yearly_filling_summery_s = frappe.get_all("Gst Yearly Filing Summery", 
											   filters=gst_yearly_filling_summery_filter,
											   fields=["name","gst_yearly_summery_report_id","gstin","gst_type","company","customer_id",
														"sales_total_taxable","purchase_total_taxable","tax_paid_amount",
														"interest_paid_amount","penalty_paid_amount","fy_first_month_of_filling",
														"fy_last_month_of_filling","contact_person","non_compliant"])
	
	for gst_yearly_filling_summery in gst_yearly_filling_summery_s:
		
		if gst_yearly_filling_summery:
			data_row = {
				"customer_id": gst_yearly_filling_summery.customer_id,
				"id":gst_yearly_filling_summery.name,
				"company": gst_yearly_filling_summery.company,
				"contact_person": gst_yearly_filling_summery.contact_person,
				"gstfile": gst_yearly_filling_summery.gstin,
				"gst_type":gst_yearly_filling_summery.gst_type,
				"non_compliant":gst_yearly_filling_summery.non_compliant,
				"fy": gst_yearly_filling_summery.gst_yearly_summery_report_id,
				"fy_first_month_of_filling": gst_yearly_filling_summery.fy_first_month_of_filling,
				"fy_last_month_of_filling": gst_yearly_filling_summery.fy_last_month_of_filling,
				"sales_total_taxable": gst_yearly_filling_summery.sales_total_taxable,
				"purchase_total_taxable": gst_yearly_filling_summery.purchase_total_taxable,
				"tax_paid_amount": gst_yearly_filling_summery.tax_paid_amount,
				"interest_paid_amount": gst_yearly_filling_summery.interest_paid_amount,
				"penalty_paid_amount": gst_yearly_filling_summery.penalty_paid_amount,
			}
			
			data.append(data_row)

	if filters.get("customer_status"):
		customer_list = frappe.get_all("Customer",filters={},fields=["name", "disabled"],)
		customer_list={cus.name:cus.disabled for cus in customer_list}
		customer_status = filters["customer_status"]
		new_data=[]
		if customer_status=="Enabled":
			for gst_file in data:
				if (not customer_list[gst_file["customer_id"]]) :
					new_data.append(gst_file)
		elif customer_status=="Disabled":
			for gst_file in data:
				if (customer_list[gst_file["customer_id"]]) :
					new_data.append(gst_file)
		data=new_data

	if gstfile_enabled is not None:
		gst_file_enabled = frappe.get_all("Gstfile", filters={"enabled":gstfile_enabled})
		gst_file_enabled=[i.name for i in gst_file_enabled]
		new_data=[]

		for gst_file in data:
			if (gst_file["gstfile"] in gst_file_enabled) :
				new_data.append(gst_file)
	
		data=new_data
	return data







