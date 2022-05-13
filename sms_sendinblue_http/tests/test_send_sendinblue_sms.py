# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests_mock

from odoo.exceptions import UserError
from odoo.tests import TransactionCase

from ..models.sms_api import SENDINBLUE_HTTP_ENDPOINT


class SendSmsCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env["iap.account"].create(
            {
                "name": "SENDINBLUE",
                "provider": "sms_sendinblue_http",
                "sms_sendinblue_http_api_key": "foo",
                "sms_sendinblue_http_from": "TEST",
            }
        )

    def test_get_credits_url(self):
        self.assertTrue("sendinblue.com" in self.account.get_credits_url("sms"))
        self.assertTrue("iap.odoo.com" in self.account.get_credits_url("other"))

    def test_check_service_name(self):
        self.assertEqual(self.account.service_name, "sms")

    def test_sending_sms(self):
        with requests_mock.Mocker() as m:
            m.post(
                SENDINBLUE_HTTP_ENDPOINT,
                status_code="201",
                json={
                    "reference": "123",
                    "messageId": 123,
                    "smsCount": 1,
                    "usedCredits": 1.0,
                    "remainingCredits": 55.32,
                },
            )
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
            params = m.request_history[0].json()
            self.assertEqual(
                params,
                {
                    "type": "transactional",
                    "unicodeEnabled": False,
                    "recipient": "+3360707070707",
                    "sender": "TEST",
                    "content": "Alpha Bravo Charlie",
                },
            )

    def test_partner_message_sms(self):
        with requests_mock.Mocker() as m:
            m.post(
                SENDINBLUE_HTTP_ENDPOINT,
                status_code="201",
                json={
                    "reference": "123",
                    "messageId": 123,
                    "smsCount": 1,
                    "usedCredits": 1.0,
                    "remainingCredits": 55.32,
                },
            )
            partner = self.env["res.partner"].create(
                {"name": "FOO", "mobile": "+3360707070707"}
            )
            partner._message_sms("Alpha Bravo Charlie")
            self.assertEqual(len(m.request_history), 1)
            params = m.request_history[0].json()
            self.assertEqual(
                params,
                {
                    "type": "transactional",
                    "unicodeEnabled": False,
                    "recipient": "+3360707070707",
                    "sender": "TEST",
                    "content": "Alpha Bravo Charlie",
                },
            )

    def test_sms_message_state_passe_case(self):
        with requests_mock.Mocker() as m:
            m.post(
                SENDINBLUE_HTTP_ENDPOINT,
                status_code="201",
                json={
                    "reference": "123",
                    "messageId": 123,
                    "smsCount": 1,
                    "usedCredits": 1.0,
                    "remainingCredits": 55.32,
                },
            )
            sms = self.env["sms.sms"].create(
                {
                    "number": "+33607070707",
                    "body": "SMS content",
                    "state": "outgoing",
                }
            )
            sms.send(unlink_sent=False)
            self.assertEqual(len(m.request_history), 1)
        sms = self.env["sms.sms"].search([])
        self.assertEqual(sms.state, "sent")

    def test_sms_message_state_failure_case(self):
        with requests_mock.Mocker() as m:
            m.post(
                SENDINBLUE_HTTP_ENDPOINT,
                status_code="400",
                json={
                    "code": "duplicate_parameter",
                    "message": "Test error message",
                },
            )
            partner = self.env["res.partner"].create(
                {"name": "FOO", "mobile": "+3360707070707"}
            )
            partner._message_sms("Alpha Bravo Charlie")
            self.assertEqual(len(m.request_history), 1)
        sms = self.env["sms.sms"].search([("partner_id", "=", partner.id)])
        self.assertEqual(sms.error_detail, "Test error message")
        self.assertEqual(sms.failure_type, "sms_sendinblue_duplicate_parameter")
        self.assertEqual(sms.state, "error")

    def test_no_number_case(self):
        sms = self.env["sms.sms"].create(
            {
                "number": None,
                "body": "SMS content",
                "state": "outgoing",
            }
        )
        sms.send()
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_number_format")

    def test_send_sms(self):
        with self.assertRaises(NotImplementedError):
            self.env["sms.api"]._send_sms("+33605050505", "content")

    def test_split_not_used_raise(self):
        with self.assertRaisesRegex(
            UserError,
            "Batch sending is not implemented by this module sms_sendinblue_http",
        ):

            SMSs = self.env["sms.sms"].create(
                [
                    {
                        "number": "+331",
                        "body": "SMS content",
                        "state": "outgoing",
                    },
                    {
                        "number": "+332",
                        "body": "SMS content",
                        "state": "outgoing",
                    },
                ]
            )
            self.env["sms.api"]._send_sms_batch(SMSs)

    def test_get_sms_api_error_messages(self):
        messages = self.env["sms.api"]._get_sms_api_error_messages()
        self.assertTrue(
            "https://app.sendinblue.com" in messages["not_enough_credits"],
            f"Couldn't found sendinblue.com in {messages['not_enough_credits']}",
        )
