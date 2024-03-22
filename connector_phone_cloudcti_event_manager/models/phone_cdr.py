import phonenumbers

from odoo import _, api, models

class PhoneCDR(models.Model):
    _inherit = "phone.cdr"

    def cloudcti_open_outgoing_notification(self):
        called_id = self._context.get('call_no')
        caller_id = self.env.user.phone
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
            # if len(self.partner_ids):
            #     self.partner_ids[0].cloudcti_outgoing_call_notification()
            if self.partner_id:
                self.partner_id.cloudcti_outgoing_call_notification()
            '''
            if partner:
                partner[0].sudo().called_for_phone = True
                partner[0].sudo().called_for_mobile = False
                channel = "notify_info_%s" % self.env.user.id
                bus_message = {
                    "message": _("Calling from : %s" % self.env.user.phone),
                    "title": _("Outgoing Call to %s" % called_id),
                    "action_link_name": "action_link_name",
                    "Outnotification": "OutGoingNotification",
                    "id": self.id,
                }
                self.env["bus.bus"].sendone(channel, bus_message)
            '''
