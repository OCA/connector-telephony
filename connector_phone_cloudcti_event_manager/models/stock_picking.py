import phonenumbers

from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_phone = fields.Char("Phone", related="partner_id.phone")
    partner_mobile = fields.Char("Mobile", related="partner_id.mobile")

    def cloudcti_open_outgoing_notification(self):
        called_id = self._context.get('call_no')
        caller_id = self.env.user.phone
        call_phone = self._context.get('phone_parter')
        call_mobile = self._context.get('mobile_parter')
        if caller_id and called_id and caller_id != called_id:
            phone = phonenumbers.format_number(
                phonenumbers.parse(caller_id, 'US'),
                phonenumbers.PhoneNumberFormat.NATIONAL
            )
            other = phonenumbers.format_number(
                phonenumbers.parse(called_id, 'US'),
                phonenumbers.PhoneNumberFormat.NATIONAL
            )
            partner = (
                self.env["phone.common"]
                .sudo()
                .get_record_from_phone_number(other)
            )
            self.partner_id.cloudcti_outgoing_call_notification()
            '''
            if partner:
                partner[0].sudo().called_for_phone = True if call_phone else False
                partner[0].sudo().called_for_mobile = True if call_mobile else False
                channel = "notify_info_%s" % self.env.user.id
                bus_message = {
                    "message": _("Calling from : %s" % self.env.user.phone),
                    "title": _("Outgoing Call to %s" % called_id),
                    "action_link_name": "action_link_name",
                    "Outnotification": "OutGoingNotification",
                    "id": partner[0].id,
                }
                self.env["bus.bus"].sendone(channel, bus_message)
            '''
