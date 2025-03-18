# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestEventPhone(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fr_country_id = cls.env.ref("base.fr").id
        cls.phco = cls.env["phone.common"]
        cls.env.company.write({"country_id": cls.fr_country_id})
        cls.test_record = cls.env["hr.employee"].create(
            {"name": "Alexis de Lattre", "mobile_phone": "+33 6 78 72 72 72"}
        )

    def test_lookup(self):
        res = self.phco.get_record_from_phone_number("0678727272")
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[0], "res.partner")
        self.assertEqual(res[1], self.test_record.work_contact_id.id)
        self.assertEqual(res[2], self.test_record.display_name)
