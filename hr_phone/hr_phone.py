# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'phone.common']
    _phone_fields = ['work_phone', 'mobile_phone']
    _phone_name_sequence = 30
    _country_field = 'country_id'
    _partner_field = None

    @api.model
    def create(self, vals):
        vals_reformated = self._reformat_phonenumbers_create(vals)
        return super(HrEmployee, self).create(vals_reformated)

    @api.multi
    def write(self, vals):
        vals_reformated = self._reformat_phonenumbers_write(vals)
        return super(HrEmployee, self).write(vals_reformated)
