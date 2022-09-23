# © 2022 CONINPE Consultores Informaticos: Telmo Suarez Venero <tsuarez@zertek.es>
# License AGPL-3.0 or later (http://gnu.org/license/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("phone")
    def _compute_phone_no_spaces(self):
        for record in self:
            if record.phone:
                record.phone_no_spaces = record.phone.replace(" ", "")
            else:
                record.phone_no_spaces = False

    @api.depends("mobile")
    def _compute_mobile_no_spaces(self):
        for record in self:
            if record.mobile:
                record.mobile_no_spaces = record.mobile.replace(" ", "")
            else:
                record.mobile_no_spaces = False

    phone_no_spaces = fields.Char(compute="_compute_phone_no_spaces", store=True)
    mobile_no_spaces = fields.Char(compute="_compute_mobile_no_spaces", store=True)

    def api_phone_call(self):
        api_controller = self.env["voztelecom.config"].search([])[0]
        api_controller.api_trigger_call(
            self.env.user.phone or self.env.user.mobile, self.phone
        )

    def api_mobile_call(self):
        api_controller = self.env["voztelecom.config"].search([])[0]
        api_controller.api_trigger_call(
            self.env.user.phone or self.env.user.mobile, self.mobile
        )
