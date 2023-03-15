# © 2023 CONINPE Consultores Informaticos: Telmo Suarez Venero <tsuarez@zertek.es>
# License AGPL-3.0 or later (http://gnu.org/license/agpl.html).
import requests

from odoo import _, api, exceptions, fields, models


class VozTelecomConfig(models.Model):
    _name = "voztelecom.config"
    _description = "VozTelecom API configuration model"

    active_configuration = fields.Boolean(string="Activado")
    name = fields.Char(string="Nombre")
    api_token = fields.Char(string="VozTelecom API token")
    callback_url = fields.Char(string="Dominio de respuesta para la API")
    state = fields.Selection(
        [("done", "Activo"), ("blocked", "Desactivado")],
        string="Kanban State",
        copy=False,
        default="blocked",
        required=True,
    )

    def api_configuration(self):

        try:
            check = requests.post(
                self.callback_url + "/vtcrm/callback/", json={"test": "test"}
            )
        except Exception as e:
            raise exceptions.ValidationError(
                _("Error en la configuración de la API: ") + str(e)
            )

        if check.status_code != 404:
            internal_api_key = self.env["res.users.apikeys"]._generate(
                None, "voz_telecom api key"
            )
            res = requests.post(
                "https://config.work.oigaa.com/vtcrm/api/configure",
                '{"events_callback_url":"' + self.callback_url + '/vtcrm/callback/"'
                ","
                '"events_callback_headers":{'
                '"user":"'
                + self.env.user.login
                + '","password":"'
                + internal_api_key
                + '","db":"'
                + self._cr.dbname
                + '"}}',
                headers={
                    "content-type": "json",
                    "Authorization": "VTCRM-Basic " + self.api_token,
                },
            )
            if res.status_code == 200:
                self.state = "done"
            else:
                raise exceptions.UserError(res.text)
        else:
            raise exceptions.UserError(_("La URL de respuesta no es correcta"))

    @api.onchange("api_token", "callback_url")
    def reset_state(self):
        self.state = "blocked"

    def api_trigger_call(self, extension, destination):
        requests.post(
            "https://config.work.oigaa.com/vtcrm/api/call",
            '{"extension": "' + extension + '","destination": "' + destination + '"}',
            headers={
                "content-type": "json",
                "Authorization": "VTCRM-Basic " + self.api_token,
            },
        )

    def api_drop_call(self, callId):
        requests.post(
            "https://config.work.oigaa.com/vtcrm/api/drop",
            '{"callId": "' + callId + '"}',
            headers={
                "content-type": "json",
                "Authorization": "VTCRM-Basic " + self.api_token,
            },
        )

    def api_redirect_call(self, callId, destination):
        requests.post(
            "https://config.work.oigaa.com/vtcrm/api/redirectIncoming",
            '{"callId": "' + callId + '","destination": "' + destination + '"}',
            headers={
                "content-type": "json",
                "Authorization": "VTCRM-Basic " + self.api_token,
            },
        )
