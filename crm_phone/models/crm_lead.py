# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _phone_name_sequence = 20
    _phone_name_fields = ['phone', 'mobile']

    phonecall_ids = fields.One2many(
        'crm.phonecall', 'opportunity_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_compute_phonecall_count', string='Number of Phonecalls',
        readonly=True)
    partner_address_mobile = fields.Char(
        string='Partner Contact Mobile', related='partner_id.mobile',
        readonly=True)

    def name_get(self):
        if self._context.get('callerid'):
            res = []
            for lead in self:
                if lead.partner_name and lead.contact_name:
                    name = u'%s (%s)' % (lead.contact_name, lead.partner_name)
                elif lead.partner_name:
                    name = lead.partner_name
                elif lead.contact_name:
                    name = lead.contact_name
                else:
                    name = lead.name
                res.append((lead.id, name))
            return res
        else:
            return super(CrmLead, self).name_get()

    @api.depends('phonecall_ids')
    def _compute_phonecall_count(self):
        rg_res = self.env['crm.phonecall'].read_group(
            [('opportunity_id', 'in', self.ids)],
            ['opportunity_id'], ['opportunity_id'])
        for rg_re in rg_res:
            lead = self.browse(rg_re['opportunity_id'][0])
            lead.phonecall_count = rg_re['opportunity_id_count']
