# -*- encoding: utf-8 -*-
##############################################################################
#
#    CRM phone module for Odoo/OpenERP
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


class crm_lead(orm.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'phone.common']
    _phone_fields = ['phone', 'mobile', 'fax']
    _phone_name_sequence = 20
    _country_field = 'country_id'
    _partner_field = None

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, None, vals, context=context)
        return super(crm_lead, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, ids, vals, context=context)
        return super(crm_lead, self).write(
            cr, uid, ids, vals_reformated, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('callerid'):
            res = []
            if isinstance(ids, (int, long)):
                ids = [ids]
            for lead in self.browse(cr, uid, ids, context=context):
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
            return super(crm_lead, self).name_get(
                cr, uid, ids, context=context)


class crm_phonecall(orm.Model):
    _name = 'crm.phonecall'
    _inherit = ['crm.phonecall', 'phone.common']
    _phone_fields = ['partner_phone', 'partner_mobile']
    _country_field = None
    _partner_field = 'partner_id'

    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, None, vals, context=context)
        return super(crm_phonecall, self).create(
            cr, uid, vals_reformated, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(
            cr, uid, ids, vals, context=context)
        return super(crm_phonecall, self).write(
            cr, uid, ids, vals_reformated, context=context)
