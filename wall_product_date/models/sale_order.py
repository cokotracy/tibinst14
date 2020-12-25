# -*- coding: utf-8 -*-

from odoo import fields,models,api
from datetime import date,timedelta
import logging
_logger = logging.getLogger(__name__)

DATETIME_FORMAT="%Y-%m-%d"


class SaleOrder(models.Model):
    _inherit='sale.order'

    message_wall=fields.Text(string="Message for Wall")
    product_wall=fields.Char(string="Product_wall",compute="_get_product_wall",store=True)
    def _message_wall(self):
        for record in self:
            for line in record.order_line:
                if line.product_id.product_tmpl_id.id in [self.env.ref('wall_product_date.product_wall1').id,self.env.ref('wall_product_date.product_wall2').id,self.env.ref('wall_product_date.product_wall3').id]:
                    return True
        return False
    
    def _cron_get_message_wall(self,day=0):
        date_search=(date.today()-timedelta(days=day)).strftime(DATETIME_FORMAT)
        recordall=self.env["sale.order"].search([('state','in',["sale","done"]),('write_date','>','%s 00:00:00' % date_search)])
        _logger.info("Search sale order for message Wall")
        for record in recordall:
            if record._message_wall():   
                _logger.info("message Wall for %s" % record.name)
                record._get_product_wall()
                record.message_post_with_template(self.env.ref('wall_product_date.mail_template_message_wall').id, composition_mode='comment')

    def _get_product_wall(self):
            for record in self:
                record.product_wall=""
                for line in record.order_line:
                    if line.product_id.product_tmpl_id.id in [self.env.ref('wall_product_date.product_wall1').id,self.env.ref('wall_product_date.product_wall2').id,self.env.ref('wall_product_date.product_wall3').id]:
                        record.product_wall+="%s, " % line.name
                