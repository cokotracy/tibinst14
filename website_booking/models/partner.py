# -*- coding: utf-8 -*-
# #Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
#                                                                                     #
#Odoo Proprietary License v1.0                                                        #
#                                                                                     #
#This software and associated files (the "Software") may only be used (executed,      #
#modified, executed after modifications) if you have purchased a valid license        #
#from the authors, typically via Odoo Apps, or if you have received a written         #
#agreement from the authors of the Software (see the COPYRIGHT file).                 #
#                                                                                     #
#You may develop Odoo modules that use the Software as a library (typically           #
#by depending on it, importing it and using its resources), but without copying       #
#any source code or material from the Software. You may distribute those              #
#modules under the license of your choice, provided that this license is              #
#compatible with the terms of the Odoo Proprietary License (For example:              #
#LGPL, MIT, or proprietary licenses similar to this one).                             #
#                                                                                     #
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software   #
#or modified copies of the Software.                                                  #
#                                                                                     #
#The above copyright notice and this permission notice must be included in all        #
#copies or substantial portions of the Software.                                      #
#                                                                                     #
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR           #
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,             #
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.                                #
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,          #
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,     #
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER          #
#DEALINGS IN THE SOFTWARE.                                                            #
#######################################################################################
from odoo import api, fields, models, _

#ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id','barcode')


class Partner(models.Model):
    _inherit="res.partner"

    x_is_hotel=fields.Boolean(string="Is a Hotel")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',default=20)
    barcode = fields.Char(string="Id unique", store=True,Readonly=True,copy=False)


    @api.model
    def copy_multi_property(self, property_name, model, ids, source_company_id, target_company_id):
        property = self.env['ir.property']
        source_property = property.with_context(force_company=source_company_id)
        target_property = property.with_context(force_company=target_company_id)
        values = source_property.get_multi(property_name, model, ids)
        target_property.set_multi(property_name, model, values)


    def write(self, values):
        result = super(Partner,self).write(values)
        company_user_id = self.env.user.company_id.id
        if values.get('property_product_pricelist',False):
            for company in self.env["res.company"].search([]):
                self.copy_multi_property('property_product_pricelist',"res.partner",[self.id],company_user_id,company.id)
        return result

    #def _address_fields(self):
    #    """Returns the list of address fields that are synced from the parent."""
    #    return list(ADDRESS_FIELDS)
    
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name or ''

            if partner.company_name or partner.parent_id:
                if not name and partner.type in ['invoice', 'delivery', 'other']:
                    name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
                if not partner.is_company:
                    name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
            if self._context.get('show_address_only'):
                name = partner._display_address(without_company=True)
            if self._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if self._context.get('show_email') and partner.email:
                name = "%s <%s>" % (name, partner.email)
            if self._context.get('show_barcode') and partner.barcode:
                name = name +"\n"+ partner.barcode
            if self._context.get('html_format'):
                name = name.replace('\n', '<br/>')
            res.append((partner.id, name))
        return res

        
    @api.model
    def create(self, values):
        values['barcode'] = self.env['ir.sequence'].next_by_code('res.partner')
        record = super(Partner, self).create(values)
        company_user_id = self.env.user.company_id.id
        if values.get('property_product_pricelist',False):
            for company in self.env["res.company"].search([]):
                self.copy_multi_property('property_product_pricelist',"res.partner",[record.id],company_user_id,company.id)
        return record

        
    @api.model
    def _cron_membership_barcode(self):
        partners=self.search([("barcode","=",None)])
        for partner in partners:
            partner.write({'barcode':self.env['ir.sequence'].next_by_code('res.partner')})
       

    @api.model
    def _cron_generate_userportal(self):
        for partner in self.env["res.partner"].search([]):
            if partner.email:
                if partner.email.find("@")>0 and partner.email.find(".")>0:
                     user = self.env['res.users'].sudo().with_context(active_test=False).search_count([('login', '=', partner.email.replace(" ","").lower())])
                     if user==0:
                         company_id = self.env['res.company']._company_default_get('res.users').id
                         data={
                             'email': partner.email.lower().replace(" ",""),
                             'login': partner.email.lower().replace(" ",""),
                             'partner_id': partner.id,
                             'company_id': company_id,
                             'company_ids': [(6, 0, [1,3,4])],
                             'groups_id': [(6, 0, [10,5])],
                             'lang':partner.lang,
                         }
                         
                         self.env['res.users'].with_context(no_reset_password=True).create(data) 
                         self._cr.commit()         
                         
    @api.model
    def _cron_search_double_email(self):
        for partner in self.env["res.partner"].search([]):
            if partner.email:
                if partner.email.find("@")>0 and partner.email.find(".")>0:
                    email_count = self.env['res.partner'].search_count([("type","=","contact"),('email', '=', partner.email)])

                    if email_count>1:
                        for user in self.env['booking.config'].sudo().search([],limit=1).user_alert:
                            activity = self.env['mail.activity'].sudo().create({
                                        'activity_type_id': self.env.ref('website_booking.mail_activity_urgent').id,
                                        'note': _('The email for the partner is several times'),
                                        'res_id':  partner.id,
                                        'user_id': user.id,
                                        'res_model_id': self.env.ref('base.model_res_partner').id,
                                        })
                            activity._onchange_activity_type_id()
    
    def _commercial_fields(self):
             list=super(Partner, self)._commercial_fields() 
             list.remove('property_product_pricelist')
             return list

