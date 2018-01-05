# -*- coding: utf-8 -*-
# © 2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)

from openerp.tests.common import TransactionCase


class TestPhone(TransactionCase):

    def test_phone(self):
        company = self.env.ref('base.main_company')
        fr_country_id = self.env.ref('base.fr').id
        company.country_id = fr_country_id
        rpo = self.env['res.partner']
        # Create an existing partner without country
        partner1 = rpo.create({
            'name': u'Pierre Paillet',
            'phone': '04-72-08-87-32',
            'mobile':  '06.42.77.42.66',
            'fax': '(0) 1 45 42 12 42',
            })
        self.assertEquals(partner1.phone, u'+33 4 72 08 87 32')
        self.assertEquals(partner1.mobile, u'+33 6 42 77 42 66')
        self.assertEquals(partner1.fax, u'+33 1 45 42 12 42')
        # Create a partner with country
        self.env.ref('base.res_partner_12').country_id =\
            self.env.ref('base.ch').id
        partner2 = rpo.create({
            'name': u'Joël Grand-Guillaume',
            'parent_id': self.env.ref('base.res_partner_12').id,
            'phone': '(0) 21 619 10 10',
            'mobile': '(0) 79 606 42 42',
            })
        self.assertEquals(partner2.country_id, self.env.ref('base.ch'))
        self.assertEquals(partner2.phone, u'+41 21 619 10 10')
        self.assertEquals(partner2.mobile, u'+41 79 606 42 42')
        # Write on an existing partner
        agrolait = self.env.ref('base.res_partner_2')
        self.assertEquals(agrolait.country_id, self.env.ref('base.be'))
        agrolait.write({'phone': '(0) 2 391 43 74'})
        self.assertEquals(agrolait.phone, u'+32 2 391 43 74')
        # Write on an existing partner with country at the same time
        agrolait.write({
            'fax': '04 72 89 32 43',
            'country_id': fr_country_id,
            })
        self.assertEquals(agrolait.fax, u'+33 4 72 89 32 43')
        # Write an invalid phone number
        partner2.fax = '42'
        self.assertEquals(partner2.fax, u'42')
        # Test get_name_from_phone_number
        pco = self.env['phone.common']
        name = pco.get_name_from_phone_number('0642774266')
        self.assertEquals(name, 'Pierre Paillet')
        name2 = pco.get_name_from_phone_number('0041216191010')
        self.assertEquals(name2, u'Joël Grand-Guillaume (Camptocamp)')
        # Test against the POS bug
        # https://github.com/OCA/connector-telephony/issues/113
        # When we edit/create a partner from the POS,
        # the country_id key in create(vals) is given as a string !
        partnerpos = rpo.create({
            'name': u'POS customer',
            'phone': '04-72-08-87-42',
            'country_id': str(fr_country_id),
            })
        self.assertEquals(partnerpos.phone, u'+33 4 72 08 87 42')
        self.assertEquals(partnerpos.country_id.id, fr_country_id)
