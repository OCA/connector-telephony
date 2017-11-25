# coding: utf-8

import re
import logging

from odoo import api, models, _
from odoo.addons.iap.models.iap import InsufficientCreditError
from odoo.exceptions import UserError


try:
    import ovh
except (ImportError, IOError) as err:
    _logger = logging.getLogger(__name__)
    _logger.debug(err)


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        account = self.env['iap.account'].get('ovh')
        if account:
            return self._send_sms_by_ovh(account, numbers, message)
        return super(SmsApi, self)._send_sms(numbers, message)

    @api.model
    def _send_sms_by_ovh(self, account, numbers, message):
        def _sanitize_numbers(numbers):
            """ OVH expects a number to be:
                - a String
                - Only digits and +
                - First digit cannot be a 0
                - Between 7-15 digits long
                - In international format (not verified)
            """
            sanitized_numbers = set()
            for number in numbers:
                number = re.sub("[^0-9^+]", "", number)
                if len(number) > 6 and len(number) < 16:
                    sanitized_numbers.add(number)
            return list(sanitized_numbers)

        if not account.ovh_endpoint \
                or not account.ovh_application_key \
                or not account.ovh_application_secret \
                or not account.ovh_consumer_key \
                or not account.ovh_sms_account \
                or not account.ovh_sender:
            raise UserError(_('Your account is not configured.'))

        client = ovh.Client(account.ovh_endpoint,
                            application_key=account.ovh_application_key,
                            application_secret=account.ovh_application_secret,
                            consumer_key=account.ovh_consumer_key,)
        url = '/sms/%s/jobs/' % account.ovh_sms_account
        result_send = client.post(url,
                                  charset='UTF-8',
                                  coding='7bit',
                                  message=message,
                                  noStopClause=True,
                                  priority='high',
                                  receivers=_sanitize_numbers(numbers),
                                  senderForResponse=False,
                                  validityPeriod=2880,
                                  sender=account.ovh_sender,
                                  )

        if not(result_send.get('totalCreditsRemoved', False) > 0):
            raise InsufficientCreditError
        return True
