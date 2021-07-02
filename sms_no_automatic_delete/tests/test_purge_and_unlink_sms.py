# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestSmsPurge(TransactionCase):
    def setUp(self):
        super(TestSmsPurge, self).setUp()
        self.sms_sms = self.env["sms.sms"]
        self.sms1 = self.sms_sms.create(
            {
                "state": "sent",
                "write_date": datetime.now() - timedelta(days=30),
            }
        )
        self.sms2 = self.sms_sms.create(
            {
                "state": "sent",
                "write_date": datetime.now() - timedelta(days=61),
            }
        )
        self.sms3 = self.sms_sms.create(
            {
                "state": "sent",
                "write_date": datetime.now() - timedelta(days=91),
            }
        )

    def test_sms_purge(self):
        self.sms_sms._purge(120)
        self.assertEqual(len(self.sms_sms.search([])), 3)

        self.sms_sms._purge(90)
        self.assertEqual(len(self.sms_sms.search([])), 2)

        self.sms_sms._purge(60)
        self.assertEqual(len(self.sms_sms.search([])), 1)

        self.sms_sms._purge(0)
        self.assertEqual(len(self.sms_sms.search([])), 0)
