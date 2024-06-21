# Copyright (c) 2024, Mohan and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": _("ID"), "fieldtype": "Link", "options": "IT Assessee Filing Data", "width": 150},
        
        {"fieldname": "customer_id", "label": _("CID"), "fieldtype": "Link", "options": "Customer", "width": 100},
        {"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 100},
        {"fieldname": "contact_person", "label": _("Contact Person"), "fieldtype": "Data", "width": 100},
        {"fieldname": "assessee_full_name", "label": _("Assessee Full Name"), "fieldtype": "Data", "width": 120},
        
        {"fieldname": "customer_status", "label": _("Customer Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "it_assessee_file", "label": _("PAN"), "fieldtype": "Link", "options": "IT Assessee File", "width": 165},
        {"fieldname": "filing_status", "label": _("Filing Status"), "fieldtype": "Data", "width": 170},
        # {"fieldname": "pan", "label": _("PAN"), "fieldtype": "Data", "width": 50},
        {"fieldname": "executive", "label": _("Executive"), "fieldtype": "Data", "width": 150},
        {"fieldname": "mobile_no", "label": _("Mobile No"), "fieldtype": "Data", "width": 100},
        # {"fieldname": "created_manually", "label": _("Created Manually"), "fieldtype": "Check", "width": 100},
        # {"fieldname": "ay", "label": _("IT Assessee File Yearly Report"), "fieldtype": "Data", "width": 150},
        # {"fieldname": "filing_notes", "label": _("Filing Notes"), "fieldtype": "Data", "width": 150},
    ]

    # Construct additional filters based on the provided filters
    additional_filters = {}

    # Check if the mandatory filters are provided
    if filters.get("ay"):
        additional_filters["ay"] = filters["ay"]
    else:
        # If mandatory filters are not provided, return empty data
        return columns, [], ""

    data = frappe.get_all(
        "IT Assessee Filing Data",
        filters=additional_filters,
        fields=["name", "customer_id","customer_name","contact_person", "assessee_full_name","customer_status", "it_assessee_file","filing_status",  "executive","mobile_no",  ],
        as_list=True
    )

    # Fetch counts for different filing statuses using custom SQL queries
    statuses = ["PENDING INITIAL CONTACT", "DOCUMENTS REQUESTED", "DOCUMENTS PARTIALLY RECEIVED",
                "DOCUMENTS FULLY COLLECTED", "REVIEWED AND VERIFIED", "RETURN PREPARED", "SHARED TO CLIENT REVIEW",
                "FILED", "ACK AND VERIFIED", "DOCS SHARED WITH CLIENT"]
    status_counts = {}

    for status in statuses:
        count_query = f"""
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE filing_status = %s
            AND ay = %s
        """

        count_result = frappe.db.sql(count_query, [status, additional_filters["ay"]], as_dict=True)
        status_count = count_result[0].get("count") if count_result else 0
        status_counts[status] = status_count

    total_records_count = sum(status_counts.values())

    doc_shared_with_client = status_counts.get("DOCS SHARED WITH CLIENT", 0)
    doc_shared_with_client_percentage = (doc_shared_with_client / total_records_count) * 100 if total_records_count != 0 else 0

    executive_counts = {}

    for executive in set(row[8] for row in data):
        # Count for all filing statuses
        count_query = f"""
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE executive = %s
            AND ay = %s
        """

        count_result = frappe.db.sql(count_query, [executive, additional_filters["ay"]], as_dict=True)
        executive_count = count_result[0].get("count") if count_result else 0

        # Count specifically for "Filed Summery Shared With Client"
        filed_summery_shared_query = f"""
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE executive = %s
            AND filing_status = 'DOCS SHARED WITH CLIENT'
            AND ay = %s
        """

        filed_summery_shared_count_result = frappe.db.sql(filed_summery_shared_query, [executive, additional_filters["ay"]], as_dict=True)
        filed_summery_shared_count = filed_summery_shared_count_result[0].get("count") if filed_summery_shared_count_result else 0

        # Count specifically for statuses other than "DOCS SHARED WITH CLIENT"
        not_doc_shared_with_client_query = f"""
            SELECT COUNT(name) as count
            FROM `tabIT Assessee Filing Data`
            WHERE executive = %s
            AND filing_status != 'DOCS SHARED WITH CLIENT'
            AND ay = %s
        """

        not_doc_shared_with_client_result = frappe.db.sql(not_doc_shared_with_client_query, [executive, additional_filters["ay"]], as_dict=True)
        not_doc_shared_with_client_count = not_doc_shared_with_client_result[0].get("count") if not_doc_shared_with_client_result else 0

        # Assign the counts to the executive
        executive_counts[executive] = {
            "total_count": executive_count,
            "filed_summery_shared_count": filed_summery_shared_count,
            "not_doc_shared_with_client_count": not_doc_shared_with_client_count
        }

    executive_table = """
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
            <td>{executive_counts[executive]["not_doc_shared_with_client_count"]}</td>
            <td>
    {("{:.2f}".format((executive_counts[executive]["filed_summery_shared_count"] / executive_counts[executive]["total_count"]) * 100) 
        if executive_counts[executive]["total_count"] > 0 
        else 'No count')}
</td>


        </tr>
        """
        for executive in executive_counts.keys()
    ])

    html_card = f"""
    <div class="frappe-card" style="margin-bottom: 10px;">
        <div class="frappe-card-head" data-toggle="collapse" data-target="#collapsible-content">
            <strong>Filing Status Counts</strong>
            <strong>(Overall Target Achieved: {doc_shared_with_client_percentage:.2f}%)</strong>
            <strong>(Total Count: {total_records_count})</strong>
            <span class="caret"></span>
        </div>
        <div class="frappe-card-body collapse" id="collapsible-content">
            <div class="flex-container" style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("PENDING INITIAL CONTACT", 0)}</div>
                        <div class="frappe-card-label">PENDING INITIAL CONTACT Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("DOCUMENTS REQUESTED", 0)}</div>
                        <div class="frappe-card-label">DOCUMENTS REQUESTED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("DOCUMENTS PARTIALLY RECEIVED", 0)}</div>
                        <div class="frappe-card-label">DOCUMENTS PARTIALLY RECEIVED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("DOCUMENTS FULLY COLLECTED", 0)}</div>
                        <div class="frappe-card-label">DOCUMENTS FULLY COLLECTED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("REVIEWED AND VERIFIED", 0)}</div>
                        <div class="frappe-card-label">REVIEWED AND VERIFIED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("RETURN PREPARED", 0)}</div>
                        <div class="frappe-card-label">RETURN PREPARED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("SHARED TO CLIENT REVIEW", 0)}</div>
                        <div class="frappe-card-label">SHARED TO CLIENT REVIEW Count</div>
                    </div>
                </div>       
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("FILED", 0)}</div>
                        <div class="frappe-card-label">FILED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("ACK AND VERIFIED", 0)}</div>
                        <div class="frappe-card-label">ACK AND VERIFIED Count</div>
                    </div>
                </div>
                <div class="frappe-card" style="flex: 1; min-width: 200px; max-width: 300px;">
                    <div class="frappe-card-content">
                        <div class="frappe-card-count">{status_counts.get("DOCS SHARED WITH CLIENT", 0)}</div>
                        <div class="frappe-card-label">DOCS SHARED WITH CLIENT Count</div>
                    </div>
                </div>
                <!-- Add other card elements here -->
            </div>
        </div>
    </div>
    <div class="frappe-card" style="margin-bottom: 10px;">
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


