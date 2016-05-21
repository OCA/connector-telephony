# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'phone.common']
    _phone_fields = ['phone', 'mobile', 'fax']
    _phone_name_sequence = 20
    _country_field = 'country_id'
    _partner_field = None

    @api.model
    def create(self, vals):
        vals_reformated = self._reformat_phonenumbers_create(vals)
        return super(CrmLead, self).create(vals_reformated)

    @api.multi
    def write(self, vals):
        vals_reformated = self._reformat_phonenumbers_write(vals)
        return super(CrmLead, self).write(vals_reformated)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('callerid'):
            res = []
            if isinstance(ids, (int, long)):
                ids = [ids]
            for lead in self.browse(cr, uid, ids, context=context):
                if lead.partner_name and lead.contact_name:
                    name = u'%s (%s)' % (lead.contact_name, lead.partner_name)
                elif lead.partner_name:
                    name = lead.partner_name
                elif lead.contact_name:
                    name = lead.contact_name
                else:
                    name = lead.name
                res.append((lead.id, name))
            return res
        else:
            return super(CrmLead, self).name_get(
                cr, uid, ids, context=context)


class ResUsers(models.Model):
    _inherit = "res.users"

    # Field name starts with 'context_' to allow modification by the user
    # in his preferences, cf server/openerp/addons/base/res/res_users.py
    # in "def write()" of "class res_users(osv.osv)"
    context_propose_creation_crm_call = fields.Boolean(
        string='Propose to create a call in CRM after a click2dial',
        default=True)


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
