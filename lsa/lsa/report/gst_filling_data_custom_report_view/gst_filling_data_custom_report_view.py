# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = [
        {"fieldname": "cid", "label": _("CID"), "fieldtype": "Link", "options": "Customer", "width": 100},
        {"fieldname": "customer_status", "label": _("Customer Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "name", "label": _("ID"), "fieldtype": "Link", "options": "Gst Filling Data", "width": 100},
        {"fieldname": "filing_status", "label": _("Filing Status"), "fieldtype": "Data", "width": 170},
        {"fieldname": "gstfile", "label": _("GSTIN"), "fieldtype": "Link", "options": "Gstfile", "width": 165},
        {"fieldname": "gstfile_enabled", "label": _("Gstfile Enable"), "fieldtype": "Check", "width": 50},
        {"fieldname": "company", "label": _("Company"), "fieldtype": "Data", "width": 220},
        {"fieldname": "mobile_no_gst", "label": _("Mobile No GST"), "fieldtype": "Data", "width": 120},
        {"fieldname": "gst_user_name", "label": _("GST User Name"), "fieldtype": "Data", "width": 120},
        {"fieldname": "gst_password", "label": _("GST Password"), "fieldtype": "Data", "width": 120},
        {"fieldname": "proprietor_name", "label": _("Proprietor Name"), "fieldtype": "Data", "width": 120},
        {"fieldname": "executive", "label": _("Executive"), "fieldtype": "Data", "width": 150},
        {"fieldname": "gst_type", "label": _("GST Type"), "fieldtype": "Data", "width": 100},
        {"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 100},
        {"fieldname": "fy", "label": _("Fiscal Year"), "fieldtype": "Data", "width": 100},
        {"fieldname": "gst_yearly_filling_summery_id", "label": _("GstYearly Filling Summery Id"), "fieldtype": "Link", "options": "Gst Yearly Filing Summery", "width": 300},
        {"fieldname": "filing_notes", "label": _("Filing Notes"), "fieldtype": "Data", "width": 150},
    ]

    # Construct additional filters based on the provided filters
    additional_filters = {}
    gstfile_enabled_filter=1
    # Check if the mandatory filters are provided
    if filters.get("gst_type") and filters.get("fy") and filters.get("month"):
        additional_filters["gst_type"] = filters["gst_type"]
        additional_filters["fy"] = filters["fy"]
        additional_filters["month"] = filters["month"]
        if filters.get("customer_id"):
            additional_filters["cid"] = filters["customer_id"]
        
    else:
        # If mandatory filters are not provided, return empty data
        return columns, [], ""

    # Fetch data using Frappe ORM
    data = frappe.get_all(
        "Gst Filling Data",
        filters=additional_filters,
        fields=["cid", "customer_status", "name", "filing_status", "gstfile", "gstfile_enabled", "company",
                "mobile_no_gst", "gst_user_name", "gst_password", "proprietor_name", "executive",
                "gst_type", "month", "fy", "gst_yearly_filling_summery_id", "filing_notes"],
    )

    if filters.get("customer_status"):
        customer_list = frappe.get_all("Customer",filters={},fields=["name", "disabled"],)
        customer_list={cus.name:cus.disabled for cus in customer_list}
        customer_status = filters["customer_status"]
        data_new=[]
        if customer_status=="Enabled":
            for gst_file in data:
                if (not customer_list[gst_file.cid]) :
                    data_new.append(gst_file)
        elif customer_status=="Disabled":
            for gst_file in data:
                if ( customer_list[gst_file.cid]) :
                    data_new.append(gst_file)
        data=data_new

    if "cid" in additional_filters:
        del additional_filters["cid"]

    # data_old = frappe.get_list(
    #     "Gst Filling Data",
    #     filters=additional_filters,
    #     fields=["cid", "customer_status", "name", "filing_status", "gstfile", "gstfile_enabled", "company",
    #             "mobile_no_gst", "gst_user_name", "gst_password", "proprietor_name", "executive",
    #             "gst_type", "month", "fy", "gst_yearly_filling_summery_id", "filing_notes"],
    # )
    gst_file_enabled = frappe.get_all("Gstfile", filters={"enabled":gstfile_enabled_filter})
    gst_file_enabled=[i.name for i in gst_file_enabled]

    data_gst_enabled=[]
    for data_i in data:
        if data_i.gstfile in gst_file_enabled:
            data_gst_enabled.append(data_i)

    data=data_gst_enabled
    data_old=data_gst_enabled

    # Fetch counts for different filing statuses using Frappe's ORM
    statuses = ["Pending", "Filed Summery Shared With Client", "GSTR-1 or IFF Prepared and Filed",
                "GSTR-2A/2B or 4A/4B Reco done", "Data Collected", "Data Finalized", "Tax Calculation Done",
                "Tax Informed to Client", "Tax Payment Processed", "GSTR-3B / CMP08 Prepared and Filed"]
    
    total_records_count=len(data_old)
    status_counts = {}
    executive_counts = {}
    executive_files  ={}
    executive_files_done={}
    filed_summery_shared_count = 0

    for row_i in data_old:
        if row_i.filing_status in status_counts:
            status_counts[row_i.filing_status]+=1
        else:
            status_counts[row_i.filing_status]=1

        if row_i.executive in executive_files:
            executive_files[row_i.executive]+=1
        else:
            executive_files[row_i.executive]=1
        
        if row_i.filing_status == "Filed Summery Shared With Client":

            filed_summery_shared_count = status_counts[row_i.filing_status]

            if row_i.executive in executive_files_done :
                executive_files_done[row_i.executive]+=1
            else:
                executive_files_done[row_i.executive]=1
    
    filed_summery_shared_percentage = (filed_summery_shared_count / total_records_count) * 100 if total_records_count != 0 else 0

    

    for executive in executive_files:
        executive_count=0
        if executive in executive_files :
            executive_count=executive_files[executive]

        filed_summery_shared_count=0
        if executive in executive_files_done :
            filed_summery_shared_count=executive_files_done[executive]

        executive_counts[executive] = {
            "total_count": executive_count,
            "filed_summery_shared_count": filed_summery_shared_count,
            "not_filed_summery_shared_count": executive_count-filed_summery_shared_count
        }

    # Create HTML card with counts for different filing statuses
    html_card = f"""
    <div class="frappe-card" style="margin-bottom: 10px;">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#collapsible-content">
            <strong>Filing Status Counts</strong>
            <strong>(Overall Target Achieved: {filed_summery_shared_percentage:.2f}%)</strong>
            <strong>(Total Count: {total_records_count})</strong>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body collapse" id="collapsible-content">
            <div class="flex-container" style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Pending", 0)}</div>
                        <div class="frappe-card-label">Pending Filing Status Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Data Collected", 0)}</div>
                        <div class="frappe-card-label">Data Collected Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Data Finalized", 0)}</div>
                        <div class="frappe-card-label">Data Finalized Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Tax Calculation Done", 0)}</div>
                        <div class="frappe-card-label">Tax Calculation Done Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Tax Informed to Client", 0)}</div>
                        <div class="frappe-card-label">Tax Informed to Client Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("GSTR-1 or IFF Prepared and Filed", 0)}</div>
                        <div class="frappe-card-label">GSTR-1 or IFF Prepared and Filed Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("GSTR-2A/2B or 4A/4B Reco done", 0)}</div>
                        <div class="frappe-card-label">GSTR-2A/2B or 4A/4B Reco done Count</div>
                    </div>
                </div>       
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Tax Payment Processed", 0)}</div>
                        <div class="frappe-card-label">Tax Payment Processed Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("GSTR-3B / CMP08 Prepared and Filed", 0)}</div>
                        <div class="frappe-card-label">GSTR-3B / CMP08 Prepared and Filed Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("Filed Summery Shared With Client", 0)}</div>
                        <div class="frappe-card-label">Filed Summery Shared With Client Count</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="frappe-card" style="margin-bottom: 10px;">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#executive-content">
            <strong>Executive-wise Counts</strong>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body collapse" id="executive-content">
            <table class="table table-bordered">
                <thead>
                    <tr>
                        <th>Executive</th>
                        <th>Total Count</th>
                        <th>Filed Summery Shared</th>
                        <th>Not Filed Summery Shared</th>
                        <th>Target Achieved</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([
                        f"<tr><td>{executive}</td><td>{executive_counts[executive]['total_count']}</td><td>{executive_counts[executive]['filed_summery_shared_count']}</td><td>{executive_counts[executive]['not_filed_summery_shared_count']}</td><td>{(executive_counts[executive]['filed_summery_shared_count'] / executive_counts[executive]['total_count']) * 100:.2f}%</td></tr>"
                        for executive in executive_counts.keys()
                    ])}
                </tbody>
            </table>
        </div>
    </div>
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




