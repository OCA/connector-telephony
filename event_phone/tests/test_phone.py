# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestEventPhone(TransactionCase):
    def setUp(self):
        super().setUp()
        self.fr_country_id = self.env.ref("base.fr").id
        self.phco = self.env["phone.common"]
        self.env.company.write({"country_id": self.fr_country_id})
        event = self.env["event.event"].create(
            {
                "name": "OCA days",
                "date_begin": "2021-05-15",
                "date_end": "2021-05-16",
            }
        )
        self.test_record = self.env["event.registration"].create(
            {
                "event_id": event.id,
                "name": "Alexis de Lattre",
                "mobile": "+33 6 78 62 62 62",
            }
        )

    def test_lookup(self):
        res = self.phco.get_record_from_phone_number("0678626262")
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[0], "event.registration")
        self.assertEqual(res[1], self.test_record.id)
        self.assertEqual(
            res[2], self.test_record.with_context(callerid=True).name_get()[0][1]
        )
