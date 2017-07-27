# coding: utf-8
# Copyright 2017 OpenSynergy Indonesia <https://opensynergy-indonesia.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields

TWILIO_KEYCHAIN_NAMESPACE = "twilio_provider"


class Keychain(models.Model):
    _inherit = "keychain.account"

    namespace = fields.Selection(
        selection_add=[
            (TWILIO_KEYCHAIN_NAMESPACE, "twilio_sms"),
        ],
    )

    def _twilio_provider_init_data(self):
        return {}

    def _twilio_provider_validate_data(self, data):
        return True
