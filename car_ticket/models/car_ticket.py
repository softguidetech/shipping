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
