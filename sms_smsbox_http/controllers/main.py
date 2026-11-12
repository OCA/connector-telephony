# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import re

from odoo.http import Controller, request, route

_logger = logging.getLogger(__name__)


class SmsSmsboxHttpController(Controller):
    @route(
        "/sms_smsbox_http/status/<string:token>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def sms_smsbox_http_status(self, token, accuse=None, odoo_uuid=None, **kwargs):
        account = (
            request.env["iap.account"]
            .sudo()
            .search(
                [
                    ("provider", "=", "sms_smsbox_http"),
                    ("sms_smsbox_http_callback_token", "=", token),
                ],
                limit=1,
            )
        )
        if not account:
            raise request.not_found()
        # SMSBOX retries until it gets "OK": acknowledge ignored reports too.
        if not accuse or not re.fullmatch(r"[0-9a-f]{32}", odoo_uuid or ""):
            _logger.warning("SMSBOX: ignored delivery report %s", request.params)
            return "OK"
        tracker = (
            request.env["sms.tracker"]
            .sudo()
            .search([("sms_uuid", "=", odoo_uuid)], limit=1)
        )
        if tracker:
            tracker._action_update_from_smsbox_http(accuse)
            request.env["sms.sms"].sudo().search(
                [("uuid", "=", odoo_uuid), ("to_delete", "=", False)]
            ).to_delete = True
        return "OK"
