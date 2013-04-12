# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2012 Alexis de Lattre <alexis@via.ecp.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import osv, fields
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class reformat_all_phonenumbers(osv.osv_memory):
    _name = "reformat.all.phonenumbers"
    _description = "Reformat all phone numbers"

    _columns = {
        'phonenumbers_not_reformatted': fields.text("Phone numbers that couldn't be reformatted"),
        }


    def run_reformat_all_phonenumbers(self, cr, uid, ids, context=None):
        partner_obj = self.pool['res.partner']
        phonefields = ['phone', 'fax', 'mobile']
        _logger.info('Starting to reformat all the phone numbers')
        all_partner_ids = partner_obj.search(cr, uid, ['|', ('active', '=', True), ('active', '=', False)], context=context)
        phonenumbers_not_reformatted = ''
        for partner in partner_obj.read(cr, uid, all_partner_ids, ['name'] + phonefields, context=context):
            init_partner = partner.copy()
            # partner is _updated_ by the fonction _reformat_phonenumbers()
            try:
                partner_obj._reformat_phonenumbers(cr, uid, partner, context=context)
            except Exception, e:
                #raise osv.except_osv(_('Error :'), _("Problem on partner '%s'. Error message: %s" % (init_partner.get('name'), e[1])))
                phonenumbers_not_reformatted += "Problem on partner '%s'. Error message: %s" % (init_partner.get('name'), e[1]) + "\n"
                _logger.warning("Problem on partner '%s'. Error message: %s" % (init_partner.get('name'), e[1]))
                continue
            # Test if the phone numbers have been changed
            if any([init_partner.get(field) != partner.get(field) for field in phonefields]):
                partner.pop('id')
                partner.pop('name')
                _logger.info('Reformating phone number: FROM %s TO %s' % (unicode(init_partner), unicode(partner)))
                partner_obj.write(cr, uid, init_partner['id'], partner, context=context)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = 'All phone numbers have been reformatted successfully.'
        self.write(cr, uid, ids[0], {'phonenumbers_not_reformatted': phonenumbers_not_reformatted}, context=context)
        _logger.info('End of the phone number reformatting wizard')
        return True
