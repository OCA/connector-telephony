# coding: utf-8
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.gateway"

    @api.model
    def get_method(self):
        method = super(SmsClient, self).get_method()
        method.append(('http_ovh', 'OVH HTTP'), )
        return method

    @api.multi
    def _provider_get_provider_conf(self):
        for rec in self:
            keychain = rec.env['keychain.account']
            if rec._check_permissions:
                retrieve = keychain.suspend_security().retrieve
            else:
                retrieve = keychain.retrieve
            accounts = retrieve(
                [['namespace', '=', 'ovh_provider']])
            return accounts[0]


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _prepare_http_ovh(self):

        keychain_account = self.gateway_id._provider_get_provider_conf()
        keychain_json = json.loads(keychain_account['data'])
        params = {
            'smsAccount': keychain_json['sms_account'],
            'login': keychain_account['login'],
            'password': keychain_account.get_password(),
            'from': self.gateway_id.from_provider,
            'url': self.gateway_id.url,
            'to': self._convert_to_e164(self.mobile),
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

    @api.model
    def _convert_to_e164(self, erp_number):
        to_dial_number = erp_number.replace(u'\xa0', u'')
        return to_dial_number

    @api.multi
    def _send_http_ovh(self):
        self.ensure_one()
        params = self._prepare_http_ovh()
        r = requests.get(params['url'], params=params.items())
        params.update({
            'password': '*****',
            'to': '*****',
            'smsAccount': '*****',
            'login': '*****',
            })
        print params
        _logger.debug("Call OVH API : %s params %s",
                      params['url'], params)
        response = r.text
        if response[0:2] != 'OK':
            raise ValueError(response)
