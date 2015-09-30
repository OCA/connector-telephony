# -*- encoding: utf-8 -*-
##############################################################################
#
#    CRM Claim Phone module for Odoo/OpenERP
#    Copyright (c) 2012-2014 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, tools


class crm_claim(models.Model):
    _name = 'crm.claim'
    _inherit = ['crm.claim', 'phone.common']
    _phone_fields = ['partner_phone']
    _country_field = None
    _partner_field = 'partner_id'

    def create(self, vals):
        vals_reformated = self._generic_reformat_phonenumbers(None, vals)
        return super(crm_claim, self).create(vals_reformated)

    def write(self, ids, vals):
        vals_reformated = self._generic_reformat_phonenumbers(ids, vals)
        return super(crm_claim, self).write(ids, vals_reformated)
