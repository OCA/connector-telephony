# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import TransactionCase

from odoo.addons.sms_alternative_provider.models.sms_api import SmsApi


class TestSmsGateway(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Disable mail notifications to avoid search on non-stored sms_id
        cls.env = cls.env(
            context=dict(
                cls.env.context, mail_create_nosubscribe=True, mail_notify_noemail=True
            )
        )

        cls.env["ir.sms.gateway"].search([]).unlink()

        cls.gateway = cls.env["ir.sms.gateway"].create(
            {
                "name": "Test Gateway",
                "gateway_type": "iap",
                "sequence": 1,
                "active": True,
            }
        )

        cls.gateway2 = cls.env["ir.sms.gateway"].create(
            {
                "name": "Test Gateway 2",
                "gateway_type": "iap",
                "sequence": 2,
                "active": True,
            }
        )

    def test_description_computed(self):
        self.assertIn(SmsApi.DESCRIPTION, self.gateway.description)

    def test_get_api_class(self):
        self.assertEqual(self.gateway._get_api_class(), SmsApi)

    def test_get_default_gateway(self):
        IrSmsGateway = self.env["ir.sms.gateway"]
        self.assertEqual(self.gateway, IrSmsGateway._get_default_gateway())
        self.gateway.sequence = 2
        self.gateway2.sequence = 1
        self.assertEqual(self.gateway2, IrSmsGateway._get_default_gateway())
