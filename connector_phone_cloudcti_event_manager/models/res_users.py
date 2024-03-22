import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth
from odoo import models, fields, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    cloudcti_token = fields.Char("Token")
    token_expiration_time = fields.Datetime("Expiration Time")
    session_id = fields.Char("Session")

    def generate_cloudcti_access_token(self):
        for user in self:
            credentials = user.partner_id._get_cloudcti_credentials(user)
            auth_token_url = credentials['sign_address']
            sub_token_url = credentials['sub_address']
            try:
                response = requests.get(
                    url=auth_token_url,
                    auth=HTTPBasicAuth(
                        credentials.get("cloudcti_username"),
                        credentials.get("cloudcti_password")
                    ),
                )
                response.raise_for_status()
                response_data = response.json()
                access_token = response_data["SecurityToken"]
                expiration_time = response_data["SecurityTokenExpirationTime"]
                #subscription
                if sub_token_url and access_token:
                    headers = {
                        "content-type": "application/json",
                        "Authorization": "Bearer " + access_token,
                        "Accept": 'text/plain'
                    }
                    response = requests.request(
                        "POST",
                        sub_token_url,
                        headers=headers
                    )
                    response_data = response.json()
                    session_id = response_data["SessionId"]
            except (
                requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
                requests.exceptions.ConnectionError,
            ) as err:
                raise UserError(
                    _("Error! \n Could not retrive token from CloudCTI. %s") % (err)
                ) from err
            user.sudo().write(
                {
                    "cloudcti_token": access_token,
                    "token_expiration_time": expiration_time,
                    "session_id": session_id
                }
            )
