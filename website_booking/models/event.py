# -*- coding: utf-8 -*-
# #Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
#                                                                                     #
# Odoo Proprietary License v1.0                                                        #
#                                                                                     #
# This software and associated files (the "Software") may only be used (executed,      #
# modified, executed after modifications) if you have purchased a valid license        #
# from the authors, typically via Odoo Apps, or if you have received a written         #
# agreement from the authors of the Software (see the COPYRIGHT file).                 #
#                                                                                     #
# You may develop Odoo modules that use the Software as a library (typically           #
# by depending on it, importing it and using its resources), but without copying       #
# any source code or material from the Software. You may distribute those              #
# modules under the license of your choice, provided that this license is              #
# compatible with the terms of the Odoo Proprietary License (For example:              #
# LGPL, MIT, or proprietary licenses similar to this one).                             #
#                                                                                     #
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software   #
# or modified copies of the Software.                                                  #
#                                                                                     #
# The above copyright notice and this permission notice must be included in all        #
# copies or substantial portions of the Software.                                      #
#                                                                                     #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR           #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,             #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.                                #
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,          #
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,     #
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER          #
# DEALINGS IN THE SOFTWARE.                                                            #
#######################################################################################
from odoo import api, fields, models, _


class Answer(models.Model):
    _inherit = "event.event"

    x_speaker = fields.Many2many("res.partner", "speaker", string="Speaker")
    x_translator = fields.Many2many("res.partner", "transaltor", string="Translator")
    x_product = fields.Many2many("product.product",string="Meal include")
    x_display_umbrella = fields.Selection([("fr_BE","Umbrella FR"),("nl_BE","Umbrella NL")], string="Umbrella Lang")

    x_snippet_text = fields.Text("Text for snippet")
    x_snippet_image = fields.Binary("Image for snippet")

    def AddQuestion(self, force=False):

        for event in self:
            if not event.question_ids or force:
                event.write({'question_ids': [(5, 0, 0)]})
                res = event.write({'question_ids': [(0, 0,
                                                              {'title': 'Choice of accomodation', 'sequence': 1,
                                                               'once_per_order': 0},
                                                              )]})
                event.question_ids[0].with_context(lang="fr_BE").write({'title': 'Choisir un logement'})
                event.question_ids[0].with_context(lang="nl_BE").write({'title': 'Overnachting'})
                res = event.write({'question_ids': [(0, 0,
                                                              {'title': "If other day of arrival", 'sequence': 2,
                                                               'once_per_order': 1},
                                                              )]})

                event.question_ids[1].with_context(lang="fr_BE").write({'title': "Si autre jour que le jour d'arrivée"})
                event.question_ids[1].with_context(lang="nl_BE").write({'title': 'Indien aankomst op een andere dag'})
                res = event.write({'question_ids': [(0, 0,
                                                              {'title': "If other day of departure", 'sequence': 3,
                                                               'once_per_order': 1},
                                                              )]})
                event.question_ids[2].with_context(lang="fr_BE").write({'title': "Si autre jour que le jour de départ"})
                event.question_ids[2].with_context(lang="nl_BE").write({'title': 'Indien vertrek op een andere dag'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "No",
                     'sequence': 1},
                )
                res.with_context(lang="fr_BE").write({'name': "Non"})
                res.with_context(lang="nl_BE").write({'name': 'Nee'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, studio for 1 person", 'sequence': 2, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                     'x_room_id': self.env.ref('website_booking.product_room_studio_1_bed').id},
                )
                res.with_context(lang="fr_BE").write({'name': "Oui, un studio pour une personne"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, studio 1 pers.'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, Studio for 2 persons", 'sequence': 3, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                     'x_room_id': self.env.ref('website_booking.product_room_studio_2_bed').id},
                )
                res.with_context(lang="fr_BE").write({'name': "Oui, un studio pour 2 personnes (Lit double)"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, studio 2 pers. (dubbelbed)'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, Studio for 2 persons (2 beds)", 'sequence': 4, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                     'x_room_id': self.env.ref('website_booking.product_room_studio_2_2_bed').id},
                )
                res.with_context(lang="fr_BE").write({'name': "Oui, un studio pour 2 personnes (2 lits)"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, studio 2 pers. (2 bedden)'})


                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, room for 1 person (", 'sequence': 5, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                     'x_room_id': self.env.ref('website_booking.product_room_1_bed').id},
                )
                res.with_context(lang="fr_BE").write({'name': "Oui, une chambre pour 1 personne"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, kamer 1 pers.'})


                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, room for 2 persons",
                     'sequence': 6, 'x_meal_ids': [
                        (6, 0, [self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                     'x_room_id': self.env.ref('website_booking.product_room_2_room').id},
                )
                res.with_context(lang="fr_BE").write({'name': "Oui, une chambre pour 2 personnes"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, kamer 2 pers.'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, shared room male",
                     'sequence': 7, 'x_room_id': self.env.ref('website_booking.product_room_shared_male_1_bed').id, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                })

                res.with_context(lang="fr_BE").write({'name': "Oui, une chambre partagée pour homme"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, gedeelde kamer mannen'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, shared room female",
                     'sequence': 8, 'x_room_id': self.env.ref('website_booking.product_room_shared_female_1_bed').id, 'x_meal_ids': [(6,0,[self.env.ref("__export__.product_template_41_379561bc").product_variant_ids[0].id])],
                })

                res.with_context(lang="fr_BE").write({'name': "Oui, une chambre partagée pour homme"})
                res.with_context(lang="nl_BE").write({'name': 'Ja, gedeelde kamer vrouwen'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[1].id, 'x_days': 0, 'name': "I’ll arrive on the day of the event",
                     'sequence': 1, 'x_meal_ids': [(6, 0, [])]},
                )

                res.with_context(lang="fr_BE").write({'name': "J'arrive le jour de l'événement"})
                res.with_context(lang="nl_BE").write({'name': 'Ik kom aan op de dag van het programma'})

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[1].id, 'x_days': -1, 'name': "I arrive the day before and have supper",
                     'sequence': 2, 'x_meal_ids': [(6, 0, [])]},
                )

                res.with_context(lang="fr_BE").write({'name': "J'arrive la veille et je souperai"})
                res.with_context(lang="nl_BE").write({'name': 'Ik kom de dag voordien voor het avondmaal'})


                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 0, 'name': "I’ll leave immediately at the end of the event",
                     'sequence': 1},
                )

                res.with_context(lang="fr_BE").write({'name': "Je partirai immédiatement à la fin de l'événement"})
                res.with_context(lang="nl_BE").write({'name': 'Ik vertrek onmiddellijk na het programma'})

                #question_ids = self.env["event.question.answer"].create(
                #    {'question_id': event.question_ids[2].id, 'x_days': 0, 'name': "I’ll leave at the end of the event, after supper",
                #     'sequence': 3, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_evening").id])]},
                #)

                res = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I leave the day after and have breakfast",
                     'sequence': 2, 'x_meal_ids': [(6, 0, [])]},
                )
                res.with_context(lang="fr_BE").write({'name': "Je pars le lendemain et je prends le petit déjeuner"})
                res.with_context(lang="nl_BE").write({'name': 'Ik vertrek de dag nadien na het ontbijt'})

                #question_ids = self.env["event.question.answer"].create(
                #    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I’ll leave the day after the event, after lunch",
                #     'sequence': 5, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_lunch").id])]},
                #)

                #question_ids = self.env["event.question.answer"].create(
                #    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I’ll leave the day after the event, after supper",
                #     'sequence': 5, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_lunch").id,self.env.ref("website_booking.product_evening").id])]},
                #)

    def RestoreQuestion(self):
        for event in self.env["event.event"].search([('company_id', '=', 1)]):
            event.AddQuestion(True)
