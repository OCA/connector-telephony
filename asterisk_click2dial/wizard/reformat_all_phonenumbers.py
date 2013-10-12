# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2012-2013 Alexis de Lattre <alexis@via.ecp.fr>
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

class reformat_all_phonenumbers(orm.TransientModel):
    _name = "reformat.all.phonenumbers"
    _description = "Reformat all phone numbers"

    _columns = {
        'phonenumbers_not_reformatted': fields.text("Phone numbers that couldn't be reformatted"),
        }


    def _extend_reformat_phonenumbers(self, cr, uid, context=None):
        '''This function is designed to be inherited
        to extend the functionnality to objects other than res.partner'''
        res = {
            self.pool['res.partner']: {
                'allids': self.pool['res.partner'].search(cr, uid, ['|', ('active', '=', True), ('active', '=', False)], context=context),
                'phonefields': ['phone', 'fax', 'mobile'],
                'namefield': 'name',
                }
        }
        return res

    def run_reformat_all_phonenumbers(self, cr, uid, ids, context=None):
        _logger.info('Starting to reformat all the phone numbers')
        phonenumbers_not_reformatted = ''
        toreformat_dict = self._extend_reformat_phonenumbers(cr, uid, context=context)
        for obj, prop in toreformat_dict.items():
            for entry in obj.read(cr, uid, prop['allids'], [prop['namefield']] + prop['phonefields'], context=context):
                init_entry = entry.copy()
                # entry is _updated_ by the fonction _generic_reformat_phonenumbers()
                try:
                    obj._generic_reformat_phonenumbers(cr, uid, entry, context=context)
                except Exception, e:
                    #raise orm.except_orm(_('Error :'), _("Problem on entry '%s'. Error message: %s" % (init_entry.get(prop['namefield']), e[1])))
                    phonenumbers_not_reformatted += "Problem on %s '%s'. Error message: %s" % (obj._description, init_entry.get(prop['namefield']), e[1]) + "\n"
                    _logger.warning("Problem on %s '%s'. Error message: %s" % (obj._description, init_entry.get(prop['namefield']), e[1]))
                    continue
                if any([init_entry.get(field) != entry.get(field) for field in prop['phonefields']]):
                    entry.pop('id')
                    entry.pop(prop['namefield'])
                    _logger.info('[%s] Reformating phone number: FROM %s TO %s' % (obj._description, unicode(init_entry), unicode(entry)))
                    obj.write(cr, uid, init_entry['id'], entry, context=context)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = 'All phone numbers have been reformatted successfully.'
        self.write(cr, uid, ids[0], {'phonenumbers_not_reformatted': phonenumbers_not_reformatted}, context=context)
        _logger.info('End of the phone number reformatting wizard')
        return True
