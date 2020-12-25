# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RegistrationEditor(models.TransientModel):
    _inherit = "registration.editor"

    #modification du wizard pour ne pas afficher plusieurs fois les mêmes personnes
    #suite à la modification qui permet de lier des articles a un event => duplication des lignes.

    sale_order_id = fields.Many2one('sale.order', 'Sales Order', required=True)
    event_registration_ids = fields.One2many('registration.editor.line', 'editor_id', string='Registrations to Edit')

    @api.model
    def default_get(self, fields):
        # Remplacer la function standard
        # pour afficher les personnes inscrites par ligne.

        res = super(RegistrationEditor, self).default_get(fields)
        if not res.get('sale_order_id'):
            sale_order_id = res.get('sale_order_id', self._context.get('active_id'))
            res['sale_order_id'] = sale_order_id
        sale_order = self.env['sale.order'].browse(res.get('sale_order_id'))
        registrations = self.env['event.registration'].search([
            ('sale_order_id', '=', sale_order.id),
            ('event_ticket_id', 'in', sale_order.mapped('order_line.event_ticket_id').ids),
            ('state', '!=', 'cancel')])

        attendee_list=[]
        for so_line in [l for l in sale_order.order_line if l.event_ticket_id]:
            #print(so_line.name)
            #print(so_line.event_ticket_id)
            #
            # Filtrer les inscriptions par ligne car cela bug au moment de la confirmation.
            #
            existing_registrations = registrations.filtered(lambda self: self.sale_order_line_id.id == so_line.id)
            for reg in existing_registrations:
                    attendee_list.append({
                        'event_id': reg.event_id.id,
                        'event_ticket_id': reg.event_ticket_id.id,
                        'registration_id': reg.id,
                        'name': reg.name,
                        'email': reg.email,
                        'phone': reg.phone,
                        'sale_order_line_id': so_line.id,
                    })
            #si la qty est différente..., ajouter / retirer des inscrits
            for count in range(int(so_line.product_uom_qty) - len(existing_registrations)):
                attendee_list.append([0, 0, {
                        'event_id': so_line.event_id.id,
                        'event_ticket_id': so_line.event_ticket_id.id,
                        'sale_order_line_id': so_line.id,
                }])
        res['event_registration_ids'] = attendee_list
        res = self._convert_to_write(res)
        return res

    @api.multi
    def action_make_registration(self):
        self.ensure_one()
        for registration_line in self.event_registration_ids:
            values = registration_line.get_registration_data()
            if registration_line.registration_id:
                registration_line.registration_id.write(values)
            else:
                self.env['event.registration'].create(values)
        if self.env.context.get('active_model') == 'sale.order':
            for order in self.env['sale.order'].browse(self.env.context.get('active_ids', [])):
                order.order_line._update_registrations(confirm=False)
        return {'type': 'ir.actions.act_window_close'}



class RegistrationEditorLine(models.TransientModel):
    _inherit = "registration.editor.line"

    editor_id = fields.Many2one('registration.editor')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line')
    event_id = fields.Many2one('event.event', string='Event', required=True)
    registration_id = fields.Many2one('event.registration', 'Original Registration')
    event_ticket_id = fields.Many2one('event.event.ticket', string='Event Ticket')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    name = fields.Char(string='Name', index=True)

    @api.multi
    def get_registration_data(self):
        self.ensure_one()
        return {
            'event_id': self.event_id.id,
            'event_ticket_id': self.event_ticket_id.id,
            'partner_id': self.editor_id.sale_order_id.partner_id.id,
            'name': self.name or self.editor_id.sale_order_id.partner_id.name,
            'phone': self.phone or self.editor_id.sale_order_id.partner_id.phone,
            'email': self.email or self.editor_id.sale_order_id.partner_id.email,
            'origin': self.editor_id.sale_order_id.name,
            'sale_order_id': self.editor_id.sale_order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
        }
