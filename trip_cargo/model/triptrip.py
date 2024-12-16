from odoo import models, fields, api, _
from odoo.exceptions import AccessError



class TripTrip(models.Model):
    _name = "trip.trip"
    
    name= fields.Char(string='PNR',required=True)
    ticket_number = fields.Char(string='Ticket Number',required=True)
    crossing_number = fields.Char(string='Crossing Number',required=True)
    crossing_date = fields.Date(string='Crossing Date',required=True)
    ticket_type = fields.Char(string='Ticket type',required=True)
    shipper_name_en = fields.Char(string='Shipper Name in English',required=True)
    shipper_name_ar = fields.Char(string='Shipper Name in Arabic',required=True)
    source_loc= fields.Many2one('loca.loca',string='Origin Port',required=True)
    consignee_name_en = fields.Char(string='Consignee Name in English',required=True)
    consignee_name_ar = fields.Char(string='Consignee Name in Arabic',required=True)
    des_loc= fields.Many2one('loca.loca',string='Destination Port',required=True)
    date = fields.Date(string='Date',required=True)
    driver_id = fields.Many2one('res.partner',string='Driver',required=True)
    vehicle_type = fields.Selection([('Sedan','Sedan'),('SUV','SUV'),('4x4','4x4'),('Truck','Truck')])
    truck_id = fields.Many2one('fleet.vehicle.model',string='Model In English',required=True)
    manufacturing_en = fields.Char(string='Manufacturing in English',required=True)
    manufacturing_ar = fields.Char(string='Manufacturing in Arabic',required=True)
    manufacturing_year = fields.Char(string='Manufacturing Year',required=True)
    plate_number = fields.Char(string='Plate Number',required=True)
    chassis_number = fields.Char(string='Chassis Number',required=True)
    state = fields.Selection([('draft','draft'),('submit','Submitted')],default='draft')
    ticket_amount = fields.Float(string='Ticket amount',required=True)
    count_bill = fields.Integer(compute='_count_bill')
    count_invoice = fields.Integer(compute='_count_invoice')
    note = fields.Html(string="Note")
    
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
    
    trip_id = fields.Many2one('trip.trip',string='Trip')
    


    
   
