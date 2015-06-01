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

from openerp import fields, api, models, _
from openerp.exceptions import Warning
import urllib
import logging
_logger = logging.getLogger(__name__)

try:
    from SOAPpy import WSDL
except:
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install"
                    "it: e.g.: apt-get install python-soappy")


class smsclient(models.Model):
    _inherit = "sms.smsclient"

    @api.model
    def get_method(self):
        method = super(smsclient, self).get_method()
        method.append(('ovh smpp', 'OVH SMPP'), )
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

    @api.model
    def _send_message(self, data):
        super(smsclient, self)._send_message(data)
        gateway = data.gateway
        if gateway:
            if not self._check_permissions(gateway):
                raise Warning(_('You have no permission to access %s ')
                              % (gateway.name,))
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                prms['smsAccount'] = gateway.sms_account
                prms['login'] = gateway.login_provider
                prms['password'] = gateway.password_provider
                prms['from'] = gateway.from_provider
                prms['to'] = data.mobile_to
                prms['message'] = data.text
                if gateway.nostop:
                    prms['noStop'] = 1
                if gateway.deferred:
                    prms['deferred'] = gateway.deferred
                if gateway.classes:
                    prms['class'] = gateway.classes
                if gateway.tag:
                    prms['tag'] = gateway.tag
                if gateway.coding:
                    prms['smsCoding'] = gateway.coding
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.env['sms.smsclient.queue']
            vals = self._prepare_smsclient_queue(data, name)
            queue_obj.create(vals)
        return True
