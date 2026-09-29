# Copyright (C) 2021 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSmsNoAlterBody(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "FOO", "mobile": "+33607070707"}
        )

    def test_force_sms_body(self):
        message = self.partner._message_sms("Welcome to https://akretion.com/fr")
        message_sms_body = (
            self.env["sms.sms"].search([("mail_message_id", "=", message.id)]).body
        )
        self.assertEqual(message_sms_body, "Welcome to https://akretion.com/fr")
