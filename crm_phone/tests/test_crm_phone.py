# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
            'country_id': self.env.ref('base.fr').id,
            })
        lead1._onchange_mobile_validation()
        self.assertEquals(lead1.mobile, u'+33 6 42 77 42 77')
        lead2 = clo.create({
            'name': u'Automobile Odoo deployment',
            'partner_name': u'Kia',
            'contact_name': u'Mikaël Content',
            'country_id': self.env.ref('base.ch').id,
            'phone': '04 31 23 45 67',
            })
        lead2._onchange_phone_validation()
        self.assertEquals(lead2.phone, u'+41 43 123 45 67')
        lead3 = clo.create({
            'name': 'Angela Strasse',
            'country_id': self.env.ref('base.de').id,
            'phone': '08912345678',
            })
        lead3._onchange_phone_validation()
        self.assertEquals(lead3.phone, u'+49 89 12345678')
        partner4 = self.env['res.partner'].create({
            'name': 'Belgian Guy',
            'country_id': self.env.ref('base.be').id,
            })
        lead4 = clo.create({
            'name': 'Large Odoo deployment',
            'partner_id': partner4.id,
            'mobile': '(0) 2-391-43-75',
            })
        lead4._onchange_mobile_validation()
        self.assertEquals(lead4.mobile, u'+32 2 391 43 75')
        pco = self.env['phone.common']
        name = pco.get_name_from_phone_number('0642774277')
        self.assertEquals(name, 'Jacques Toufaux (Ford)')
        name2 = pco.get_name_from_phone_number('0041431234567')
        self.assertEquals(name2, u'Mikaël Content (Kia)')
