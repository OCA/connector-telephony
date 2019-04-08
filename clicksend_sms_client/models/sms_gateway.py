# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# Valentin CHEMIERE <valentin.chemiere@akretion.com>
# Copyright (C) 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from ..models.keychain import CLICKSEND_KEYCHAIN_NAMESPACE
import requests
import logging
from xml.etree.ElementTree import fromstring

_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.gateway"

    method = fields.Selection(selection_add=[
        ('http_clicksend', 'ClickSend HTTP')])

    @api.multi
    def _provider_get_provider_conf(self):
        for rec in self:
            keychain = rec.env['keychain.account']
            # TODO: implement suspend_security module
            # if rec._check_permissions():
            #    retrieve = keychain.suspend_security().retrieve
            # else:
            #    retrieve = keychain.retrieve
            retrieve = keychain.retrieve
            accounts = retrieve(
                [['namespace', '=', CLICKSEND_KEYCHAIN_NAMESPACE]])
            return accounts[0]


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _prepare_http_clicksend(self):

        keychain_account = self.gateway_id._provider_get_provider_conf()
        params = {
            'username': keychain_account['login'],
            'key': keychain_account._get_password(),
            'senderid': self.gateway_id.from_provider,
            'url': self.gateway_id.url,
            'to': self._convert_to_e164(self.mobile),
            'message': self.message,
            }
        return params

    @api.model
    def _convert_to_e164(self, erp_number):
        to_dial_number = erp_number.replace(u'\xa0', u'')
        return to_dial_number

    @api.multi
    def _send_http_clicksend(self):
        self.ensure_one()
        params = self._prepare_http_clicksend()
        r = requests.get(params['url'], params=params.items())
        params.update({
            'password': '*****',
            'to': '*****',
            'username': '*****',
            })
        _logger.debug("Call ClickSend API : %s params %s",
                      params['url'], params)
        response = r.text
        xml_response = fromstring(response)
        for messages in xml_response:
            for message in messages:
                for element in message:
                    if element.tag == 'result' and \
                            element.text != '0000':
                        raise ValueError(response)
