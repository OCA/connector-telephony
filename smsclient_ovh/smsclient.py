# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import api, models, _
from openerp.exceptions import Warning
import urllib
import logging
_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.smsclient"

    @api.model
    def get_method(self):
        method = super(smsclient, self).get_method()
        method.append(('ovh_http', 'OVH HTTP'), )
        return method

    @api.onchange('method')
    def onchange_method(self):
        super(smsclient, self).onchange_method()
        if self.method == 'ovh http':
            self.url_visible = True
            self.sms_account_visible = True
            self.login_provider_visible = True
            self.password_provider_visible = True
            self.from_provider_visible = True
            self.validity_visible = True
            self.classes_visible = True
            self.deferred_visible = True
            self.nostop_visible = True
            self.priority_visible = True
            self.coding_visible = True
            self.tag_visible = True
            self.char_limit_visible = True


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _prepare_ovh_http(self):
        params = {
            'smsAccount': gateway.sms_account,
            'login': gateway.login_provider,
            'password': gateway.password_provider,
            'from': gateway.from_provider,
            'to': self.mobile_to,
            'message': self.text,
            }
        if self.nostop:
            params['noStop'] = 1
        if self.deferred:
            params['deferred'] = self.deferred
        if self.classes:
            params['class'] = self.classes
        if self.tag:
            params['tag'] = self.tag
        if self.coding:
            params['smsCoding'] = self.coding
        return params
