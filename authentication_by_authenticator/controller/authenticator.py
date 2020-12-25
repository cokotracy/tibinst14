# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo import modules
import pyotp


class authenticate_web(http.Controller):

    @http.route('/web/authenticator/', type='http', auth="public", methods=['POST'], website=True)
    def verify(self,  **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        # if select database
        db= kw.pop('db', None)
        # login, password,..
        login= kw.pop('login', None)
        password = kw.pop('password', None)
        redirect = kw.pop('redirect', None)
        pincode= kw.pop('pincode', None)
        numpin= kw.pop('numpin', None)

        if not db:
            db=db_monodb()
        if not numpin:
            numpin=0

        registry = modules.registry.Registry(db)

        with registry.cursor() as cr:
            res_users = registry.get('res.users')
            iduser=res_users.authenticate(db, login, password,user_agent_env=None)
            cr.commit()
            if iduser != False:
                user=http.request.env['res.users'].sudo().browse([iduser])
                if int(numpin)>0 :
                    totp = pyotp.TOTP(user.x_key)
                    if pincode!=totp.now():
                        return request.env['ir.ui.view'].render_template('web.login', {'signup_enabled':True,'reset_password_enabled':True, 'error':'Wrong pincode '})
                    else:
                        url = "/web"
                        credentials = (cr.dbname, login, password)
                        return login_and_redirect(*credentials, redirect_url=url)
                if user.x_authenticator:
                    return request.env['ir.ui.view'].render_template('authentication_by_authenticator.authenticator', {
                        'login': login,
                        'password':password,
                        'db':db,
                        'redirect':redirect,
                        'numpin':1,
                    })
                else:
                        url = redirect or "/my/home"
                        credentials = (cr.dbname, login, password)
                        return login_and_redirect(*credentials, redirect_url=url)
                                           

        return request.env['ir.ui.view'].render_template('web.login', {'signup_enabled':True,'reset_password_enabled':True,'error':'Wrong login/password '})





