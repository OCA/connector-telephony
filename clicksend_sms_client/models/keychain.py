# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# Valentin CHEMIERE <valentin.chemiere@akretion.com>
# Copyright (C) 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

CLICKSEND_KEYCHAIN_NAMESPACE = 'clicksend_provider'


class Keychain(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[(CLICKSEND_KEYCHAIN_NAMESPACE, 'ClickSend_sms')])

    def _clicksend_provider_init_data(self):
        return {'sms_account': ""}

    def _clicksend_provider_validate_data(self, data):
        return True
