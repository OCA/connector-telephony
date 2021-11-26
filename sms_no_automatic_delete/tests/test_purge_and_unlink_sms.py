# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase

from odoo.addons.sms.tests.common import MockSMS


class TestSmsPurgeAndUnlink(TransactionCase, MockSMS):
    def setUp(self):
        super(TestSmsPurgeAndUnlink, self).setUp()
        self.sms_sms = self.env["sms.sms"]
        self.sms1 = self.sms_sms.create(
            {
                "state": "outgoing",
                "write_date": datetime.now() - timedelta(days=30),
            }
        )
        self.sms2 = self.sms_sms.create(
            {
                "state": "outgoing",
                "write_date": datetime.now() - timedelta(days=61),
            }
        )
        self.sms3 = self.sms_sms.create(
            {
                "state": "outgoing",
                "write_date": datetime.now() - timedelta(days=91),
            }
        )

    def test_sms_state_as_sent(self):
        with self.mockSMSGateway():
            self.sms1.send()
        self.assertEqual(self.sms1.state, "sent")
        self.assertEqual(self.sms2.state, "outgoing")

        with self.mockSMSGateway():
            self.sms2.send()
        self.assertEqual(self.sms2.state, "sent")

    def test_sms_unlink(self):
        # force_unlink=False by default
        self.sms1.unlink()
        self.assertTrue(self.sms1.exists())
        # force_unlink=True
        self.sms1.with_context(force_unlink=True).unlink()
        self.assertFalse(self.sms1.exists())

    def test_sms_purge(self):
        self.sms_sms._purge(120)
        self.assertEqual(len(self.sms_sms.search([])), 3)

        self.sms_sms._purge(90)
        self.assertEqual(len(self.sms_sms.search([])), 2)

        self.sms_sms._purge(60)
        self.assertEqual(len(self.sms_sms.search([])), 1)

        self.sms_sms._purge(0)
        self.assertEqual(len(self.sms_sms.search([])), 0)
