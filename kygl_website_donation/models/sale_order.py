# -*- coding: utf-8 -*-
from odoo import fields,models
from datetime import date,timedelta
import logging
_logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d"

class SaleOrder(models.Model):
    _inherit='sale.order'

    message_donation = fields.Text(string="Message for donation")
