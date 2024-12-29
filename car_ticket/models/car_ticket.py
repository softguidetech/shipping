# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class CarTicket(models.Model):
    _name = "car.ticket"
    _description = 'Car Ticket'
    _rec_name = 'ticket_no'

    ticket_no = fields.Char(string='Ticket Number', required=True)
    booking_no = fields.Char(string='Booking Number')
    ticket_type = fields.Selection([
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('vip', 'VIP')
    ], string='Ticket Type', default='economy')
    departure_date = fields.Datetime(string='Departure Date', required=True)
    route_no = fields.Char(string='Route Number')
    price = fields.Float(string='Price', required=True)
    passenger_name = fields.Char(string='Passenger Name')

    # Trip Request fields
    pnr = fields.Char(string="PNR")
    origin_port = fields.Char(string="Origin Port")
    destination_port = fields.Char(string="Destination Port")
    date = fields.Date(string="Date")
    model_in_english = fields.Char(string="Model In English")
    crossing_number = fields.Char(string="Crossing Number")
    crossing_date = fields.Date(string="Crossing Date")
    shipper_name_english = fields.Char(string="Shipper Name in English")
    shipper_name_arabic = fields.Char(string="Shipper Name in Arabic")
    consignee_name_english = fields.Char(string="Consignee Name in English")
    consignee_name_arabic = fields.Char(string="Consignee Name in Arabic")
    vehicle_type = fields.Char(string="Vehicle Type")
    manufacturing_english = fields.Char(string="Manufacturing in English")
    manufacturing_arabic = fields.Char(string="Manufacturing in Arabic")
    manufacturing_year = fields.Char(string="Manufacturing Year")
    plate_number = fields.Char(string="Plate Number")
    chassis_number = fields.Char(string="Chassis Number")
    term = fields.Html(string='Term and Conditions')
    note = fields.Html(string='Notes')