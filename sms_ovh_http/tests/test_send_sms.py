# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid

import requests_mock

from odoo.tests import TransactionCase

from ..models.sms_api import OVH_HTTP_ENDPOINT


class SendSmsCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env["iap.account"].create(
            {
                "name": "OVH",
                "provider": "sms_ovh_http",
                "sms_ovh_http_account": "foo",
                "sms_ovh_http_login": "bar",
                "sms_ovh_http_password": "secret",
                "sms_ovh_http_from": "+33642424242",
                "service_id": cls.env.ref("sms_ovh_http.iap_service_sms_ovh").id,
            }
        )
        cls.gateway = cls.env.ref("sms_ovh_http.ovh_gateway_iap")
        cls.gateway.iap_account_id = cls.account

    def test_check_service_name(self):
        self.assertEqual(self.account.service_name, "sms_ovh_http")

    def test_sending_sms(self):
        with requests_mock.Mocker() as m:
            m.get(OVH_HTTP_ENDPOINT, text="OK")
            gateway = self.env["ir.sms.gateway"].search(
                [("iap_account_id", "=", self.account.id)], limit=1
            )
            sms_api = gateway._get_api_class()(self.env, self.account)
            sms_api._send_sms_batch(
                [
                    {
                        "numbers": [{"number": "+3360707070707", "uuid": uuid.uuid1()}],
                        "content": "Alpha Bravo Charlie",
                    }
                ]
            )
            self.assertEqual(len(m.request_history), 1)
            params = m.request_history[0].qs
            self.assertEqual(
                params,
                {
                    "nostop": ["1"],
                    "from": ["+33642424242"],
                    "password": ["secret"],
                    "message": ["alpha bravo charlie"],
                    "to": ["+3360707070707"],
                    "smsaccount": ["foo"],
                    "login": ["bar"],
                },
            )

    def test_partner_message_sms(self):
        with requests_mock.Mocker() as m:
            m.get(OVH_HTTP_ENDPOINT, text="OK")
            partner = self.env["res.partner"].create(
                {"name": "FOO", "mobile": "+3360707070707"}
            )
            gateway = self.env["ir.sms.gateway"].search(
                [("iap_account_id", "=", self.account.id)], limit=1
            )
            partner.with_context(sms_gateway_id=gateway)._message_sms(
                "Alpha Bravo Charlie"
            )
            self.assertEqual(len(m.request_history), 1)
            params = m.request_history[0].qs
            self.assertEqual(
                params,
                {
                    "nostop": ["1"],
                    "from": ["+33642424242"],
                    "password": ["secret"],
                    "message": ["alpha bravo charlie"],
                    "to": ["+3360707070707"],
                    "smsaccount": ["foo"],
                    "login": ["bar"],
                },
            )
