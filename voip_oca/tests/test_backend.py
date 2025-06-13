# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestVoipOca(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pbx = cls.env["voip.pbx"].create(
            {
                "name": "Test PBX",
                "mode": "prod",
                "domain": "odoo-community.com",
                "ws_server": "wss://odoo-community.com",
            }
        )
        cls.partner_01 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 01",
                "phone": "1234567890",
            }
        )
        cls.partner_02 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 01",
                "mobile": "0987654321",
            }
        )
        cls.activity_type = cls.env["mail.activity.type"].create(
            {
                "name": "Call",
                "category": "phonecall",
            }
        )
        cls.activity_01 = cls.env["mail.activity"].create(
            {
                "summary": "Activity 01",
                "activity_type_id": cls.activity_type.id,
                "res_id": cls.partner_01.id,
                "res_model_id": cls.env.ref("base.model_res_partner").id,
                "date_deadline": "2020-01-01",
                "user_id": cls.env.uid,
            }
        )
        cls.activity_02 = cls.env["mail.activity"].create(
            {
                "summary": "Activity 02",
                "activity_type_id": cls.activity_type.id,
                "res_id": cls.partner_02.id,
                "res_model_id": cls.env.ref("base.model_res_partner").id,
                "date_deadline": "2020-01-01",
                "user_id": cls.env.uid,
            }
        )
        cls.call_01 = cls.env["voip.call"].create(
            {
                "phone_number": "Call 01",
                "partner_id": cls.partner_01.id,
                "type_call": "incoming",
                "state": "ongoing",
                "pbx_id": cls.pbx.id,
                "start_date": "2020-01-01 00:00:00",
            }
        )
        cls.call_02 = cls.env["voip.call"].create(
            {
                "phone_number": "Call 02",
                "type_call": "outgoing",
                "state": "terminated",
                "pbx_id": cls.pbx.id,
                "start_date": "2020-01-01 00:00:00",
                "end_date": "2020-01-01 00:01:20",
            }
        )

    def test_partner_search(self):
        results = self.env["res.partner"].voip_get_contacts("1234567890", 0, 1000)
        self.assertIn(self.partner_01.id, [result["id"] for result in results])
        self.assertNotIn(self.partner_02.id, [result["id"] for result in results])
        results = self.env["res.partner"].voip_get_contacts("0987654321", 0, 1000)
        self.assertNotIn(self.partner_01.id, [result["id"] for result in results])
        self.assertIn(self.partner_02.id, [result["id"] for result in results])

    def test_activity_partner(self):
        self.assertEqual(self.activity_01.main_partner_id, self.partner_01)
        self.assertEqual(self.activity_01.main_partner, self.partner_01.name)
        self.assertEqual(self.activity_02.main_partner_id, self.partner_02)
        self.assertEqual(self.activity_02.main_partner, self.partner_02.name)

    def test_activity_search(self):
        results = self.env["mail.activity"].get_call_activities("Activity 01", 0, 1000)
        self.assertIn(self.activity_01.id, [result["id"] for result in results])
        self.assertNotIn(self.activity_02.id, [result["id"] for result in results])
        results = self.env["mail.activity"].get_call_activities("Activity 02", 0, 1000)
        self.assertNotIn(self.activity_01.id, [result["id"] for result in results])
        self.assertIn(self.activity_02.id, [result["id"] for result in results])

    def test_call_search(self):
        results = self.env["voip.call"].get_recent_calls("Call 01", 0, 1000)
        self.assertIn(self.call_01.id, [result["id"] for result in results])
        self.assertNotIn(self.call_02.id, [result["id"] for result in results])
        results = self.env["voip.call"].get_recent_calls("Call 02", 0, 1000)
        self.assertNotIn(self.call_01.id, [result["id"] for result in results])
        self.assertIn(self.call_02.id, [result["id"] for result in results])

    def test_call_process_ok(self):
        call_data = self.env["voip.call"].create_call(
            {
                "phone_number": "1234567890",
                "type_call": "incoming",
                "pbx_id": self.pbx.id,
            }
        )
        call = self.env["voip.call"].browse(call_data["id"])
        self.assertEqual(call.partner_id, self.partner_01)
        self.assertEqual(call.state, "calling")
        self.assertFalse(call.start_date)
        self.assertFalse(call.end_date)
        call.accept_call()
        self.assertEqual(call.state, "ongoing")
        self.assertTrue(call.start_date)
        self.assertFalse(call.end_date)
        call.terminate_call()
        self.assertEqual(call.state, "terminated")
        self.assertTrue(call.end_date)

    def test_call_process_rejected(self):
        call_data = self.env["voip.call"].create_call(
            {
                "phone_number": "1234567890",
                "type_call": "incoming",
                "pbx_id": self.pbx.id,
            }
        )
        call = self.env["voip.call"].browse(call_data["id"])
        self.assertEqual(call.partner_id, self.partner_01)
        self.assertEqual(call.state, "calling")
        self.assertFalse(call.start_date)
        self.assertFalse(call.end_date)
        call.reject_call()
        self.assertEqual(call.state, "rejected")
        self.assertTrue(call.end_date)
        self.assertFalse(call.start_date)
