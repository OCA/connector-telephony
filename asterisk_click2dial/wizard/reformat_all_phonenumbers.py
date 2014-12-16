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

from osv import osv, fields
import netsvc

logger = netsvc.Logger()


class reformat_all_phonenumbers(osv.osv_memory):
    _name = "reformat.all.phonenumbers"
    _description = "Reformat all phone numbers"
    _columns = {
        'phonenumbers_not_reformatted': fields.text(
            "Phone numbers that couldn't be reformatted"
        ),
    }

    def run_reformat_all_phonenumbers(self, cr, uid, ids, context=None):
        print "RUN ids=", ids
        addr_obj = self.pool.get('res.partner.address')
        phonefields = ['phone', 'fax', 'mobile']
        logger.notifyChannel(
            'click2dial',
            netsvc.LOG_INFO,
            'Starting to reformat all the phone numbers'
        )
        all_addr_ids = addr_obj.search(
            cr, uid, [
                '|',
                ('active', '=', True),
                ('active', '=', False)
            ], context=context
        )
        phonenumbers_not_reformatted = ''
        for addr in addr_obj.read(
                cr, uid, all_addr_ids, ['name'] + phonefields, context=context
        ):
            init_addr = addr.copy()
            # addr is _updated_ by the fonction _reformat_phonenumbers()
            try:
                addr_obj._reformat_phonenumbers(cr, uid, addr, context=context)
            except Exception, e:
                phonenumbers_not_reformatted += (
                    "Problem on partner contact '%s'. "
                    "Error message: %s" % (init_addr.get('name'), e[1]) + "\n"
                )
                logger.notifyChannel(
                    'click2dial',
                    netsvc.LOG_WARNING,
                    "Problem on partner contact '%s'. Error message: %s"
                    % (init_addr.get('name'), e[1])
                )
                continue
            # Test if the phone numbers have been changed
            if any([init_addr.get(field) != addr.get(field)
                    for field in phonefields]):
                addr.pop('id')
                addr.pop('name')
                logger.notifyChannel(
                    'click2dial',
                    netsvc.LOG_INFO,
                    'Reformating phone number: FROM %s TO %s'
                    % (unicode(init_addr), unicode(addr))
                )
                addr_obj.write(cr, uid, init_addr['id'], addr, context=context)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = (
                'All phone numbers have been reformatted successfully.'
            )
        self.write(cr, uid, ids, {
            'phonenumbers_not_reformatted': phonenumbers_not_reformatted
        }, context=context)
        logger.notifyChannel(
            'click2dial',
            netsvc.LOG_INFO,
            'End of the phone number reformatting wizard'
        )
        return True

reformat_all_phonenumbers()
