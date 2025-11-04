# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class SmsTemplate(models.Model):
    _name = "sms.template"
    _inherit = ["mail.template", "sms.abstract"]
    _description = "Sms Template"

    model_object_field = fields.Many2one(
        "ir.model.fields",
        string="Field",
        help="Select target field for placeholder generation",
    )
    sub_object = fields.Char(string="Sub-model", readonly=True)
    sub_model_object_field = fields.Many2one("ir.model.fields", string="Sub-field")
    null_value = fields.Char()
    copyvalue = fields.Text(string="Copy Value")
    mobile = fields.Char(required=True)
    message = fields.Text(translate=True)
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="sms_template_attachment_rel",
        column1="sms_template_id",
        column2="attachment_id",
        string="Attachments",
    )
    report_template_ids = fields.Many2many(
        "ir.actions.report",
        "sms_template_report_rel",
        "sms_template_id",
        "report_template_id",
        string="Reports to print and attach",
    )

    def get_email_template(self, res_ids):
        """Return the template mapping for backward compatibility."""
        self.ensure_one()
        # Odoo 18 already handles per-template logic.
        # For backward compatibility, return a simple mapping.
        return {res_id: self for res_id in res_ids}

    def _split_recipients_string(self, s):
        """Split a recipients string into clean items (comma/semicolon separated)."""
        if not s:
            return []
        parts = []
        for part in (p.strip() for p in s.replace(";", ",").split(",")):
            if part:
                parts.append(part)
        return parts

    def generate_recipients(self, results, template_res_ids):
        """
        Fill results[res_id]['partner_ids'] based on rendered mobile/partner_to fields.

        - Renders 'mobile' and 'partner_to'
        - Resolves corresponding res.partner records
        - Always ensures results[res_id]['partner_ids'] exists
        """
        self.ensure_one()

        # Render fields for all target records
        try:
            rendered_mobiles = self._render_field("mobile", template_res_ids)
        except Exception:
            rendered_mobiles = {}

        try:
            rendered_partner_to = self._render_field("partner_to", template_res_ids)
        except Exception:
            rendered_partner_to = {}

        Partner = self.env["res.partner"]

        for res_id in template_res_ids:
            vals = results.setdefault(res_id, {})

            # Skip if already defined
            if "partner_ids" in vals and vals["partner_ids"] is not None:
                continue

            partner_ids = []
            mobile_val = rendered_mobiles.get(res_id) or vals.get("mobile") or False
            if mobile_val:
                mobiles = self._split_recipients_string(str(mobile_val))
                for mobile_number in mobiles:
                    m_norm = mobile_number.strip()
                    if not m_norm:
                        continue
                    partner = Partner.search(
                        ["|", ("mobile", "=", m_norm), ("phone", "=", m_norm)],
                        limit=1,
                    )
                    if partner:
                        partner_ids.append(partner.id)

            partner_to_val = (
                rendered_partner_to.get(res_id) or vals.get("partner_to") or False
            )
            if partner_to_val:
                items = self._split_recipients_string(str(partner_to_val))
                for item in items:
                    item_stripped = item.strip()
                    if not item_stripped:
                        continue
                    if "@" in item_stripped:
                        partner = Partner.search(
                            [("email", "=", item_stripped)], limit=1
                        )
                    else:
                        partner = Partner.search(
                            [("name", "=", item_stripped)], limit=1
                        )
                    if partner:
                        partner_ids.append(partner.id)

            # Deduplicate partner IDs
            vals["partner_ids"] = list(dict.fromkeys(partner_ids))

        return results

    def generate_sms(self, res_ids):
        """
        Legacy-compatible SMS generation method.

        Odoo 18’s API no longer provides this exact function,
        but older modules still rely on it.
        """
        self.ensure_one()
        if isinstance(res_ids, int):
            res_ids = [res_ids]

        results = {res_id: {} for res_id in res_ids}

        # Generate recipients first
        results = self.generate_recipients(results, res_ids)

        for res_id in res_ids:
            vals = results[res_id]
            # Render the SMS message if missing
            if not vals.get("message"):
                try:
                    vals["message"] = self._render_field("message", [res_id])[res_id]
                except Exception as err:
                    raise UserError(
                        _(
                            "Error rendering SMS message for record"
                            " %(res_id)s: %(error)s"
                        )
                        % {"res_id": res_id, "error": err}
                    ) from err

            # Render the mobile field if still missing
            if not vals.get("mobile"):
                try:
                    vals["mobile"] = self._render_field("mobile", [res_id])[res_id]
                except Exception:
                    vals["mobile"] = False

            vals.setdefault("partner_ids", [])

        return results

    def send_sms(
        self, res_id, force_send=False, raise_exception=False, sms_values=None
    ):
        """Generate and send SMS messages based on the template."""
        self.ensure_one()
        generated_sms = self.generate_sms(res_id)
        sms = self.env["sms.message"].create(list(generated_sms.values()))
        if force_send:
            sms.send(raise_exception=raise_exception)
        return sms.ids

    def create_action(self):
        """Create an action button to send SMS based on the template."""
        act_window_model = self.env["ir.actions.act_window"]
        view = self.env.ref("base_sms_client.sms_compose_message_form_view")
        for template in self:
            button_name = _("Send SMS (%s)") % template.name
            action = act_window_model.create(
                {
                    "name": button_name,
                    "type": "ir.actions.act_window",
                    "res_model": "sms.compose.message",
                    "context": (
                        "{'default_template_id': %d, 'default_use_template': True}"
                        % template.id
                    ),
                    "view_mode": "form",
                    "view_id": view.id,
                    "target": "new",
                    "binding_model_id": template.model_id.id,
                }
            )
            template.write({"ref_ir_act_window": action.id})
        return True
