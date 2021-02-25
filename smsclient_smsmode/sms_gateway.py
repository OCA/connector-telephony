# -*- coding: utf-8 -*-
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError
import requests
import re
import logging
_logger = logging.getLogger(__name__)


class SmsClient(models.Model):
    _inherit = "sms.gateway"

    @api.model
    def get_method(self):
        method = super(SmsClient, self).get_method()
        method.append(('http_smsmode', 'SMSmode HTTP'), )
        return method

    @api.onchange('method')
    def onchange_method(self):
        super(SmsClient, self).onchange_method()
        if self.method == 'http_smsmode':
            self.url_visible = True
            self.sms_account_visible = False
            self.login_provider_visible = False
            self.password_provider_visible = True
            self.from_provider_visible = True
            self.validity_visible = True
            self.classes_visible = False
            self.deferred_visible = False
            self.nostop_visible = True
            self.priority_visible = True
            self.coding_visible = True
            self.tag_visible = True
            self.char_limit_visible = True


class SmsSms(models.Model):
    _inherit = "sms.sms"

    @api.model
    def _prepare_http_smsmode(self):
        SMS_unit_max = 5
        try:
            self.message.encode('iso8859-15')
        except UnicodeEncodeError:
            raise UserError(_(
                "The message cannot be encoded in iso8859-15. This limitation "
                "could be overcomed, but it would use more SMS units."))

        numero = re.sub('\D', '', self.mobile)
        params = {
            'accessToken': self.gateway_id.password_provider,
            'emetteur': self.gateway_id.from_provider,
            'numero': numero,
            'message': self.message.encode('iso-8859-15'),
            'nbr_msg': SMS_unit_max,
            }
        max_size = SMS_unit_max * 153
        # 153 = nb of caracters in multi-SMS mode
        # So max_size = 153 * 5
        if len(self.message) > max_size:
            raise UserError(_(
                "The SMS that you're trying to send exceeds %d SMS units. "
                "The message has %d caracters. "
                "The maximum is %d caracters.")
                % (SMS_unit_max, len(self.message), max_size))
        if self.tag:
            params['refClient'] = self.tag
        return params

    @api.multi
    def _send_http_smsmode(self):
        self.ensure_one()
        params = self._prepare_http_smsmode()
        r = requests.get(self.gateway_id.url, params=params)
        params.update({
            'accessToken': '*****',
            'numero': '*****',
            })
        _logger.debug("Call SMSmode API : %s params %s",
                      self.gateway_id.url, params)
        if not r:
            raise ValueError(_("Failed to connect to SMSmode"))
        response = r.text
        if response[0] != '0':
            raise ValueError(response)
