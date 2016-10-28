# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonecall_ids = fields.One2many(
        'crm.phonecall', 'partner_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_count_phonecalls', string='Number of Phonecalls',
        readonly=True)

    @api.multi
    @api.depends('phonecall_ids')
    def _count_phonecalls(self):
        cpo = self.env['crm.phonecall']
        for partner in self:
            try:
                partner.phonecall_count = cpo.search_count(
                    [('partner_id', 'child_of', partner.id)])
            except:
                partner.phonecall_count = 0
