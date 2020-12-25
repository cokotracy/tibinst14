# -*- coding: utf-8 -*-

from odoo import fields,models,api
from odoo import tools
import pyotp
import qrcode
from io import BytesIO
import base64

class user_authenticator(models.Model):
    _inherit='res.users'

    x_authenticator=fields.Boolean(string="Authenticate by Authenticator")
    x_key=fields.Char(string='Key')
    x_qrcode=fields.Binary(string='QR code')

    @api.onchange('x_authenticator')
    def _generate_key(self):
        for record in self:
            if record.x_authenticator:
               record.x_key=pyotp.random_base32()
               qr = qrcode.QRCode(
                 version=1,
                 error_correction=qrcode.constants.ERROR_CORRECT_L,
                 box_size=10,
                 border=4,
               )
               qr.add_data('otpauth://totp/%s?secret=%s'% (record.login,record.x_key))
               qr.make(fit=True)
               img = qr.make_image()
               buffer=BytesIO()
               img.save(buffer)
               data=base64.encodestring(buffer.getvalue())
               record.x_qrcode=tools.image_resize_image_big(data)



