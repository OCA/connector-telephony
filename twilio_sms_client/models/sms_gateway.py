# coding: utf-8
# Copyright 2017 OpenSynergy Indonesia <https://opensynergy-indonesia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields
from ..models.keychain import TWILIO_KEYCHAIN_NAMESPACE
from twilio.rest import Client
import logging

_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.gateway"

    method = fields.Selection(
        selection_add=[
            ("twilio", "TWILIO"),
        ],
    )

    @api.multi
    def _provider_get_provider_conf(self):
        for rec in self:
            keychain = rec.env["keychain.account"]
            if rec._check_permissions():
                retrieve = keychain.suspend_security().retrieve
            else:
                retrieve = keychain.retrieve
            accounts = retrieve(
                [["namespace", "=", TWILIO_KEYCHAIN_NAMESPACE]])
            return accounts[0]


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _prepare_twilio(self):

        keychain_account = self.gateway_id._provider_get_provider_conf()
        params = {
            "twilio_account": keychain_account["login"],
            "twilio_token": keychain_account.get_password(),
            "from": self.gateway_id.from_provider,
            "to": self._convert_to_e164(self.mobile),
            "message": self.message,
        }
        if self.nostop:
            params["noStop"] = 1
        if self.deferred:
            params["deferred"] = self.deferred
        if self.classes:
            params["class"] = self.classes
        if self.tag:
            params["tag"] = self.tag
        if self.coding:
            params["smsCoding"] = self.coding
        return params

    @api.model
    def _convert_to_e164(self, erp_number):
        to_dial_number = erp_number.replace(u"\xa0", u"")
        return to_dial_number

    @api.multi
    def _send_twilio(self):
        self.ensure_one()
        params = self._prepare_twilio()
        client = Client(
            params["twilio_account"],
            params["twilio_token"],
        )
        client.messages.create(
            to=params["to"],
            from_=params["from"],
            body=params["message"]
        )
