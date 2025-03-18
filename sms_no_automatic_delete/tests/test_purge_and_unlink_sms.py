# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.addons.sms.tests.common import MockSMS


class TestSmsPurgeAndUnlink(MockSMS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sms_sms = cls.env["sms.sms"]
        cls.sms1 = cls.sms_sms.create(
            {
                "state": "outgoing",
                "write_date": datetime.now() - timedelta(days=30),
            }
        )
        cls.sms2 = cls.sms_sms.create(
            {
                "state": "outgoing",
                "write_date": datetime.now() - timedelta(days=61),
            }
        )
        cls.sms3 = cls.sms_sms.create(
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

    def test_gc_device(self):
        # Write SQL in order not to update write_date
        with self.env.cr.savepoint():
            self.env.cr.execute(
                """
                UPDATE sms_sms
                SET to_delete = TRUE
                WHERE id IN (%s, %s, %s)
                """,
                (self.sms1.id, self.sms2.id, self.sms3.id),
            )

        self.env["ir.config_parameter"].sudo().set_param(
            "sms_no_automatic_delete.sms_purge_days", 90
        )

        self.sms_sms._gc_device()

        self.assertTrue(self.sms1.exists(), "This SMS should not be deleted")
        self.assertTrue(self.sms2.exists(), "This SMS should not be deleted")
        self.assertFalse(self.sms3.exists(), "Old SMS should have been deleted")

        self.env["ir.config_parameter"].sudo().set_param(
            "sms_no_automatic_delete.sms_purge_days", 60
        )

        self.sms_sms._gc_device()

        self.assertTrue(self.sms1.exists(), "This SMS should not be deleted")
        self.assertFalse(self.sms2.exists(), "Old SMS should have been deleted")
