# Copyright 2016-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCrmPhone(TransactionCase):
    def setUp(self):
        super(TestCrmPhone, self).setUp()
        self.fr_country_id = self.env.ref("base.fr").id
        self.phco = self.env["phone.common"]
        self.env.company.write({"country_id": self.fr_country_id})
        self.lead_akretion = self.env["crm.lead"].create(
            {
                "name": "Deployment at Akretion France",
                "partner_name": "Akretion France",
                "country_id": self.fr_country_id,
                "phone": "+33 4 78 42 42 42",
            }
        )

    def test_lookup(self):
        res = self.phco.get_record_from_phone_number("0478424242")
        self.assertIsInstance(res, tuple)
        self.assertEqual(res[0], "crm.lead")
        self.assertEqual(res[1], self.lead_akretion.id)
        self.assertEqual(
            res[2], self.lead_akretion.with_context(callerid=True).name_get()[0][1]
        )

    def test_crm_phone_formatting(self):
        clo = self.env["crm.lead"]
        lead1 = clo.create(
            {
                "name": "The super deal of the year !",
                "partner_name": "Ford",
                "contact_name": "Jacques Toufaux",
                "mobile": "06.42.77.42.77",
                "country_id": self.fr_country_id,
            }
        )
        lead1._onchange_mobile_validation()
        self.assertEqual(lead1.mobile, "+33 6 42 77 42 77")
        lead2 = clo.create(
            {
                "name": "Automobile Odoo deployment",
                "partner_name": "Kia",
                "contact_name": "Mikaël Content",
                "country_id": self.env.ref("base.ch").id,
                "phone": "04 31 23 45 67",
            }
        )
        lead2._onchange_phone_validation()
        self.assertEqual(lead2.phone, "+41 43 123 45 67")
        lead3 = clo.create(
            {
                "name": "Angela Strasse",
                "country_id": self.env.ref("base.de").id,
                "phone": "08912345678",
            }
        )
        lead3._onchange_phone_validation()
        self.assertEqual(lead3.phone, "+49 89 12345678")
        partner4 = self.env["res.partner"].create(
            {
                "name": "Belgian Guy",
                "country_id": self.env.ref("base.be").id,
            }
        )
        lead4 = clo.create(
            {
                "name": "Large Odoo deployment",
                "partner_id": partner4.id,
                "mobile": "(0) 2-391-43-75",
            }
        )
        lead4._onchange_mobile_validation()
        self.assertEqual(lead4.mobile, "+32 2 391 43 75")
        pco = self.env["phone.common"]
        name = pco.get_name_from_phone_number("0642774277")
        self.assertEqual(name, "Jacques Toufaux (Ford)")
        name2 = pco.get_name_from_phone_number("0041431234567")
        self.assertEqual(name2, "Mikaël Content (Kia)")
