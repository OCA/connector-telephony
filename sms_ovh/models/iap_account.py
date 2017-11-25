# coding: utf-8

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class IapAccount(models.Model):
    _inherit = 'iap.account'

    ovh_endpoint = fields.Char('End Point', default='ovh-eu')
    ovh_application_key = fields.Char('Application key')
    ovh_application_secret = fields.Char('Application secret')
    ovh_consumer_key = fields.Char('Consumer key')
    ovh_sms_account = fields.Char('SMS account')
    ovh_sender = fields.Char('Sender')

    @api.model
    def get(self, service_name):
        if service_name == 'sms':
            return super(IapAccount, self).get(service_name)
        account = self.search([('service_name', '=', service_name), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        if not account:
            raise UserError(_('You need to create an IAP account with service name : %s.') % service_name)
        return account
