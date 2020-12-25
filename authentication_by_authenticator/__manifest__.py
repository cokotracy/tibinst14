# -*- coding: utf-8 -*-
#######################################################################################
#                                                                                     #
#Copyright (C) Monoyer Fabian (info@olabs.be)                                         #
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

{
    'name': 'Authentication By Authenticator Google',
    'version': '11.0.1.',
    'depends': ['base','web'],
    'author': "O'Labs",
    'price':49,
    'currency':'EUR',
    'category':'Extra Tools',
    'website':'http://www.olabs.be',
    'description': """

Authentication By Authentificator.
===================================
Google Authenticator is an application that implements two-step verification services using the Time-based One-time Password Algorithm and HMAC-based One-time Password Algorithm , for authenticating users. The service implements algorithms specified in RFC 6238 and RFC 4226.[2]

Authenticator provides a six- to eight-digit one-time password which users must provide in addition to their username and password to log in to Odoo.    """,
    'data': [
        'views/user_view.xml',
        'views/frontend.xml',
     ],
    "external_dependencies": {
    'python': ['pyotp']
},
    'images':['static/description/banner.jpg',],
    'installable': True,
    'licence':"OPL-1",
}
