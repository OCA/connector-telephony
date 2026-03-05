# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class VoipOcaCall(models.Model):
    _inherit = "res.partner"

    def format_partner(self):
        return {
            "id": self.id,
            "type": "partner",
            "display_name": self.display_name,
            "email": self.email,
            "phone": self.phone,
            "name": self.name,
        }

    @api.model
    def voip_get_contacts(self, _search, offset, limit):
        domain = [("phone", "!=", False)]
        if _search:
            search_fields = ["name", "phone", "email"]
            search_domain = fields.Domain.OR(
                [[(field, "ilike", _search)] for field in search_fields]
            )
            domain = fields.Domain.AND([domain, search_domain])
        contacts = self.search(domain, offset=offset, limit=limit)
        return {"res.partner": [contact.format_partner() for contact in contacts]}

    def get_activity_main_partner_id(self):
        """Override to return the partner itself."""
        return self
