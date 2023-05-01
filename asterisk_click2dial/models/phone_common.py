# Copyright 2010-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import _, api, exceptions, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
TIMEOUT = 10


class PhoneCommon(models.AbstractModel):
    _inherit = "phone.common"

    @api.model
    def click2dial(self, erp_number):
        res = super().click2dial(erp_number)
        if not erp_number:
            raise UserError(_("Missing phone number"))

        user = self.env.user
        aso = self.env["asterisk.server"]
        ast_server, auth, url = aso._get_connect_info("/ari/channels")
        ast_number = self.convert_to_dial_number(erp_number)
        # Add 'out prefix'
        if ast_server.out_prefix:
            _logger.debug("Out prefix = %s", ast_server.out_prefix)
            ast_number = "%s%s" % (ast_server.out_prefix, ast_number)
        _logger.debug("Number to be sent to Asterisk = %s", ast_number)

        # The user should have a CallerID
        if not user.callerid:
            raise UserError(_("No callerID configured for the current user"))

        variable = []
        if user.asterisk_chan_type in ("SIP", "PJSIP"):
            # We can only have one alert-info header in a SIP request
            if user.alert_info:
                variable.append("SIPAddHeader=Alert-Info: %s" % user.alert_info)
            elif ast_server.alert_info:
                variable.append("SIPAddHeader=Alert-Info: %s" % ast_server.alert_info)
            if user.variable:
                for user_variable in user.variable.split("|"):
                    variable.append(user_variable.strip())
        channel = user.asterisk_chan_name
        if user.dial_suffix:
            channel += "/%s" % user.dial_suffix

        params = {
            "endpoint": channel,
            "extension": ast_number,
            "context": ast_server.context,
            "priority": str(ast_server.extension_priority),
            "timeout": str(ast_server.wait_time),
            "callerId": user.callerid,
        }
        # TODO set variable in body
        # https://wiki.asterisk.org/wiki/display/AST/
        # Asterisk+17+Channels+REST+API#Asterisk17ChannelsRESTAPI-originate

        try:
            res_req = requests.post(url, auth=auth, params=params, timeout=TIMEOUT)
        except Exception as e:
            _logger.error(
                "Error in the Originate request to Asterisk server %s",
                ast_server.ip_address,
            )
            _logger.error("Here are the details of the error: '%s'", str(e))
            raise UserError from exceptions(
                _("Click to dial with Asterisk failed.\nHere is the error: '%s'")
                % str(e)
            )
        if res_req.status_code != 200:
            raise UserError(
                _("Click to dial with Asterisk failed.\nHTTP error code: %s.")
                % res.status_code
            )

        res["dialed_number"] = ast_number
        return res
