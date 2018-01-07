# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super(PhoneCommon, self).click2dial(erp_number)
        if (
                self.env.user.context_propose_creation_crm_call and
                self.env.context.get('click2dial_model')
                in ('res.partner', 'crm.lead')):
            res.update({
                'action_name': _('Create Call in CRM'),
                'action_model': 'wizard.create.crm.phonecall',
                })
        return res
