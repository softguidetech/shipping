# -*- coding: utf-8 -*-

{
    "name": "Trip Cargo",
    "version": "1.6.1",
    "depends": [
        'base', 'account', 'contacts','analytic','fleet'
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/trip_trip_view.xml',
        'view/location_location_view.xml',
        'reports/trip_report.xml',
        'reports/car_ticket_report_template.xml',
        'reports/car_ticket_report.xml',
        'reports/car_ticket_layout.xml',
       
    ],
    "author": "SGT",
    "category": "Accounting",
    "installable": True,
    "auto_install": False,
    "application": True,
}
