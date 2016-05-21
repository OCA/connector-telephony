# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'phone.common']
    _phone_fields = ['phone']
    _phone_name_sequence = 100
    _country_field = None
    _partner_field = 'partner_id'

    @api.model
    def create(self, vals):
        vals_reformated = self._reformat_phonenumbers_create(vals)
        return super(EventRegistration, self).create(vals_reformated)

    @api.multi
    def write(self, vals):
        vals_reformated = self._reformat_phonenumbers_write(vals)
        return super(EventRegistration, self).write(vals_reformated)
