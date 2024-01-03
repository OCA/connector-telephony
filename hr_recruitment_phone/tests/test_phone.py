# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestRecruitmentPhone(TransactionCase):
    def setUp(self):
        super().setUp()
        self.fr_country_id = self.env.ref("base.fr").id
        self.phco = self.env["phone.common"]
        self.env.company.write({"country_id": self.fr_country_id})
        self.partner = self.env["res.partner"].create(
            {
                "name": "Partner 0",
                "country_id": self.fr_country_id,
                "phone": "+33 4 78 32 32 32",
            }
        )

    def test_lookup(self):
        res = self.phco.get_record_from_phone_number("0478323232")
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[0], "res.partner")
        self.assertEqual(res[1], self.partner.id)
        self.assertEqual(
            res[2], self.partner.with_context(callerid=True).name_get()[0][1]
        )
        res = self.phco.get_record_from_phone_number("0499889988")
        self.assertFalse(res)
