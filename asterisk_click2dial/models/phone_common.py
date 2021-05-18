# Copyright 2010-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super().click2dial(erp_number)
        if not erp_number:
            raise UserError(_('Missing phone number'))

        user, ast_server, ast_manager = \
            self.env['asterisk.server']._connect_to_asterisk()
        ast_number = self.convert_to_dial_number(erp_number)
        # Add 'out prefix'
        if ast_server.out_prefix:
            _logger.debug('Out prefix = %s', ast_server.out_prefix)
            ast_number = '%s%s' % (ast_server.out_prefix, ast_number)
        _logger.debug('Number to be sent to Asterisk = %s', ast_number)

        # The user should have a CallerID
        if not user.callerid:
            raise UserError(_('No callerID configured for the current user'))

        variable = []
        if user.asterisk_chan_type in ('SIP', 'PJSIP'):
            # We can only have one alert-info header in a SIP request
            if user.alert_info:
                variable.append(
                    'SIPAddHeader=Alert-Info: %s' % user.alert_info)
            elif ast_server.alert_info:
                variable.append(
                    'SIPAddHeader=Alert-Info: %s' % ast_server.alert_info)
            if user.variable:
                for user_variable in user.variable.split('|'):
                    variable.append(user_variable.strip())
        channel = '%s/%s' % (user.asterisk_chan_type, user.resource)
        if user.dial_suffix:
            channel += '/%s' % user.dial_suffix

        try:
            ast_manager.Originate(
                channel,
                context=ast_server.context,
                extension=ast_number,
                priority=str(ast_server.extension_priority),
                timeout=str(ast_server.wait_time * 1000),
                caller_id=user.callerid,
                account=user.cdraccount,
                variable=variable)
        except Exception as e:
            _logger.error(
                "Error in the Originate request to Asterisk server %s",
                ast_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'", str(e))
            raise UserError(_(
                "Click to dial with Asterisk failed.\nHere is the error: "
                "'%s'") % str(e))
        finally:
            ast_manager.Logoff()

        res['dialed_number'] = ast_number
        return res
