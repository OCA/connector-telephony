# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ReformatAllPhonenumbers(models.TransientModel):
    _name = "reformat.all.phonenumbers"
    _inherit = "res.config.installer"
    _description = "Reformat all phone numbers"

    phonenumbers_not_reformatted = fields.Text(
        string="Phone numbers that couldn't be reformatted")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='State', default='draft')

    @api.multi
    def run_reformat_all_phonenumbers(self):
        self.ensure_one()
        logger.info('Starting to reformat all the phone numbers')
        phonenumbers_not_reformatted = u''
        phoneobjects = self.env['phone.common']._get_phone_models()
        for obj_dict in phoneobjects:
            fields = obj_dict['fields']
            obj = obj_dict['object']
            logger.info(
                'Starting to reformat phone numbers on object %s '
                '(fields = %s)', obj._name, fields)
            # search if this object has an 'active' field
            if obj._fields.get('active') or obj._name == 'hr.employee':
                # hr.employee inherits from 'resource.resource' and
                # 'resource.resource' has an active field
                # As I don't know how to detect such cases, I hardcode it here
                # If you know a better solution, please tell me
                domain = ['|', ('active', '=', True), ('active', '=', False)]
            else:
                domain = []
            all_entries = obj.search(domain)

            for entry in all_entries:
                vals = {}
                for field in fields:
                    vals[field] = entry[field]
                if any([value for value in vals.values()]):
                    entry.write(vals)
        if not phonenumbers_not_reformatted:
            phonenumbers_not_reformatted = \
                'All phone numbers have been reformatted successfully.'
        self.write({
            'phonenumbers_not_reformatted': phonenumbers_not_reformatted,
            'state': 'done',
            })
        logger.info('End of the phone number reformatting wizard')
        action = self.env['ir.actions.act_window'].for_xml_id(
            'base_phone', 'reformat_all_phonenumbers_action')
        action['res_id'] = self.id
        return action
