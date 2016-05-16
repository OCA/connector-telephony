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

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, None, vals, context=context)
        return super(hr_applicant, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, ids, vals, context=context)
        return super(hr_applicant, self).write(
            cr, uid, ids, vals_reformated, context=context)

    # The only reason this is overloaded her as applicant.name is the
    # position. This is what base_phone.py:name_get will return.
    # It makes more sense in this context to return the applicant's name.
    # This code appears weird as it returns [] in the cases:
    # 1) hired - done or 2) refused - cancel.
    # This is done so that an employees record is used instead of the
    # applicant record. The following (cancel) applies here as well.
    # It is done for cancel so that an applicant who is refused doesn't
    # cause problems if that number is reassigned to another entity in the
    # future or the same person applies for the same or different position
    # in the future. We cannot call super name_get in these cases as it will
    # still return the position the person applied for and the pop-up
    # functionality would then pull up this record. Both of these are
    # undesirable.
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('callerid'):
            res = []
            if isinstance(ids, (int, long)):
                ids = [ids]
            for applicant in self.browse(cr, uid, ids, context=context):
                name = applicant.partner_name
                if applicant.state not in ['done', 'cancel']:
                    res.append((applicant.id, name))
            return res
        else:
            return super(hr_applicant, self).name_get(
                cr, uid, ids, context=context)
