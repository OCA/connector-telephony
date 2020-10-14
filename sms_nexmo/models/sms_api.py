# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

from nexmo import Client
from nexmo.sms import Sms


class SmsApi(models.AbstractModel):

    _inherit = 'sms.api'

    def _send_sms_nexmo(self, sms, params):
        return sms.send_message(params)

    @api.model
    def _send_sms(self, numbers, message):
        account = self.env['iap.account'].get('nexmo.sms')
        if not account:
            return super(SmsApi, self)._send_sms(numbers, message)

        sms = Sms(Client(key=account.key, secret=account.secret))
        self._send_sms_nexmo(sms, {
            'from': 'Odoo',
            'to': numbers,
            'text': message,
        })

    @api.model
    def _send_sms_batch(self, messages):
        account = self.env['iap.account'].get('nexmo.sms')
        if not account:
            return super(SmsApi, self)._send_sms_batch(messages)

        sms = Sms(Client(key=account.key, secret=account.secret))

        for record in messages:
            result = self._send_sms_nexmo(sms, {
                'from': 'Odoo',
                'to': record['number'],
                'text': record['content'],
            })
            if result['messages'][0]['status'] == '0':
                record['state'] = 'success'
            else:
                record['state'] = 'error'
        return messages
