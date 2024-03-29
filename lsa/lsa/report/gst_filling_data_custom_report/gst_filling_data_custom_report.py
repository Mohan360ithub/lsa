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

    # Check if the mandatory filters are provided
    if filters.get("gst_type") and filters.get("fy") and filters.get("month"):
        additional_filters["gst_type"] = filters["gst_type"]
        additional_filters["fy"] = filters["fy"]
        additional_filters["month"] = filters["month"]
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
        as_list=True
    )

    # Fetch counts for different filing statuses using custom SQL queries
    statuses = ["Pending", "Filed Summery Shared With Client", "GSTR-1 or IFF Prepared and Filed",
                "GSTR-2A/2B or 4A/4B Reco done", "Data Collected", "Data Finalized", "Tax Calculation Done",
                "Tax Informed to Client", "Tax Payment Processed", "GSTR-3B / CMP08 Prepared and Filed"]
    status_counts = {}


    filed_summery_shared_count = 0

    for status in statuses:
        count_query = f"""
            SELECT COUNT(name) as count
            FROM `tabGst Filling Data`
            {"WHERE filing_status = %s" if not additional_filters else "WHERE filing_status = %s AND "
            + " AND ".join([f"{key} = %s" for key in additional_filters])}
        """

        count_result = frappe.db.sql(count_query, [status, *additional_filters.values()], as_dict=True)
        status_count = count_result[0].get("count") if count_result else 0
        status_counts[status] = status_count

        if status == "Filed Summery Shared With Client":
            filed_summery_shared_count = status_count

    total_records_count = sum(status_counts.values())

    filed_summery_shared_percentage = (filed_summery_shared_count / total_records_count) * 100 if total_records_count != 0 else 0

    executive_counts = {}

    for executive in set([row[11] for row in data]):
        # Count for all filing statuses
        count_query = f"""
            SELECT COUNT(name) as count
            FROM `tabGst Filling Data`
            {"WHERE executive = %s" if not additional_filters else "WHERE executive = %s AND "
            + " AND ".join([f"{key} = %s" for key in additional_filters])}
        """

        count_result = frappe.db.sql(count_query, [executive, *additional_filters.values()], as_dict=True)
        executive_count = count_result[0].get("count") if count_result else 0

        # Count specifically for "Filed Summery Shared With Client"
        filed_summery_shared_query = f"""
            SELECT COUNT(name) as filed_summery_shared_count
            FROM `tabGst Filling Data`
            WHERE executive = %s AND filing_status = 'Filed Summery Shared With Client'
            AND gst_type = %s AND fy = %s AND month = %s
        """

        filed_summery_shared_count_result = frappe.db.sql(filed_summery_shared_query, [executive, *additional_filters.values()], as_dict=True)
        filed_summery_shared_count = filed_summery_shared_count_result[0].get("filed_summery_shared_count") if filed_summery_shared_count_result else 0

        # Count specifically for statuses other than "Filed Summery Shared With Client"
        not_filed_summery_shared_count_query = f"""
            SELECT COUNT(name) as not_filed_summery_shared_count
            FROM `tabGst Filling Data`
            WHERE executive = %s AND filing_status != 'Filed Summery Shared With Client'
            AND gst_type = %s AND fy = %s AND month = %s
        """

        not_filed_summery_shared_count_result = frappe.db.sql(not_filed_summery_shared_count_query, [executive, *additional_filters.values()], as_dict=True)
        not_filed_summery_shared_count = not_filed_summery_shared_count_result[0].get("not_filed_summery_shared_count") if not_filed_summery_shared_count_result else 0

        # Assign the counts to the executive
        executive_counts[executive] = {
            "total_count": executive_count,
            "filed_summery_shared_count": filed_summery_shared_count,
            "not_filed_summery_shared_count": not_filed_summery_shared_count
        }

    # ...

    executive_table = """
    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Executive</th>
                <th>Total Count</th>
                <th>Filed </th>
                <th>Not Filed </th>
                <th>Target Achieved </th>
            </tr>
        </thead>
        <tbody>
            {0}
        </tbody>
    </table>
    """

    executive_rows = "".join([
        f"""
        <tr>
            <td>{executive}</td>
            <td>{executive_counts[executive]["total_count"]}</td>
            <td>{executive_counts[executive]["filed_summery_shared_count"]}</td>
            <td>{executive_counts[executive]["not_filed_summery_shared_count"]}</td>
            <td>{(executive_counts[executive]["filed_summery_shared_count"] / executive_counts[executive]["total_count"]) * 100:.2f}%</td>
        </tr>
        """
        for executive in executive_counts.keys()
    ])
    # Create HTML card with counts for different filing statuses
    html_card = f"""
 
    <div class="frappe-card" style="margin-bottom: 10px;>
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
                <!-- Add other card elements here -->
            </div>
        </div>
    </div>
    <div class="frappe-card" style="margin-bottom: 10px;>
    <div class="frappe-card-head" data-toggle="collapse" data-target="#executive-content">
        <strong>Executive-wise Counts</strong>
        <span class="caret"></span>
    </div>
    <div class="frappe-card-body collapse" id="executive-content">
        {executive_table.format(executive_rows)}
    </div>
    
</div>

    """
    """
    <script>
        frappe.ui.form.on('Gst Filling Data', {
            refresh: function (frm) {
                frm.fields_dict['collapsible-content'].$wrapper.find('.frappe-card-head').on('click', function () {
                    frm.fields_dict['collapsible-content'].toggle();
                });
            }
        });
    </script>
    """

    return columns, data, html_card

