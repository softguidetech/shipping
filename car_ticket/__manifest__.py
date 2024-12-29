# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Car Ticket Management",
    "version": "16.0",
    "summary": "Car Ticket Management",
    "description": """
       Car Ticket Management
    """,
    "category": 'Customization',

    # Author
    "author": "Bahelim Munafkhan",
    "website": "https://www.4minds.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['web', 'base','fleet'],

    "data": [
        "security/ir.model.access.csv",
        "views/car_ticket_views.xml",
        "views/location_location_view.xml",
        "reports/car_ticket_layout.xml",
        "reports/car_ticket_report_template.xml",
        "reports/car_ticket_report.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
