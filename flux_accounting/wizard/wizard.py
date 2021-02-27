# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.http import request
import logging
import datetime
import base64
logger = logging.getLogger(__name__)


class ReportCalculSpecifique(models.AbstractModel):
    _name = 'report.flux_accounting.report_rapport_bjorn_doc'

    #@api.model
    #def render_html(self, docids, data=None):
    #    report_obj = self.env['report']
    #    report = report_obj._get_report_from_name('flux_accounting.action_report_rapport_bjorn_doc')
    #    docargs = {
    #        'doc_ids': docids,
    #        'doc_model': report.model,
    #        'docs': data,
    #    }
    #    return report_obj.render('flux_accounting.action_report_rapport_bjorn_doc', docargs)

    @api.model
    def get_details(self, invoices):

        account = []
        account_date = []
        total_credit = {}
        total_debit = {}
        detail = {}
        account_lst_name = {}
        for invoice in invoices:
            moves = self.env['account.move'].search([('name','=',invoice.number)])
            for move in moves:
                for line in move.line_ids:
                    account_code = line.account_id.code
                    account_name = line.account_id.name
                    debit = line.debit
                    credit = line.credit
                    qty = line.quantity
                    date = line.date

                    account_total_credit = total_credit.get("account_code",0.0) + (credit * qty)
                    account_total_debit = total_debit.get("account_code",0.0) + (debit * qty)
                    total_credit.update({account_code:account_total_credit})
                    total_debit.update({account_code:account_total_debit})

                    detail_account = detail.get(account_code,[])

                    detail_account.append({
                                   'date': date,
                                   'code': account_code,
                                   'name': account_name,
                                    'ref': invoice.number,
                                   'debit': debit*qty,
                                   'credit': credit*qty,
                                   })

                    detail.update({account_code:detail_account})

                    # sauver la liste des code account
                    if account_code not in account:
                        account.append(account_code)
                        account_lst_name.update({account_code:account_name})

        return sorted(account), account_lst_name, total_credit, total_debit, detail

    @api.model
    def get_report_values(self, docids, data=None):
        docs = []
        month = int(data['form']['month'])
        year = int(data['form']['year'])
        ifdetail = data['form']['detail']
        com_id = data['form']['company_id']
        company = self.env["res.company"].browse(int(com_id))
        invoices = self.env["account.invoice"].search([('company_id',"=",company.id),('type','not in',['draft','cancel']),("date", ">=", "%s-%s-01" % (year,month)),("date","<", "%s-%s-01" % (year+1 if month==12 else year,month+1 if month<=11 else 1))])

        account, account_name,total_credit, total_debit, detail= self.get_details(invoices)

        docs.append({
            'company_name': company.name,
            'month': month,
            'year': year,
            'ifdetail': ifdetail,
            'detail': detail,
            'account': account,
            'account_name': account_name,
            'total_credit': total_credit,
            'total_debit': total_debit,
            'currency:': self.env.ref('base.main_company').currency_id,
        })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }



class account_check_echeancier(models.TransientModel):
    _name = 'account.export.data'
    _description = 'export data'

    x_month = fields.Integer(string="Month",required=1)
    x_year = fields.Integer(string="Year",required=1)
    x_detail = fields.Boolean(string="Detail",default=False)
    x_company_id = fields.Many2one("res.company",string="Company",required=1)

    @api.multi
    def account_export_data(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'year': self.x_year,
                'month': self.x_month,
                'company_id': self.x_company_id.id,
                'detail': self.x_detail,
            },
        }

        return self.env.ref("flux_accounting.action_report_rapport_bjorn_doc").report_action(self, data=data)

    def _generate_document_bjorn(self):

        mail_mail = self.env['mail.mail']
        x_year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        x_month = fields.Date.from_string(fields.Date.today()).strftime('%m')

        for x_detail in [0,1]:
            for company in self.env["res.company"].search([]):
                mail_ids = []
                attachment_ids = []

                email_to = "fmo@olabs.be"

                data_report = self.env['account.export.data'].create({
                    'x_year': x_year,
                    'x_month': x_month,
                    'x_detail': x_detail,
                    'x_company_id': company.id,
                })

                data = {
                    'ids': data_report.id,
                    'model': 'account.export.data',
                    'form': {
                        'year': x_year,
                        'month': x_month,
                        'company_id': company.id,
                        'detail': x_detail,
                    },
                }

                pdf = self.env.ref("flux_accounting.action_report_rapport_bjorn_doc").render(self, data=data)[0]

                attachement = self.env['ir.attachment'].create({
                    'name': 'report_%s_%s_%s.pdf' % (x_month,x_year,company.name),
                    'datas_fname': 'report_%s_%s_%s.pdf' % (x_month,x_year,company.name),
                    'type': 'binary',
                    'datas': base64.b64encode(pdf),
                    'mimetype': 'application/x-pdf'
                })

                attachment_ids.append(attachement.id)
                subject = "Report : %s" % company.name    # # your object Name ref
                body = """Hello,
        
                FROM Odoo System
        
                Kind regards.
                """
                mail=mail_mail.create({
                                                     'email_to': email_to,
                                                     'subject': subject,
                                                     'body_html': '<pre>%s</pre>' % body,
                                                     'attachment_ids': [(6, 0, attachment_ids)],
                                                 })
                mail.send()

