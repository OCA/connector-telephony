# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class ServerAction(models.Model):

    _inherit = 'ir.actions.server'

    state = fields.Selection(selection_add=[('sms', 'Send SMS')])
    sms_template_id = fields.Many2one(
        comodel_name='sms.template',
        string='SMS Template',
        help='Select the SMS Template configuration to use with this action.',
    )

    @api.model
    def run_action_sms(self, action, eval_context=None):
        if not action.sms_template_id or not self._context.get('active_id'):
            return False
        cleaned_ctx = dict(self.env.context)
        cleaned_ctx.pop('default_type', None)
        cleaned_ctx.pop('default_parent_id', None)
        action.sms_template_id.with_context(cleaned_ctx).send_sms(
            self._context.get('active_id'),
            force_send=False,
            raise_exception=False,
        )
        return False

    @api.model
    def run_action_sms_multi(self, action, eval_context=None):
        if not action.sms_template_id:
            return False
        cleaned_ctx = dict(self.env.context)
        if self._context.get('active_id'):
            res_ids = self._context.get('active_id')
        else:
            res_ids = (
                self.env[action.model_id.model]
                .search([('mobile', '!=', False)])
                .ids
            )
        action.sms_template_id.with_context(cleaned_ctx).send_sms(
            res_ids, force_send=False, raise_exception=False
        )
        return False
