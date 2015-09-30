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

    def run_reformat_all_phonenumbers(self, ids):
        logger.info('Starting to reformat all the phone numbers')
        phonenumbers_not_reformatted = ''
        phoneobjects = self.env['phone.common']._get_phone_fields()
        ctx_raise = dict(self.env.context, raise_if_phone_parse_fails=True)
        for objname in phoneobjects:
            fields = self.env[objname]._phone_fields
            obj = self.env[objname]
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
            all_ids = obj.search(domain)
            for entry in obj.read(all_ids, fields):
                init_entry = entry.copy()
                # entry is _updated_ by the fonction
                # _generic_reformat_phonenumbers()
                try:
                    self.env.context = ctx_raise
                    obj._generic_reformat_phonenumbers([entry['id']], entry)
                except Exception, e:
                    name = obj.name_get([init_entry['id']])[0][1]
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
                    obj.write(init_entry['id'], entry)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = \
                'All phone numbers have been reformatted successfully.'
        self.write(ids[0], {'phonenumbers_not_reformatted': phonenumbers_not_reformatted, 'state': 'done'})
        logger.info('End of the phone number reformatting wizard')
        action = self.env['ir.actions.act_window'].for_xml_id('base_phone', 'reformat_all_phonenumbers_action')
        action['res_id'] = ids[0]
        return action
