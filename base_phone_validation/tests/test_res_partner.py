# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux , Jordi Riera <kender.jr@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    __valid_numbers = [
        ('05 69 70 57 80', 'FR'),
        ('514 789 3254', 'CA'),
        ('81 81 37 00', 'BE'),
    ]

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.res_partner_pool = self.env['res.partner']
        self.res_country_pool = self.env['res.country']

    def test_valid_numbers(self):
        for number, country_code in self.__valid_numbers:
            country = self.res_country_pool.search(
                [('code', 'ilike', country_code)]
            )[0].id
            partner = self.res_partner_pool.create(
                {
                    'name': 't_name',
                    'country_id': country,
                    'phone': number,
                }
            )
            self.assertEqual(partner.name, 't_name')

    def test_unvalid_numbers(self):
        for number, country_code in self.__valid_numbers:
            country = self.res_country_pool.search(
                [('code', 'ilike', country_code)]
            )[0].id
            with self.assertRaises(ValidationError):
                self.res_partner_pool.create(
                    {
                        'name': 't_name',
                        'country_id': country,
                        # Remove a number from the phonenumber.
                        # it should make is unvalid.
                        'phone': number[:-1],
                    }
                )

    def test_undefined_numbers(self):
        """Nothing special should happen if no phonenumber is set."""
        partner = self.res_partner_pool.create({'name': 't_name'})
        self.assertEqual(partner.name, 't_name')
