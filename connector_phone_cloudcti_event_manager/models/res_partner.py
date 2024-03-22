import datetime
import logging
import re

import requests
import simplejson
from requests.auth import HTTPBasicAuth

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.web.controllers.utils import clean_action

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    called_for_phone = fields.Boolean()
    called_for_mobile = fields.Boolean()

    def update_called_for_values(self):
        for partner in self:
            if self._context.get("phone_partner"):
                partner.called_for_phone = True
                partner.called_for_mobile = False
            elif self._context.get("mobile_partner"):
                partner.called_for_phone = False
                partner.called_for_mobile = True
            else:
                partner.called_for_phone = False
                partner.called_for_mobile = False

    def _get_cloudcti_credentials(self, user):
        company_id = user.company_id
        if not all(
            [
                company_id.cloudcti_base_url,
                company_id.cloudcti_signin_url,
                company_id.cloudcti_out_url,
                company_id.cloudcti_subscription_url,
            ]
        ):
            raise UserError(_("Please configure CloudCTI URLs in Company Setting."))

        if not user.token_expiration_time or (
            datetime.datetime.now() > user.token_expiration_time
        ):
            expired = True
        else:
            expired = False

        # Check if user.phone is not None and is a string
        if user.phone is not None and isinstance(user.phone, str):
            cloudcti_username = re.sub(r"\D", "", user.phone)
        else:
            cloudcti_username = ""

        return {
            "base_address": company_id.cloudcti_base_url,
            "sign_address": company_id.cloudcti_signin_url,
            "out_address": company_id.cloudcti_out_url,
            "sub_address": company_id.cloudcti_subscription_url,
            "token": user.cloudcti_token,
            "expired": expired,
            "cloudcti_username": cloudcti_username,
            "cloudcti_password": user.phone_password,
        }

    def cloudcti_open_outgoing_notification(self):
        channel = "notify_info_%s" % self.env.user.id
        bus_message = {
            "message": _("Calling from : %s" % self.env.user.phone),
            "title": _("Outgoing Call to %s" % self.display_name),
            "action_link_name": "action_link_name",
            "Outnotification": "OutGoingNotification",
            "id": self.id,
        }
        self.update_called_for_values()
        self.cloudcti_outgoing_call_notification()
        # self.env["bus.bus"].sendone(channel, bus_message)

    def cloudcti_outgoing_call_notification(self):
        # For Outgoing Calls
        if self == {}:
            raise UserError(_("Bad Partner Record"))

        # get token
        credentials = self._get_cloudcti_credentials(self.env.user)

        # if token is expired, get a new one
        if credentials["expired"]:
            self.env.user.generate_cloudcti_access_token()
            credentials = self._get_cloudcti_credentials(self.env.user)

        # Fetched from partner
        number = re.sub(
            r"\D",
            "",
            self.sudo().called_for_mobile and self.sudo().mobile or self.sudo().phone,
        )

        data = {
            "Number": number,
        }

        payload = simplejson.dumps(data)

        # use token credentials to connect
        if credentials.get("token") and not credentials.get("expired"):
            headers = {
                "content-type": "application/json",
                "Authorization": "Bearer " + credentials.get("token"),
                "Accept": "text/plain",
            }
            url = credentials.get("out_address") + "/makecall"
            response = requests.request("POST", url, data=payload, headers=headers)

        # not secure fallback to basic authentication
        else:
            headers = {"content-type": "application/json"}
            url = credentials["base_address"] + "/makecall/" + number
            response = requests.request(
                "GET",
                url,
                auth=HTTPBasicAuth(
                    credentials.get("cloudcti_username"),
                    credentials.get("cloudcti_password"),
                ),
                headers=headers,
            )
        _logger.info("Response ---- %s", response.text)
        # error in response
        if response.status_code in (400, 401, 403, 403, 500):
            error_msg = _(
                "Request Call failed with Status %s.\n\n"
                "Request:\nGET %s\n\n"
                "Response:\n%s"
            ) % (response.status_code, url or "", response.text)
            _logger.error(error_msg)

    def incoming_call_notification(self):
        partners = self.ids
        action = self.env.ref(
            "connector_phone_cloudcti_event_manager.cloudcti_action_partners_tree_all"
        ).read()[0]
        if len(partners) > 1:
            action["domain"] = [("id", "in", partners)]
        elif partners:
            form_view = [(self.env.ref("base.view_partner_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = partners[0]
        action = clean_action(action)
        return action

    # def incall_notify_by_login_test(self, number, login_list):
    #     self.incall_notify_by_login('(582) 126-8105',['admin'])

    # @api.model
    # def incall_notify_by_login(self, number, login_list, calltype="Incoming Call"):
    #     number = False
    #     assert isinstance(login_list, list), "login_list must be a list"
    #     bus_message = {
    #         "message": _(calltype + " from : " + self.name),
    #         "title": _(calltype),
    #         "action_link_name": "action_link_name",
    #         "notification": "IncomingNotification",
    #         "id": self.id,
    #         "phone": number
    #     }

    #     return bus_message
