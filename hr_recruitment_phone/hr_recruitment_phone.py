# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class HrApplicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant', 'phone.common']
    _phone_fields = ['partner_phone', 'partner_mobile']
    _phone_name_sequence = 50
    _country_field = None
    _partner_field = 'partner_id'

    @api.model
    def create(self, vals):
        vals_reformated = self._reformat_phonenumbers_create(vals)
        return super(HrApplicant, self).create(vals_reformated)

    @api.multi
    def write(self, vals):
        vals_reformated = self._reformat_phonenumbers_write(vals)
        return super(HrApplicant, self).write(vals_reformated)

    @api.multi
    def name_get(self):
        if self._context.get('callerid'):
            res = []
            for appl in self:
                if appl.partner_id:
                    name = u'%s (%s)' % (appl.partner_id.name, appl.name)
                elif appl.partner_name:
                    name = u'%s (%s)' % (appl.partner_name, appl.name)
                else:
                    name = appl.name
                res.append((appl.id, name))
            return res
        else:
            return super(HrApplicant, self).name_get()
