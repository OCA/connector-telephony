# -*- coding: utf-8 -*-
# © 2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCRMPhone(TransactionCase):

    def test_crm_phone(self):
        clo = self.env['crm.lead']
        lead1 = clo.create({
            'name': 'The super deal of the year !',
            'partner_name': 'Ford',
            'contact_name': 'Jacques Toufaux',
            'mobile': '06.42.77.42.77',
            'fax': '(0) 1 45 44 42 43',
            'country_id': self.env.ref('base.fr').id,
            })
        self.assertEquals(lead1.mobile, u'+33 6 42 77 42 77')
        self.assertEquals(lead1.fax, u'+33 1 45 44 42 43')
        lead2 = clo.create({
            'name': u'Automobile Odoo deployment',
            'partner_name': u'Kia',
            'contact_name': u'Mikaël Content',
            'country_id': self.env.ref('base.ch').id,
            'phone': '04 31 23 45 67',
            })
        self.assertEquals(lead2.phone, u'+41 43 123 45 67')
        lead3 = clo.create({
            'name': 'Angela Strasse',
            'country_id': self.env.ref('base.de').id,
            })
        lead3.write({'phone': '08912345678'})
        self.assertEquals(lead3.phone, u'+49 89 12345678')
        lead4 = clo.create({
            'name': 'Large Odoo deployment',
            'partner_id': self.env.ref('base.res_partner_2').id,
            })
        lead4.write({'mobile': '(0) 2-391-43-75'})
        self.assertEquals(lead4.mobile, u'+32 2 391 43 75')
        pco = self.env['phone.common']
        name = pco.get_name_from_phone_number('0642774277')
        self.assertEquals(name, 'Jacques Toufaux (Ford)')
        name2 = pco.get_name_from_phone_number('0041431234567')
        self.assertEquals(name2, u'Mikaël Content (Kia)')
