from odoo import models, fields, api, _
from odoo.exceptions import AccessError



class TripTrip(models.Model):
    _name = "trip.trip"
    
    name= fields.Char(string='Reference',readonly=True,default='New')
    source_loc= fields.Many2one('loca.loca',string='Source Location',required=True)
    des_loc= fields.Many2one('loca.loca',string='Destination Location',required=True)
    date = fields.Date(string='Date',required=True)
    driver_id = fields.Many2one('res.partner',string='Driver',required=True)
    truck_id = fields.Many2one('fleet.vehicle.model',string='Truck',required=True)
    state = fields.Selection([('draft','draft'),('submit','Submitted')],default='draft')
    
    def action_submit(self):
        for rec in self:
            rec.state='submit'
            
    @api.model
    def create(self, vals):
        code = 'trip.trip.code'

        if vals.get('name', 'New') == 'New':
            message = 'Trip/' + self.env['ir.sequence'].next_by_code(code)
            vals['name'] = message
            # self.message_post(subject='Create CCR', body='This is New CCR Number' + str(message))
        return super(TripTrip, self).create(vals)
        
class LocaLoca(models.Model):
    _name = 'loca.loca'
    
    name=fields.Char(string='Name',required=True)
    


    
   
