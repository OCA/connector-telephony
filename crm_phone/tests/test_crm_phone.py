# Copyright 2016-2019 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCRMPhone(TransactionCase):

    def test_phone(self):
        company = self.env.ref('base.main_company')
        fr_country_id = self.env.ref('base.fr').id
        company.country_id = fr_country_id
        rpo = self.env['res.partner']
        # Create an existing partner without country
        partner1 = rpo.create({
            'name': 'Pierre Paillet',
            'phone': '04-72-08-87-32',
            'mobile': '06.42.77.42.66',
            })
        partner1._onchange_phone_validation()
        partner1._onchange_mobile_validation()
        self.assertEquals(partner1.phone, '+33 4 72 08 87 32')
        self.assertEquals(partner1.mobile, '+33 6 42 77 42 66')
        # Create a partner with country
        parent_partner2 = rpo.create({
            'name': 'C2C',
            'country_id': self.env.ref('base.ch').id,
            })
        partner2 = rpo.create({
            'name': 'Joël Grand-Guillaume',
            'parent_id': parent_partner2.id,
            'phone': '(0) 21 619 10 10',
            'mobile': '(0) 79 606 42 42',
            })
        partner2._onchange_phone_validation()
        partner2._onchange_mobile_validation()
        self.assertEquals(partner2.country_id, self.env.ref('base.ch'))
        self.assertEquals(partner2.phone, '+41 21 619 10 10')
        self.assertEquals(partner2.mobile, '+41 79 606 42 42')
        # Write on an existing partner
        partner3 = rpo.create({
            'name': 'Belgian corp',
            'country_id': self.env.ref('base.be').id,
            })
        partner3.write({'phone': '(0) 2 391 43 74'})
        partner3._onchange_phone_validation()
        self.assertEquals(partner3.phone, '+32 2 391 43 74')
        # Write on an existing partner with country at the same time
        partner3.write({
            'phone': '04 72 89 32 43',
            'country_id': fr_country_id,
            })
        partner3._onchange_phone_validation()
        self.assertEquals(partner3.phone, '+33 4 72 89 32 43')
        # Test get_name_from_phone_number
        pco = self.env['phone.common']
        name = pco.get_name_from_phone_number('0642774266')
        self.assertEquals(name, 'Pierre Paillet')
        name2 = pco.get_name_from_phone_number('0041216191010')
        self.assertEquals(name2, 'C2C, Joël Grand-Guillaume')
        # Test against the POS bug
        # https://github.com/OCA/connector-telephony/issues/113
        # When we edit/create a partner from the POS,
        # the country_id key in create(vals) is given as a string !
        partnerpos = rpo.create({
            'name': 'POS customer',
            'phone': '04-72-08-87-42',
            'country_id': str(fr_country_id),
            })
        partnerpos._onchange_phone_validation()
        self.assertEquals(partnerpos.phone, '+33 4 72 08 87 42')
        self.assertEquals(partnerpos.country_id.id, fr_country_id)

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
        self.assertEquals(lead1.mobile, '+33 6 42 77 42 77')
        lead2 = clo.create({
            'name': 'Automobile Odoo deployment',
            'partner_name': 'Kia',
            'contact_name': 'Mikaël Content',
            'country_id': self.env.ref('base.ch').id,
            'phone': '04 31 23 45 67',
            })
        lead2._onchange_phone_validation()
        self.assertEquals(lead2.phone, '+41 43 123 45 67')
        lead3 = clo.create({
            'name': 'Angela Strasse',
            'country_id': self.env.ref('base.de').id,
            'phone': '08912345678',
            })
        lead3._onchange_phone_validation()
        self.assertEquals(lead3.phone, '+49 89 12345678')
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
        self.assertEquals(lead4.mobile, '+32 2 391 43 75')
        pco = self.env['phone.common']
        name = pco.get_name_from_phone_number('0642774277')
        self.assertEquals(name, 'Jacques Toufaux (Ford)')
        name2 = pco.get_name_from_phone_number('0041431234567')
        self.assertEquals(name2, u'Mikaël Content (Kia)')
