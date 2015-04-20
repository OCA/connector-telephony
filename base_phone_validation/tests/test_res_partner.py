# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C)  cgstudiomap <cgstudiomap@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


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
            for phone_field in self.res_partner_pool._phone_fields:
                partner = self.res_partner_pool.create(
                    {
                        'name': 't_name',
                        'country_id': country,
                        phone_field: number,
                    }
                )
                self.assertEqual(partner.name, 't_name')

    def test_unvalid_numbers(self):
        for number, country_code in self.__valid_numbers:
            country = self.res_country_pool.search(
                [('code', 'ilike', country_code)]
            )[0].id
            for phone_field in self.res_partner_pool._phone_fields:
                with self.assertRaises(ValidationError):
                    self.res_partner_pool.create(
                        {
                            'name': 't_name',
                            'country_id': country,
                            # Remove a number from the phonenumber.
                            # it should make is unvalid.
                            phone_field: number[:-1],
                            }
                    )


