# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = [
			# Customer details columns
			{"label": "Bank Transaction", "fieldname": "name", "fieldtype": "Link", "options": "Bank Transaction", "width": 100, },
			{"label": "Transaction Date", "fieldname": "date", "fieldtype": "Date", "width": 120, },
			
			{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100, },
			{"label": "Deposit", "fieldname": "deposit", "fieldtype": "Currency", "width": 100, },
			{"label": "Withdrawal", "fieldname": "withdrawal", "fieldtype": "Currency", "width": 100, },
			

			{"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Data", "width": 100, },
			{"label": "Reference Number", "fieldname": "reference_number", "fieldtype": "Data", "width": 100, },
			
			{"label": "Allocated Amount", "fieldname": "allocated_amount", "fieldtype": "Currency", "width": 80, },
			{"label": "Unallocated Amount", "fieldname": "unallocated_amount", "fieldtype": "Currency", "width": 80, },


			{"label": "Bank Account", "fieldname": "bank_account", "fieldtype": "Data", "width": 100, },
			
			{"label": "Party Type", "fieldname": "party_type", "fieldtype": "Data", "width": 100, },
			{"label": "Party", "fieldname": "party", "fieldtype": "Data", "width": 100, },
			{"label": "Party Name", "fieldname": "party_name", "fieldtype": "Data", "width": 200, },
		]
	
	
	data = get_data(filters)
	
	html_card = f"""
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
    """
	return columns, data, html_card





def get_data(filters):
	data=[]
	#"Internal Transfer"
	bnk_transactions_child=frappe.get_all('Bank Transaction Payments',
								 	fields= ['payment_entry','parent'],
									filters= {'payment_document':"Payment Entry",
				   								"docstatus":1})
	
	bnk_transactions = frappe.get_all('Bank Transaction',
										fields=["name","date","status","deposit","withdrawal",
											"bank_account","reference_number","allocated_amount","unallocated_amount",],
										filters={'docstatus': 1},
										)
	bnk_transactions_child_list={}
	for btc in bnk_transactions_child:
		bnk_transactions_child_list[btc.parent]=btc.payment_entry

	pe_s=frappe.get_all('Payment Entry',
								 	fields= ["name","party_type",'party','party_name',"payment_type"],
									filters= {"docstatus":1})
	pe_list={}
	for pe in pe_s:
		pe_list[pe.name]=[pe.party_type,pe.party,pe.party_name,pe.payment_type]


	bnk_transactions_list=[]
	for bt in bnk_transactions:
		if bt.name in bnk_transactions_child_list:
			bt_temp=bt.copy()
			pe_temp=bnk_transactions_child_list[bt.name]
			bt_temp["payment_entry"]=pe_temp
			bt_temp["party_type"]=pe_list[pe_temp][0]
			bt_temp["party"]=pe_list[pe_temp][1]
			bt_temp["party_name"]=pe_list[pe_temp][2]
			print(filters.get("transaction_type"),pe_list[pe_temp][3])
			if filters.get("transaction_type") :
				if filters.get("transaction_type")==pe_list[pe_temp][3]:
					bnk_transactions_list.append(bt_temp)
			else:
				bnk_transactions_list.append(bt_temp)
			
	data=bnk_transactions_list
	return data
