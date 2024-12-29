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
    departure_date = fields.Datetime(string='Departure Date')
    route_no = fields.Char(string='Route Number')
    price = fields.Float(string='Price', required=True)
    passenger_name = fields.Char(string='Passenger Name')

    # Trip Request fields
    pnr = fields.Char(string="PNR")
    origin_port = fields.Many2one('loca.loca',string="Origin Port")
    destination_port = fields.Many2one('loca.loca',string="Destination Port")
    date = fields.Date(string="Date")
    model_in_english = fields.Many2one('fleet.vehicle.model',string="Model In English")
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
    state = fields.Selection([('draft','draft'),('submit','Submitted')],default='draft')
    count_bill = fields.Integer(compute='_count_bill')
    count_invoice = fields.Integer(compute='_count_invoice')
    
    
    def _count_invoice(self):
        invoice_ids = self.env['account.move'].search_count([('trip_id','=',self.id),('move_type','=','out_invoice')])
        if invoice_ids:
            self.count_invoice = invoice_ids
        else:
            self.count_invoice = 0
            
    def action_cancel(self):
        for rec in self:
            rec.state='draft'
            
            
    def _count_bill(self):
        bill_ids = self.env['account.move'].search_count([('trip_id','=',self.id),('move_type','=','in_invoice')])
        if bill_ids:
            self.count_bill = bill_ids
        else:
            self.count_bill = 0
    
    def view_invoice(self):
        list_ids = []
        invoice_ids = self.env['account.move'].search([('trip_id','=',self.id),('move_type','=','out_invoice')])
        for rec in invoice_ids:
            list_ids.append(rec.id)
        tree_view = self.env.ref('account.view_out_invoice_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Invoice',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'tree',
            'move_type': 'out_invoice',
            'views': [(tree_view.id, 'tree')],
            'domain': [('id', 'in', list_ids)],

        }
        
    def view_bill(self):
        list_ids = []
        bill_ids = self.env['account.move'].search([('trip_id','=',self.id),('move_type','=','in_invoice')])
        for rec in bill_ids:
            list_ids.append(rec.id)
        tree_view = self.env.ref('account.view_in_invoice_bill_tree')
        form_view = self.env.ref('account.view_move_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Bills',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'tree',
            'move_type': 'in_invoice',
            'views': [(tree_view.id, 'tree')],
            'domain': [('id', 'in', list_ids)],

        }
    
    
    
    def action_submit(self):
        for rec in self:
            rec.state='submit'
            
    # @api.model
    # def create(self, vals):
    #     code = 'trip.trip.code'

    #     if vals.get('name', 'New') == 'New':
    #         message = 'Trip/' + self.env['ir.sequence'].next_by_code(code)
    #         vals['name'] = message
    #         # self.message_post(subject='Create CCR', body='This is New CCR Number' + str(message))
    #     return super(TripTrip, self).create(vals)
        
class LocaLoca(models.Model):
    _name = 'loca.loca'
    
    name=fields.Char(string='Name',required=True)
    
    
    
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    trip_id = fields.Many2one('car.ticket',string='Trip')
    


    
   

