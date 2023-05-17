# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestBasePhone(TransactionCase):
    def setUp(self):
        super(TestBasePhone, self).setUp()
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

    def test_get_phone_model(self):
        res = self.phco._get_phone_models()
        self.assertIsInstance(res, list)
        rpo = self.env["res.partner"]
        self.assertTrue(any([x["object"] == rpo for x in res]))
        for entry in res:
            self.assertIsInstance(entry.get("fields"), list)

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

    def test_to_dial(self):
        phone_to_dial = self.phco.convert_to_dial_number("+33 4 78 99 88 77")
        self.assertEqual(phone_to_dial, "0478998877")
        phone_to_dial = self.phco.convert_to_dial_number("+32 455 78 99 88")
        self.assertEqual(phone_to_dial, "0032455789988")

    def create_partner(self, vals):
        rpo = self.env["res.partner"]
        partner_form = Form(rpo)
        for key, value in vals.items():
            if key == "name":
                partner_form.name = value
            elif key == "phone":
                partner_form.phone = value
            elif key == "mobile":
                partner_form.mobile = value
            elif key == "country_id":
                partner_form.country_id = value
            # elif key == "is_company":
            #     partner_form.is_company = value
            #     AssertionError: can't write on invisible field is_company
            elif key == "parent_id":
                partner_form.parent_id = value
        res = partner_form.save()
        return res

    def test_partner_phone_formatting(self):
        # Create an existing partner without country
        vals = {
            "name": "Partner 1",
            "phone": "04-72-98-76-54",
            "mobile": "06.42.12.34.56",
        }
        partner_1 = self.create_partner(vals)
        self.assertEqual(partner_1.phone, "+33 4 72 98 76 54")
        self.assertEqual(partner_1.mobile, "+33 6 42 12 34 56")
        # Create a partner with country
        vals = {
            "name": "Parent Partner 2",
            "country_id": self.env.ref("base.ch"),
        }
        parent_partner2 = self.create_partner(vals)
        parent_partner2.is_company = True
        vals = {
            "name": "Partner 2",
            "parent_id": parent_partner2,
            "phone": "(0) 21 123 45 67",
            "mobile": "(0) 79 987 65 43",
        }
        partner2 = self.create_partner(vals)
        self.assertEqual(partner2.country_id, self.env.ref("base.ch"))
        self.assertEqual(partner2.phone, "+41 21 123 45 67")
        self.assertEqual(partner2.mobile, "+41 79 987 65 43")
        # Write on an existing partner
        vals = {
            "name": "Partner 3",
            "country_id": self.env.ref("base.be"),
        }
        partner3 = self.create_partner(vals)
        partner3.is_company = True
        partner3_form = Form(partner3)
        partner3_form.phone = "(0) 2 312 34 56"
        self.assertEqual(partner3_form.phone, "+32 2 312 34 56")
        partner3_form.mobile = "04 72 98 76 54"
        # Changing country_id should change phone prefix and format
        partner3_form.country_id = self.env.ref("base.fr")
        # The number is valid in Belgium but becomes invalid in France
        # so it is kept at national format
        self.assertEqual(partner3_form.phone, "02 312 34 56")
        self.assertEqual(partner3_form.mobile, "+33 4 72 98 76 54")
        # Change back to Belgium country
        partner3_form.country_id = self.env.ref("base.be")
        self.assertEqual(partner3_form.phone, "+32 2 312 34 56")
        # Test get_name_from_phone_number
        pco = self.env["phone.common"]
        name = pco.get_name_from_phone_number("0642123456")
        self.assertEqual(name, "Partner 1")
        name2 = pco.get_name_from_phone_number("0041211234567")
        self.assertEqual(name2, "Parent Partner 2, Partner 2")
