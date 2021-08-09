# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import date, timedelta
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    kygl_message_email = fields.Html(string="Message for email", compute="_get_message_email")

    @api.depends("invoice_line_ids")
    def _get_message_email(self):
        for record in self:
            self.kygl_message_email = False
            for product in record.invoice_line_ids.product_id:
                if product.kygl_message_document:
                    record.kygl_message_email = product.kygl_message_document

    def _post(self,soft=True):
        res = super(AccountMove,self)._post(soft)
        for record in self.filtered(lambda k: k.move_type == "out_invoice"):
            for line in record.invoice_line_ids:
                if line.product_id.membership:
                    day = 365 #default
                    if line.product_id.subscription_template_id:
                        day = 1
                        if line.product_id.subscription_template_id.recurring_rule_type == 'monthly':
                           day = 30
                        if line.product_id.subscription_template_id.recurring_rule_type == 'yearly':
                           day = 365
                    day = day * line.product_id.subscription_template_id.recurring_interval
                    membership_line = self.env['membership.membership_line'].search([("account_invoice_id","=",record.id)])
                    membership_line.write({"date_from":fields.Date.today() ,"date_to":fields.Date.today() + timedelta(days=day)})
        return res


