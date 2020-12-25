# Copyright  2018 Forest and Biomass Romania
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models,_
from datetime import datetime,timedelta

class VATReport(models.TransientModel):
    _name = "report_summary_report"


    # Filters fields, used for data computation
    #company_id = fields.Many2one(comodel_name='res.company')
    date_from = fields.Date()
    date_to = fields.Date()

    # Data fields, used to browse report data
    summary_header =[]
    room_summary=[]


class VATReportCompute(models.TransientModel):

    _inherit = 'report_summary_report'

    @api.multi
    def print_report(self, report_type='qweb'):
        self.ensure_one()
        report_name = 'website_booking.report_summary_report_qweb'
        context = dict(self.env.context)
        action = self.env['ir.actions.report'].search(
            [('report_name', '=', report_name),
             ('report_type', '=', report_type)], limit=1)
        return action.with_context(context).report_action(self)

    def create_booking(self,room_id,date):
        public=self.env["res.users"].search([("login","=","public"),("active","=",False)])
        sale = self.env["sale.order"].create({'partner_id': public[0].partner_id.id})
        sale_line = self.env["sale.order.line"].create({
                        'order_id': sale.id,
                        'product_id': int(room_id),
                        'x_rental':True,
                        })
        return sale.id

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get('active_id'))
        booking = self.env['booking.config'].search([],limit=1)
        rooms=self.env["product.product"].search([('x_is_room','=',True)])
        if report:
            DATETIME_FORMAT = "%Y-%m-%d"
            from_dt = datetime.strptime(report.date_from, DATETIME_FORMAT).date()
            to_dt = datetime.strptime(report.date_to, DATETIME_FORMAT).date()
            delta = to_dt - from_dt
            listdate=[]
            room_summary=[]
            for i in range(delta.days + 1):
                listdate.append(from_dt + timedelta(days=i))
            for room in rooms:
                values=[]
                for date in listdate:
                         AM = datetime.strptime(str(date)+" 00:00:01","%Y-%m-%d %H:%M:%S")
                         PM = datetime.strptime(str(date)+" 23:59:59","%Y-%m-%d %H:%M:%S")
                         #"AM"
                         queryAM=[("product_id.id","=",room.id),
                         ("product_id.x_rental", "=", True),
                         ("x_start", "<", str(AM)), ("x_end", ">",str(AM)),
                         ('order_id.state', 'not in', ["cancel","sent","draft"])]

                         queryAM_Draft=[("product_id.id","=",room.id),
                         ("product_id.x_rental", "=", True),
                         ("x_start", "<", str(AM)), ("x_end", ">",str(AM)),
                         ('order_id.state', 'in', ["sent", "draft"])]

                         #PM
                         queryPM=[("product_id.id","=",room.id),
                         ("product_id.x_rental", "=", True),
                         ("x_start", "<", str(PM)), ("x_end", ">",str(PM)),
                         ('order_id.state', 'not in', ["cancel", "sent","draft"])]

                         queryPM_Draft=[("product_id.id","=",room.id),
                         ("product_id.x_rental", "=", True),
                         ("x_start", "<", str(PM)), ("x_end", ">",str(PM)),
                         ('order_id.state', 'in', ["sent", "draft"])]

                         salelinesAM=self.env["sale.order.line"].search(queryAM)
                         salelinesPM=self.env["sale.order.line"].search(queryPM)
                         salelinesAMD=self.env["sale.order.line"].search(queryAM_Draft)
                         salelinesPMD=self.env["sale.order.line"].search(queryPM_Draft)
                         blocked="No"
                         if len(salelinesAM)==0 and len(salelinesAMD)==0:
                             stateAM="Free"
                             draftAM="No"
                             id=0
                         elif len(salelinesAMD)>0:
                             stateAM="In Progress"
                             draftAM="Yes"
                             id = salelinesAMD[0].order_id.id
                         elif len(salelinesAM)>1:
                             stateAM="multiReserverd"
                             draftAM="No"
                             id = salelinesAM.mapped("order_id.id")
                         else:
                            stateAM="Reserverd"
                            draftAM="No"
                            id = salelinesAM[0].order_id.id
                         if room.x_available_until and str(AM)[0:10]>=room.x_available_until:
                            blocked="Yes"

                         values.append({"date":date,
                                        "state":stateAM,
                                        "room_id":room.id,
                                        "is_draft":draftAM,
                                        "data_model":"sale.order",
                                        'data_date':date,
                                        'data_id': id,
                                        'blocked':blocked,
                                        })

                         if len(salelinesPM)==0 and len(salelinesPMD)==0:
                              statePM="Free"
                              draftPM="No"
                              id=0
                         elif len(salelinesPMD)>0:
                              statePM="In Progress"
                              draftPM="Yes"
                              id = salelinesPMD[0].order_id.id
                         elif len(salelinesPM)>1:
                              statePM="multiReserverd"
                              draftPM="No"
                              id = salelinesPM.mapped("order_id.id")
                         else:
                              statePM="Reserverd"
                              draftPM="No"
                              id = salelinesPM[0].order_id.id


                         values.append({"date":date,
                                         "state":statePM,
                                         "room_id":room.id,
                                         "is_draft":draftPM,
                                         "data_model":"sale.order",
                                         'data_id': id,
                                         'blocked':blocked,
                                         })


                room_summary.append({'name':room.name,'value':values})
            report.summary_header =[{'header':listdate}]
            report.room_summary=room_summary
            rcontext['o'] = report
            result['html'] = self.env.ref(
                'website_booking.report_summary_report').render(
                    rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        # Compute report data

        self.refresh()
