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
        self.test_record = self.env["hr.employee"].create(
            {"name": "Alexis de Lattre", "mobile_phone": "+33 6 78 72 72 72"}
        )

    def test_lookup(self):
        res = self.phco.get_record_from_phone_number("0678727272")
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[0], "hr.employee")
        self.assertEqual(res[1], self.test_record.id)
        self.assertEqual(
            res[2], self.test_record.with_context(callerid=True).name_get()[0][1]
        )
