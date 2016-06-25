# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.addons.base_phone.fields import Phone


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _phone_name_sequence = 20

    phone = Phone(country_field='country_id', partner_field='partner_id')
    mobile = Phone(country_field='country_id', partner_field='partner_id')
    fax = Phone(country_field='country_id', partner_field='partner_id')
    phonecall_ids = fields.One2many(
        'crm.phonecall', 'opportunity_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_count_phonecalls', string='Number of Phonecalls',
        readonly=True)

    @api.multi
    def name_get(self):
        if self._context.get('callerid'):
            res = []
            for lead in self:
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
            return super(CrmLead, self).name_get()

    @api.multi
    @api.depends('phonecall_ids')
    def _count_phonecalls(self):
        cpo = self.env['crm.phonecall']
        for lead in self:
            try:
                lead.phonecall_count = cpo.search_count(
                    [('opportunity_id', '=', lead.id)])
            except:
                lead.phonecall_count = 0


class CrmPhonecall(models.Model):
    _name = 'crm.phonecall'
    _inherit = ['mail.thread']
    _order = "id desc"

    # Restore the object that existed in v8
    # and doesn't exist in v9 community any more
    name = fields.Char(
        string='Call Summary', required=True, track_visibility='onchange')
    date = fields.Datetime(
        string='Date', track_visibility='onchange', copy=False,
        default=lambda self: fields.Datetime.now())
    description = fields.Text(string='Description', copy=False)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'crm.phonecall'))
    user_id = fields.Many2one(
        'res.users', string='Responsible', track_visibility='onchange',
        default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team', track_visibility='onchange',
        default=lambda self: self.env['crm.team']._get_default_team_id())
    partner_id = fields.Many2one(
        'res.partner', string='Contact', ondelete='cascade')
    partner_phone = Phone(string='Phone', partner_field='partner_id')
    partner_mobile = Phone(string='Mobile', partner_field='partner_id')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')
        ], string='Priority', track_visibility='onchange', default='1')
    opportunity_id = fields.Many2one(
        'crm.lead', string='Lead/Opportunity',
        ondelete='cascade', track_visibility='onchange')
    state = fields.Selection([
        ('open', 'To Do'),
        ('done', 'Held'),
        ('cancel', 'Cancelled'),
        ], string='Status', default='open', copy=False, required=True,
        track_visibility='onchange',
        help='The status is set to Confirmed, when a case is created.\n'
        'When the call is over, the status is set to Held.\n'
        'If the call is not applicable anymore, the status can be set to '
        'Cancelled.')
    direction = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ], string='Type', required=True, default='outbound')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
            self.partner_mobile = self.partner_id.mobile

    @api.onchange('opportunity_id')
    def onchange_opportunity_id(self):
        if self.opportunity_id:
            self.partner_phone = self.opportunity_id.phone
            self.partner_mobile = self.opportunity_id.mobile
            self.team_id = self.opportunity_id.team_id.id
            self.partner_id = self.opportunity_id.partner_id.id

    @api.multi
    def schedule_another_call(self):
        self.ensure_one()
        cur_call = self[0]
        ctx = self._context.copy()
        ctx.update({
            'default_date': False,
            'default_partner_id': cur_call.partner_id.id,
            'default_opportunity_id': cur_call.opportunity_id.id,
            'default_direction': 'outbound',
            'default_partner_phone': cur_call.partner_phone,
            'default_partner_mobile': cur_call.partner_mobile,
        })
        action = {
            'name': _('Phone Call'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.phonecall',
            'view_mode': 'form,tree,calendar',
            'context': ctx,
            }
        return action


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonecall_ids = fields.One2many(
        'crm.phonecall', 'partner_id', string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_count_phonecalls', string='Number of Phonecalls',
        readonly=True)

    @api.multi
    @api.depends('phonecall_ids')
    def _count_phonecalls(self):
        cpo = self.env['crm.phonecall']
        for partner in self:
            try:
                partner.phonecall_count = cpo.search_count(
                    [('partner_id', 'child_of', partner.id)])
            except:
                partner.phonecall_count = 0


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
