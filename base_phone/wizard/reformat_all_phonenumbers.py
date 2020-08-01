# -*- encoding: utf-8 -*-
##############################################################################
#
#    Base Phone module for Odoo
#    Copyright (C) 2012-2015 Alexis de Lattre <alexis@via.ecp.fr>
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

from openerp import models, fields
import logging

logger = logging.getLogger(__name__)


class reformat_all_phonenumbers(models.TransientModel):
    _name = "reformat.all.phonenumbers"
    _inherit = "res.config.installer"
    _description = "Reformat all phone numbers"

    phonenumbers_not_reformatted = fields.Text(
        string="Phone numbers that couldn't be reformatted")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='State', default='draft')

    def run_reformat_all_phonenumbers(self, cr, uid, ids, context=None):
        logger.info('Starting to reformat all the phone numbers')
        phonenumbers_not_reformatted = ''
        phoneobjects = self.pool['phone.common']._get_phone_fields(
            cr, uid, context=context)
        ctx_raise = dict(context, raise_if_phone_parse_fails=True)
        for objname in phoneobjects:
            fields = self.pool[objname]._phone_fields
            obj = self.pool[objname]
            logger.info(
                'Starting to reformat phone numbers on object %s '
                '(fields = %s)' % (objname, fields))
            # search if this object has an 'active' field
            if obj._columns.get('active') or objname == 'hr.employee':
                # hr.employee inherits from 'resource.resource' and
                # 'resource.resource' has an active field
                # As I don't know how to detect such cases, I hardcode it here
                # If you know a better solution, please tell me
                domain = ['|', ('active', '=', True), ('active', '=', False)]
            else:
                domain = []
            all_ids = obj.search(cr, uid, domain, context=context)
            for entry in obj.read(
                    cr, uid, all_ids, fields, context=context):
                init_entry = entry.copy()
                # entry is _updated_ by the fonction
                # _generic_reformat_phonenumbers()
                try:
                    obj._generic_reformat_phonenumbers(
                        cr, uid, [entry['id']], entry, context=ctx_raise)
                except Exception, e:
                    name = obj.name_get(
                        cr, uid, [init_entry['id']], context=context)[0][1]
                    phonenumbers_not_reformatted += \
                        "Problem on %s '%s'. Error message: %s\n" % (
                            obj._description, name, unicode(e))
                    logger.warning(
                        "Problem on %s '%s'. Error message: %s" % (
                            obj._description, name, unicode(e)))
                    continue
                if any(
                        [init_entry.get(field)
                            != entry.get(field) for field
                            in fields]):
                    entry.pop('id')
                    logger.info(
                        '[%s] Reformating phone number: FROM %s TO %s' % (
                            obj._description, unicode(init_entry),
                            unicode(entry)))
                    obj.write(
                        cr, uid, init_entry['id'], entry, context=context)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = \
                'All phone numbers have been reformatted successfully.'
        self.write(
            cr, uid, ids[0], {
                'phonenumbers_not_reformatted': phonenumbers_not_reformatted,
                'state': 'done',
                }, context=context)
        logger.info('End of the phone number reformatting wizard')
        action = self.pool['ir.actions.act_window'].for_xml_id(
            cr, uid, 'base_phone', 'reformat_all_phonenumbers_action',
            context=context)
        action['res_id'] = ids[0]
        return action
