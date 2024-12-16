# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class Waybill(models.Model):
    _name = 'freight.waybill'
    _description = 'Freight Waybill'
    _rec_name = 'bill_number'

    bill_number = fields.Char(string='Bill Number', required=True)
    bill_date = fields.Date(string='Bill Date', required=True)
    place = fields.Char(string='Place')
    shipper_name = fields.Char(string='Shipper Name')
    shipper_address = fields.Text(string='Shipper Address')
    shipper_contact = fields.Char(string='Shipper Contact')
    recipient_name = fields.Char(string='Recipient Name')
    recipient_address = fields.Text(string='Recipient Address')
    recipient_contact = fields.Char(string='Recipient Contact')
    insurance_amount = fields.Float(string='Insurance Amount')
    weight = fields.Float(string='Weight (kg)')
    description = fields.Text(string='Description of Goods')
    num_parcels = fields.Integer(string='Number of Parcels')
    parcel_status = fields.Selection([
        ('draft', 'Draft'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='Parcel Status', default='draft')
    category = fields.Char(string='Category')
    additional_charges = fields.Float(string='Additional Charges')
    tax = fields.Float(string='Tax')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('additional_charges', 'tax')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.additional_charges + record.tax
