# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons.base_phone.fields import Phone, Fax


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _phone_name_sequence = 20

    phone = Phone(country_field='country_id', partner_field='partner_id')
    mobile = Phone(country_field='country_id', partner_field='partner_id')
    fax = Fax(country_field='country_id', partner_field='partner_id')
    phonecall_ids = fields.One2many(
        'crm.phonecall', 'opportunity_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_count_phonecalls', string='Number of Phonecalls',
        readonly=True)

    @api.multi
    def name_get(self):
        if self._context.get('callerid'):
            res = []
            for lead in self:
                if lead.partner_name and lead.contact_name:
                    name = '%s (%s)' % (lead.contact_name, lead.partner_name)
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

    @api.multi
    @api.depends('phonecall_ids')
    def _count_phonecalls(self):
        cpo = self.env['crm.phonecall']
        for lead in self:
            try:
                lead.phonecall_count = cpo.search_count(
                    [('opportunity_id', '=', lead.id)])
            except:
                lead.phonecall_count = 0
