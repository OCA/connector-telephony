# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

OVH_KEYCHAIN_NAMESPACE = 'ovh_provider'


class Keychain(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[(OVH_KEYCHAIN_NAMESPACE, 'Ovh_sms')])

    def _ovh_provider_init_data(self):
        return {'sms_account': ""}

    def _ovh_provider_validate_data(self, data):
        return True
