# -*- coding: utf-8 -*-
# Copyright 2010-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError


class NumberNotFound(models.TransientModel):
    _inherit = "number.not.found"

    to_update_lead_id = fields.Many2one(
        'crm.lead', string='Lead or Opportunity to Update',
        help="Lead or opportunity on which the phone number will be written.")
    current_lead_phone = fields.Char(
        related='to_update_lead_id.phone', readonly=True)
    current_lead_mobile = fields.Char(
        related='to_update_lead_id.mobile', readonly=True)

    def create_lead(self):
        '''Function called by the related button of the wizard'''
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id(
            'crm', 'crm_lead_all_leads')
        form_views = [viewt for viewt in action['views'] if viewt[1] == 'form']
        action.update({
            'view_mode': 'form',
            'views': form_views,
            'context': {
                'default_%s' % self.number_type: self.e164_number,
                'default_type': 'lead',
                'search_default_type': 'lead',
                'search_default_to_process': True,
                },
            })
        return action

    def create_opportunity(self):
        '''Function called by the related button of the wizard'''
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id(
            'crm', 'crm_lead_opportunities')
        form_views = [viewt for viewt in action['views'] if viewt[1] == 'form']
        action.update({
            'view_mode': 'form',
            'views': form_views,
            'context': {
                'default_%s' % self.number_type: self.e164_number,
                'default_type': 'opportunity',
                'search_default_type': 'opportunity',
                },
            })
        return action

    def update_lead(self):
        self.ensure_one()
        if not self.to_update_lead_id:
            raise UserError(_("Select the Lead or Opportunity to Update."))
        self.to_update_lead_id.write({self.number_type: self.e164_number})
        if self.to_update_lead_id.type == 'lead':
            action = self.env['ir.actions.act_window'].for_xml_id(
                'crm', 'crm_lead_all_leads')
        else:
            action = self.env['ir.actions.act_window'].for_xml_id(
                'crm', 'crm_lead_opportunities')
        form_views = [viewt for viewt in action['views'] if viewt[1] == 'form']
        action.update({
            'view_mode': 'form',
            'views': form_views,
            'res_id': self.to_update_lead_id.id,
            })
        return action
