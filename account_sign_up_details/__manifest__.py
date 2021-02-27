# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{

  "name"                 :  "Website Date-Of-Birth and gender",
  "summary"              :  "Add a mandatory field for users to share their date of birth, gender during the sign up.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "O'labs",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com",
  "description"          :  """https://store.webkul.com""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=account_sign_up_details&version=11.0",
  "depends"              :  [
                             'auth_signup',
                             'portal',
                            ],
  "data"                 :  [
                             'views/res_partner_view.xml',
                             'views/account_details_template.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,

}
