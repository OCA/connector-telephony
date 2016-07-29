# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class NumberNotFound(models.TransientModel):
    _inherit = "number.not.found"

    to_update_lead_id = fields.Many2one(
        'crm.lead', string='Lead to Update',
        domain=[('type', '=', 'lead')],
        help="Lead on which the phone number will be written")
    current_lead_phone = fields.Char(
        related='to_update_lead_id.phone', string='Current Phone',
        readonly=True)
    current_lead_mobile = fields.Char(
        related='to_update_lead_id.mobile', string='Current Mobile',
        readonly=True)

    @api.multi
    def create_lead(self):
        '''Function called by the related button of the wizard'''
        self.ensure_one()

        action = {
            'name': _('Create New Lead'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form,tree',
            'domain': ['|', ('type', '=', 'lead'), ('type', '=', False)],
            'nodestroy': False,
            'target': 'current',
            'context': {
                'default_%s' % self.number_type: self.e164_number,
                'default_type': 'lead',
                'stage_type': 'lead',
                'needaction_menu_ref': 'crm.menu_crm_opportunities',
                },
            }
        return action

    @api.multi
    def update_lead(self):
        self.ensure_one()
        if not self.to_update_lead_id:
            raise UserError(_("Select the Lead to Update."))
        self.to_update_lead_id.write({self.number_type: self.e164_number})
        action = {
            'name': _('Lead: %s' % self.to_update_lead_id.name),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'form,tree',
            'nodestroy': False,
            'target': 'current',
            'res_id': self.to_update_lead_id.id,
            'context': {
                'stage_type': 'lead',
                'needaction_menu_ref': 'crm.menu_crm_opportunities',
                },
            }
        return action
