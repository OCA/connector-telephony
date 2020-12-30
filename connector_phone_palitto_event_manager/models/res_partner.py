import hashlib
import logging
import urllib

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def outgoing_call_notification(self):
        # For Outgoing Calls
        if not self.env.user.company_id.server_address:
            raise UserError(_("Please specify server address in Company Setting"))
        server = self.env.user.company_id.server_address + "/DialNumber/?"
        number = self.phone  # Fetched from partner

        user = self.env.user
        ext = user.external_code  # Fetched from user
        cid = user.related_phone  # Fetched from user
        cidname = user.name  # Fetched from user
        password = user.phone_password  # Fetched from user

        if not password:
            raise UserError(_("No password configured on User"))

        # Generate AUTH via sha1
        hash_object = hashlib.sha1((password + ext).encode("utf-8"))
        auth = hash_object.hexdigest()

        payload = {
            "ext": ext,
            "number": number,
            "cid": cid,
            "cidname": cidname,
            "auth": auth,
        }
        payload = urllib.parse.urlencode(payload)
        url = server + payload
        _logger.info("URL ---- %s", url)
        response = requests.get(url=url, params={})
        # ToDo : This should be modified based on real response
        if response.status_code in (400, 401, 404, 500):
            error_msg = _(
                "Request Call failed with Status %s.\n\n"
                "Request:\nGET %s\n\n"
                "Response:\n%s"
            ) % (response.status_code, url or "", response.text)
            _logger.error(error_msg)
        _logger.info("response ----", response.text)

    @api.multi
    def incoming_call_notification(self):
        action = {
            "name": _("Customer"),
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "form",
            "views": [[False, "form"]],
            "target": "new",
            "res_id": self.id,
        }
        return action
