# -*- coding: utf-8 -*-
# © 2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)

from openerp.tests.common import TransactionCase


class TestSmsSendPicking(TransactionCase):

    def setUp(self):
        super(TestSmsSendPicking, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'test man',
            'mobile': '336789123',
            'email': 'testcustomer+3@test.com',
        })
        self.product = self.env.ref('product.product_product_4')
        self.picking_out = self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': (
                self.env.ref('stock.stock_location_customers').id
            ),
            'partner_id': self.partner.id
        })
        self.env['stock.move'].create({
            'name': 'a move',
            'product_id': self.product.id,
            'product_uom_qty': 3.0,
            'product_uom': self.product.uom_id.id,
            'picking_id': self.picking_out.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': (
                self.env.ref('stock.stock_location_customers').id
            )
        })
        self.picking_out.action_assign()
        self.picking_out.force_assign()

    def test_availability_flag(self):
        self.assertEqual(False, self.picking_out.availability_sent_by_sms)
        self.picking_out._cron_send_picking_availability_by_sms()
        self.assertEqual(True, self.picking_out.availability_sent_by_sms)

    def test_sms_created(self):
        dom = [('message', 'ilike',
                'Your picking %s %%' % self.picking_out.name)]
        self.assertTrue(len(self.env['sms.sms'].search(dom)) == 0)
        self.picking_out._cron_send_picking_availability_by_sms()
        self.assertTrue(len(self.env['sms.sms'].search(dom)) == 1)
