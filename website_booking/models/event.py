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
    x_display_umbrella = fields.Boolean("Display on website Umbrella")
    x_snippet_text = fields.Text("Text for snippet", translate=True)
    x_snippet_image = fields.Binary("Image for snippet")

    def AddQuestion(self, force=False):

        for event in self:
            if not event.question_ids or force:
                event.write({'question_ids': [(5, 0, 0)]})
                question_ids = event.write({'question_ids': [(0, 0,
                                                              {'title': 'Accommodation', 'sequence': 1,
                                                               'once_per_order': 0},
                                                              )]})
                question_ids = event.write({'question_ids': [(0, 0,
                                                              {'title': "Arrival", 'sequence': 2,
                                                               'once_per_order': 1},
                                                              )]})

                question_ids = event.write({'question_ids': [(0, 0,
                                                              {'title': "Departure", 'sequence': 3,
                                                               'once_per_order': 1},
                                                              )]})

                question_ids = []
                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "NO",
                     'sequence': 1},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, shared room male",
                     'sequence': 2, 'x_room_id': self.env.ref('website_booking.product_room_shared_male_1_bed').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, shared room female",
                     'sequence': 3, 'x_room_id': self.env.ref('website_booking.product_room_shared_female_1_bed').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "YES, studio 1 pers.", 'sequence': 4,
                     'x_room_id': self.env.ref('website_booking.product_room_studio_1_bed').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "YES, room 1 pers.", 'sequence': 5,
                     'x_room_id': self.env.ref('website_booking.product_room_1_bed').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "Yes, Studio 2 pers.", 'sequence': 6,
                     'x_room_id': self.env.ref('website_booking.product_room_studio_2_bed').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[0].id, 'x_days': 0, 'name': "YES, room 2 pers.", 'sequence': 7,
                     'x_room_id': self.env.ref('website_booking.product_room_2_room').id},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[1].id, 'x_days': -1, 'name': "I’ll arrive the day before",
                     'sequence': 1, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_breakfast").id,self.env.ref("website_booking.product_lunch").id])]},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[1].id, 'x_days': 0, 'name': "I’ll arrive on the day of the event",
                     'sequence': 5, 'x_meal_ids': [(6, 0, [])]},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 0, 'name': "I’ll leave immediately at the end of the event",
                     'sequence': 1},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 0, 'name': "I’ll leave at the end of the event, after supper",
                     'sequence': 3, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_evening").id])]},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I’ll leave the day after the event, after breakfast",
                     'sequence': 5, 'x_meal_ids': [(6, 0, [])]},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I’ll leave the day after the event, after lunch",
                     'sequence': 5, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_lunch").id])]},
                )

                question_ids = self.env["event.question.answer"].create(
                    {'question_id': event.question_ids[2].id, 'x_days': 1, 'name': "I’ll leave the day after the event, after supper",
                     'sequence': 5, 'x_meal_ids': [(6, 0, [self.env.ref("website_booking.product_lunch").id,self.env.ref("website_booking.product_evening").id])]},
                )

    def RestoreQuestion(self):
        for event in self.env["event.event"].search([('company_id', '=', 1)]):
            event.AddQuestion(True)
