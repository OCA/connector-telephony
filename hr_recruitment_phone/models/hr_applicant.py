# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.addons.base_phone.fields import Phone


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _phone_name_sequence = 50

    partner_phone = Phone(partner_field='partner_id')
    partner_mobile = Phone(partner_field='partner_id')

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
