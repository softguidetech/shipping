from odoo import models,fields,api,_

class TripReport(models.AbstractModel):
    _name = 'trip.trip.report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('trip_cargo.report_trip')
        docargs = {
            'doc_ids': docids,
            'doc_model': trip.trip,
            'docs': self,
        }
        return report_obj.render('trip_cargo.report_trip', docargs)