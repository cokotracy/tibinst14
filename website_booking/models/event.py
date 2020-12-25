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

class Answer(models.Model):
    _inherit="event.event"

    x_speaker=fields.Many2many("res.partner",'speaker',string="Speaker")
    x_translator=fields.Many2many("res.partner",'translator',string="Translator")
    x_product=fields.Many2many("product.product",'products',string="Product mandatory")


    def AddQuestion(self, force=False):

        for event in self:
            if not event.question_ids or force:
                event.write({'question_ids': [(5, 0,0)]})
                question_ids = event.write({'question_ids':[(0, 0,
                                                           {'title': 'Type de logement', 'sequence': 1, 'is_individual': 1},
                                                           )]})
                event.question_ids[0].with_context(lang='nl_BE').write({'title': 'Accommodatie'})

                question_ids = event.write({'question_ids':[(0, 0,
                                                           {'title': "Jour d'arrivée", 'sequence': 2, 'is_individual': 0},
                                                               )]})
                event.question_ids[1].with_context(lang='nl_BE').write({'title': 'Aankomstdatum'})

                question_ids = event.write({'question_ids':[(0, 0,
                                                           {'title': "Jour du départ", 'sequence': 3, 'is_individual': 0},
                                                           )]})
                event.question_ids[2].with_context(lang='nl_BE').write({'title': 'Vertrekdatum'})

                question_ids=[]
                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Pas besoin de logement", 'sequence': 1},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Zonder overnachting'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Chambre commune homme", 'sequence': 2,'x_type_logement':197},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Gemeenschappelijke kamer man'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Chambre commune femme", 'sequence': 3,'x_type_logement':139},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Gemeenschappelijke kamer vrouw'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Chambre 1 lit", 'sequence': 1,'x_type_logement':195},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Eenpersoonskamer'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Chambre 2 lits", 'sequence': 5,'x_type_logement':196},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Tweepersoonskamer'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Studio 1 lit", 'sequence': 6,'x_type_logement': 148},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Eenpersoonsstudio'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[0].id, 'x_days': 0 ,'name': "Studio 2 lits", 'sequence': 7,'x_type_logement':149},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'Tweepersoonsstudio'})


                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[1].id, 'x_days': 0 ,'name': "Le jour de l'évènement", 'sequence': 1,},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'De dag van het evenement'})

                #question_ids = self.env["event.answer"].create(
                #               {'question_id': event.question_ids[1].id, 'x_days': 0 ,'name': "Le jour de l'évènement (avant le petit déjeuner)", 'sequence': 2,'x_product_ids':[(6, 0,[3407])]},
                #               )
                #question_ids.with_context(lang='nl_BE').write({'name': 'De dag van het evenement (voor het ontbijt)'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[1].id, 'x_days': -1 ,'name': "1 jour avant (avant le souper)", 'sequence': 3,'x_product_ids':[(6, 0,[])]}, #3407
                               )
                question_ids.with_context(lang='nl_BE').write({'name': '1 dag eerder (voor het avondmaal)'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[1].id, 'x_days': -1 ,'name': "1 jour avant (avant le dîner)", 'sequence': 4,'x_product_ids':[(6, 0,[3445])]},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': '1 dag eerder (voor de lunch)'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[2].id, 'x_days': 0 ,'name': "Le jour de l'évènement", 'sequence': 1},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'De dag van het evenement'})

                #question_ids = self.env["event.answer"].create(
                #               {'question_id': event.question_ids[2].id, 'x_days': 0 ,'name': "Le jour de l'évènement (aprés le souper)", 'sequence': 2,'x_product_ids':[(6, 0,[3589])]},
                #               )
                #question_ids.with_context(lang='nl_BE').write({'name': 'De dag van het evenement (na het avondmaal)'})

                question_ids = self.env["event.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "Le lendemain (après le dîner)",
                     'sequence': 3, 'x_product_ids': [(6, 0, [3445])]},
                )
                question_ids.with_context(lang='nl_BE').write({'name': 'De volgende dag (na de lunch)'})

                question_ids = self.env["event.answer"].create(
                               {'question_id': event.question_ids[2].id , 'x_days': 1 ,'name': "Le lendemain (après le souper)", 'sequence': 4,'x_product_ids':[(6, 0,[3445,3589])]},
                               )
                question_ids.with_context(lang='nl_BE').write({'name': 'De volgende dag (na het avondmaal)'})



    def RestoreQuestion(self):

        #Yoga Studio Paramita : 161
        #Shared Room Women : 139
        #Studio 1P : 148
        #Studio 2P : 149
        #ABC 1pers.Bedroom : 195
        #ABC 2pers.Bedroom : 196
        #Shared Room Men : 197

        for event in self.env["event.event"].search([('company_id', '=', 1)]):
            event.AddQuestion(True)
