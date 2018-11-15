# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonecall_ids = fields.One2many(
        'crm.phonecall', 'partner_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_compute_phonecall_count', string='Number of Phonecalls',
        readonly=True)

    @api.depends('phonecall_ids')
    def _compute_phonecall_count(self):
        rg_res = self.env['crm.phonecall'].read_group(
            [('partner_id', 'in', self.ids)],
            ['partner_id'], ['partner_id'])
        for rg_re in rg_res:
            partner = self.browse(rg_re['partner_id'][0])
            partner.phonecall_count = rg_re['partner_id_count']
