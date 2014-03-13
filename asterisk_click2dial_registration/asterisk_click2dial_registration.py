# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial Registration module for OpenERP
#    Copyright (C) 2013 Invitu <contact@invitu.com>
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


class event_registration(orm.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'phone.common']

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, vals, context=context)
        return super(event_registration, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, vals, context=context)
        return super(event_registration, self).write(
            cr, uid, ids, vals_reformated, context=context)
