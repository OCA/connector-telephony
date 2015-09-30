# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Recruitment phone module for Odoo/OpenERP
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

from openerp.osv import orm


class hr_applicant(orm.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant', 'phone.common']
    _phone_fields = ['partner_phone', 'partner_mobile']
    _phone_name_sequence = 50
    _country_field = None
    _partner_field = 'partner_id'

    def create(self, vals):
        vals_reformated = self._generic_reformat_phonenumbers(None, vals)
        return super(hr_applicant, self).create(vals_reformated)

    def write(self, ids, vals):
        vals_reformated = self._generic_reformat_phonenumbers(ids, vals)
        return super(hr_applicant, self).write(ids, vals_reformated)
