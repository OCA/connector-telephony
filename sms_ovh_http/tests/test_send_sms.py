# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests_mock

from odoo.tests import SavepointCase

from ..models.sms_api import OVH_HTTP_ENDPOINT


class SendSmsCase(SavepointCase):
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
            }
        )

    def test_check_service_name(self):
        self.assertEqual(self.account.service_name, "sms")

    def test_sending_sms(self):
        with requests_mock.Mocker() as m:
            m.get(OVH_HTTP_ENDPOINT, text="OK")
            self.env["sms.api"]._send_sms_batch(
                [
                    {
                        "number": "+3360707070707",
                        "content": "Alpha Bravo Charlie",
                        "res_id": 42,
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
            partner._message_sms("Alpha Bravo Charlie")
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
