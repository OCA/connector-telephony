# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

import requests

from odoo.tests import Form, HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSmsSmsboxHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Standard Odoo states, whatever other installed modules change.
        cls.startClassPatcher(
            mock.patch.object(
                type(cls.env["sms.sms"]),
                "IAP_TO_SMS_STATE_SUCCESS",
                {
                    "processing": "process",
                    "success": "pending",
                    "sent": "pending",
                    "delivered": "sent",
                },
            )
        )
        cls.account = cls.env["iap.account"].create(
            {
                "name": "SMSBOX",
                "service_id": cls.env.ref("sms.iap_service_sms").id,
                "provider": "sms_smsbox_http",
                "sms_smsbox_http_api_key": "pub-test",
            }
        )
        cls.env["ir.sms.gateway"].create(
            {
                "name": "SMSBOX",
                "gateway_type": "smsbox_http",
                "iap_account_id": cls.account.id,
                "sequence": 0,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "SMSBOX Partner", "mobile": "+33612345678"}
        )

    def _send_sms(self, answer):
        response = mock.Mock(text=answer, status_code=200)
        with mock.patch.object(requests.Session, "post", return_value=response) as post:
            message = self.partner._message_sms("Test", partner_ids=self.partner.ids)
        return message.notification_ids, post

    def test_account_service(self):
        account_form = Form(
            self.env["iap.account"].with_context(default_provider="sms_smsbox_http")
        )
        account_form.name = "SMSBOX 2"
        account = account_form.save()
        self.assertEqual(
            account.service_id,
            self.env.ref("sms_smsbox_http.iap_service_sms_smsbox_http"),
        )
        self.assertTrue(account.sms_smsbox_http_callback_token)

    def test_send_ok(self):
        notification, post = self._send_sms("OK 12345")
        self.assertEqual(notification.notification_status, "pending")
        tracker = notification.sms_tracker_ids
        self.assertEqual(tracker.sms_smsbox_http_reference, "12345")
        kwargs = post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["Authorization"], "App pub-test")
        self.assertEqual(kwargs["data"]["dest"], "33612345678")
        self.assertEqual(kwargs["data"]["cvar"], f"odoo_uuid={tracker.sms_uuid}")

    def test_send_errors(self):
        for answer, failure_type in (
            ("ERROR 03", "sms_credit"),
            ("ERROR 04", "sms_number_format"),
            ("ERROR", "unknown"),
        ):
            with self.subTest(answer=answer):
                notification, __ = self._send_sms(answer)
                self.assertEqual(notification.notification_status, "exception")
                self.assertEqual(notification.failure_type, failure_type)

    def test_delivery_report(self):
        token = self.account.sms_smsbox_http_callback_token
        self.assertEqual(
            self.url_open("/sms_smsbox_http/status/wrong?accuse=0").status_code, 404
        )
        for accuse, status, failure_type in (
            ("0", "sent", False),
            ("7", "bounce", "sms_invalid_destination"),
        ):
            with self.subTest(accuse=accuse):
                notification, __ = self._send_sms("OK 12345")
                uuid = notification.sms_tracker_ids.sms_uuid
                response = self.url_open(
                    f"/sms_smsbox_http/status/{token}"
                    f"?accuse={accuse}&odoo_uuid={uuid}&reference=12345"
                )
                self.assertEqual(response.text, "OK")
                notification.invalidate_recordset()
                self.assertEqual(notification.notification_status, status)
                self.assertEqual(notification.failure_type, failure_type)
