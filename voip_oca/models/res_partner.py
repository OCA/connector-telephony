# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv import expression


class VoipOcaCall(models.Model):
    _inherit = "res.partner"

    def format_partner(self):
        return {
            "id": self.id,
            "type": "partner",
            "displayName": self.display_name,
            "email": self.email,
            "landlineNumber": self.phone,
            "mobileNumber": self.mobile,
            "name": self.name,
        }

    @api.model
    def voip_get_contacts(self, _search, offset, limit):
        domain = ["|", ("phone", "!=", False), ("mobile", "!=", False)]
        if _search:
            search_fields = ["name", "phone", "mobile", "email"]
            search_domain = expression.OR(
                [[(field, "ilike", _search)] for field in search_fields]
            )
            domain = expression.AND([domain, search_domain])
        contacts = self.search(domain, offset=offset, limit=limit)
        return [contact.format_partner() for contact in contacts]

    def get_activity_main_partner_id(self):
        """Override to return the partner itself."""
        return self
