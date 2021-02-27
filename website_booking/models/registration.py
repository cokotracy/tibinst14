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

class Registration(models.Model):
    _inherit = "event.registration"

    x_barcode = fields.Char(string='Identifiant')

    """
    @api.model
    def create(self,data):
        email=data.get('email',False)
        name=data.get('name',False)
        phone=data.get('phone',False)
        x_barcode=data.get('barcode',False)
        partner_id=data.get('partner_id',False)

        if email:
            if self.env["res.partner"].search_count([('email','=',email.lower())])==0:
                 if partner_id:
                     partner_link=self.env["res.partner"].browse(partner_id)

                 if partner_link and partner_link.active:
                    partner_data={'parent_id':partner_id,'type':'other','name':name,'email':email,'phone':phone}
                 else:
                    partner_data={'type':'other','name':name,'email':email,'phone':phone}

                 new_partner=self.env["res.partner"].create(partner_data)
                 company_id = self.env.context.get('company_id')
                 group_portal=self.env['res.groups'].sudo().search([('is_portal', '=', True)])[0]
                 self.env['res.users'].with_context(no_reset_password=False).create({
                 'email': new_partner.email,
                 'login': new_partner.email,
                 'partner_id': new_partner.id,
                 'company_id': new_partner.company_id.id,
                 'company_ids': [(6, 0,self.env["res.company"].sudo().search([]).mapped("id"))],
                 'groups_id': [(6, 0, [group_portal.id])],
        })
        return super(Registration,self).create(data)
    """