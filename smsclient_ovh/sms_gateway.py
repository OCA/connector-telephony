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
import requests
import logging
_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.gateway"

    @api.model
    def get_method(self):
        method = super(SmsClient, self).get_method()
        method.append(('http_ovh', 'OVH HTTP'), )
        return method

    @api.onchange('method')
    def onchange_method(self):
        super(SmsClient, self).onchange_method()
        if self.method == 'http_ovh':
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
    def _prepare_http_ovh(self):
        params = {
            'smsAccount': self.gateway_id.sms_account,
            'login': self.gateway_id.login_provider,
            'password': self.gateway_id.password_provider,
            'from': self.gateway_id.from_provider,
            'to': self.mobile,
            'message': self.message,
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

    @api.multi
    def _send_http_ovh(self):
        self.ensure_one()
        params = self._prepare_http_ovh().items()
        r = requests.get(self.gateway_id.url, params=params)
        _logger.debug("Call OVH API : %s params %s",
                      self.gateway_id.url, params)
        response = r.text
        if response[0:2] != 'OK':
            raise ValueError(response)
