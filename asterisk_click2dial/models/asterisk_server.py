# Copyright 2010-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from pprint import pformat

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
TIMEOUT = 10


class AsteriskServer(models.Model):
    """Asterisk server object, stores the parameters of the Asterisk IPBXs"""

    _name = "asterisk.server"
    _description = "Asterisk Servers"

    name = fields.Char(string="Asterisk Server Name", required=True)
    active = fields.Boolean(default=True)
    ip_address = fields.Char(string="Asterisk IP address or DNS", required=True)
    port = fields.Integer(
        required=True,
        default=5038,
        help="TCP port on which the Asterisk REST Interface listens. "
        "Defined in /etc/asterisk/ari.conf on Asterisk.",
    )
    out_prefix = fields.Char(
        size=4,
        help="Prefix to dial to make outgoing "
        "calls. If you don't use a prefix to make outgoing calls, "
        "leave empty.",
    )
    login = fields.Char(
        string="ARI Login",
        required=True,
        help="Login that Odoo will use to communicate with the "
        "Asterisk REST Interface. Refer to /etc/asterisk/ari.conf "
        "on your Asterisk server.",
    )
    password = fields.Char(
        string="ARI Password",
        required=True,
        help="Password that Odoo will use to communicate with the "
        "Asterisk REST Interface. Refer to /etc/asterisk/ari.conf "
        "on your Asterisk server.",
    )
    context = fields.Char(
        string="Dialplan Context",
        required=True,
        help="Asterisk dialplan context from which the calls will be "
        "made. Refer to /etc/asterisk/extensions.conf on your Asterisk "
        "server.",
    )
    wait_time = fields.Integer(
        required=True,
        default=15,
        help="Amount of time (in seconds) Asterisk will try to reach "
        "the user's phone before hanging up.",
    )
    extension_priority = fields.Integer(
        required=True,
        default=1,
        help="Priority of the extension in the Asterisk dialplan. Refer "
        "to /etc/asterisk/extensions.conf on your Asterisk server.",
    )
    alert_info = fields.Char(
        string="Alert-Info SIP Header",
        help="Set Alert-Info header in SIP request to user's IP Phone "
        "for the click2dial feature. If empty, the Alert-Info header "
        "will not be added. You can use it to have a special ring tone "
        "for click2dial (a silent one !) or to activate auto-answer "
        "for example.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        help="Company who uses the Asterisk server.",
    )

    @api.constrains(
        "out_prefix",
        "wait_time",
        "extension_priority",
        "port",
        "context",
        "alert_info",
        "login",
        "password",
    )
    def _check_validity(self):
        for server in self:
            out_prefix = ("Out prefix", server.out_prefix)
            dialplan_context = ("Dialplan context", server.context)
            alert_info = ("Alert-Info SIP header", server.alert_info)
            login = ("ARI login", server.login)
            password = ("ARI password", server.password)

            if out_prefix[1] and not out_prefix[1].isdigit():
                raise ValidationError(
                    _(
                        "Only use digits for the '%(out_prefix[0])s' on the Asterisk server "
                        "'%(server.name)s'"
                    )
                )
            if server.wait_time < 1 or server.wait_time > 120:
                raise ValidationError(
                    _(
                        "You should set a 'Wait time' value between 1 and 120 "
                        "seconds for the Asterisk server '%s'" % server.name
                    )
                )
            if server.extension_priority < 1:
                raise ValidationError(
                    _(
                        "The 'extension priority' must be a positive value for "
                        "the Asterisk server '%s'" % server.name
                    )
                )
            if server.port > 65535 or server.port < 1:
                raise ValidationError(
                    _(
                        "You should set a TCP port between 1 and 65535 for the "
                        "Asterisk server '%s'" % server.name
                    )
                )
            for check_str in [dialplan_context, alert_info, login, password]:
                if check_str[1]:
                    try:
                        check_str[1].encode("ascii")
                    except UnicodeEncodeError:
                        raise ValidationError from None(
                            _(
                                "The '%(check_str[0])s' should only have ASCII caracters for "
                                "the Asterisk server '%(server.name)s'"
                            )
                        )

    @api.model
    def _get_connect_info(self, url_path):
        user = self.env.user
        ast_server = user.get_asterisk_server_from_user()
        auth = (ast_server.login, ast_server.password)
        url = "http://%s:%s%s" % (ast_server.ip_address, ast_server.port, url_path)
        return ast_server, auth, url

    def test_ari_connection(self):
        self.ensure_one()
        auth = (self.login, self.password)
        url = "http://%s:%s/ari/asterisk/info" % (self.ip_address, self.port)
        try:
            res = requests.get(url, auth=auth, timeout=TIMEOUT)
        except Exception as e:
            raise UserError from None(
                _("Connection Test Failed! The error message is: %s" % e)
            )
        if res.status_code != 200:
            raise UserError(
                _("Connection Test Failed! HTTP error code: %s" % res.status_code)
            )
        raise UserError(
            _(
                "Connection Test Successfull! Odoo can successfully login to "
                "the Asterisk Manager Interface."
            )
        )

    @api.model
    def _get_calling_number_from_channel(self, chan, user):
        """
        Method designed to be inherited to work with
        very old or specific versions of Asterisk
        """
        sip_account = user.asterisk_chan_name
        if chan.get("state") in ("Up", "Ringing") and sip_account in chan.get(
            "name", ""
        ):
            number = chan.get("connected", {}).get("number")
            _logger.debug(
                "Found a matching Event with channelstate = %s. Returning number %s",
                chan.get("state"),
                number,
            )
            return number
        return False

    @api.model
    def _get_calling_number(self):
        ast_server, auth, url = self._get_connect_info("/ari/channels")
        user = self.env.user
        calling_party_number = False
        try:
            res_req = requests.get(url, auth=auth, timeout=TIMEOUT)
            if res_req.status_code != 200:
                _logger.error(
                    "ARI request on %s returned HTTP error code %s",
                    url,
                    res_req.status_code,
                )
                return False
            list_chan = res_req.json()
            from pprint import pprint

            pprint(list_chan)
            _logger.debug("Result of Status ARI request:")
            _logger.debug(pformat(list_chan))
            for chan in list_chan:
                calling_party_number = self._get_calling_number_from_channel(chan, user)
                if calling_party_number:
                    break
        except Exception as e:
            _logger.error(
                "Error in the Status request to Asterisk server %s",
                ast_server.ip_address,
            )
            _logger.error("Here are the details of the error: '%s'", str(e))
            raise UserError from None(
                _(
                    "Can't get calling number from  Asterisk.\nHere is the "
                    "error: '%s'" % str(e)
                )
            )

        _logger.debug("Calling party number: '%s'", calling_party_number)
        return calling_party_number

    @api.model
    def get_record_from_my_channel(self):
        calling_number = self.env["asterisk.server"]._get_calling_number()
        # calling_number = "0641981246"
        if calling_number:
            record = self.env["phone.common"].get_record_from_phone_number(
                calling_number
            )
            if record:
                return record
            else:
                return calling_number
        else:
            return False
