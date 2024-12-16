# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Shipping Waybill",
    "version": "16.0",
    "summary": "Shipping Waybill",
    "description": """
       Shipping Waybill.
    """,
    "category": 'Customization',

    # Author
    "author": "Bahelim Munafkhan",
    "website": "https://www.4minds.com",
    "license": "LGPL-3",

    # Dependency
    "depends": [],

    "data": [
        "security/ir.model.access.csv",
        "views/freight_way_bill_views.xml",
        # Report
        "data/paper_format.xml",
        "reports/shipping_waybill_report_template.xml",
        "reports/report_action.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
