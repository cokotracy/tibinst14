# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from datetime import datetime,timedelta


class SaleRoomEportWizard(models.TransientModel):
    _name = "sale.room.report.wizard"

    date_from = fields.Date('Start Date', default=datetime.today(), required=True)
    date_to = fields.Date('End Date', default=datetime.today()+timedelta(days=15),required=True)

    @api.multi
    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref('website_booking.action_report_summary_report')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_summary_report']
        report = model.create(self._prepare_summary_report())
        report.compute_data_for_report()
        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        report_type = 'qweb-pdf'
        return self._export(report_type)

    def _prepare_summary_report(self):
        self.ensure_one()

        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

    
