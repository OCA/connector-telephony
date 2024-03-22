import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = "phone.common"

    def get_record_from_phone_number(self, presented_number):
        _logger.debug(
            "Call get_name_from_phone_number with number = %s" % presented_number
        )
        if not isinstance(presented_number, str):
            _logger.warning(
                "Number '%s' should be a 'str' but it is a '%s'"
                % (presented_number, type(presented_number))
            )
            return False
        if not presented_number.isdigit():
            _logger.warning(
                "Number '%s' should only contain digits." % presented_number
            )

        nr_digits_to_match_from_end = (
            self.env.user.company_id.number_of_digits_to_match_from_end
        )
        partners = []
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[
                -nr_digits_to_match_from_end : len(presented_number)
            ]
            partners = (
                self.env["res.partner"]
                .sudo()
                .search(
                    [
                        "|",
                        ("phone", "ilike", end_number_to_match),
                        ("mobile", "ilike", end_number_to_match),
                    ]
                )
            )
        return partners

    def incall_notify_by_login_test(self, number, login_list):
        self.incall_notify_by_login("(582) 126-8105", ["admin"])

    @api.model
    def incall_notify_by_login(self, number, login_list, calltype="Incoming Call"):
        assert isinstance(login_list, list), "login_list must be a list"
        partners = self.sudo().get_record_from_phone_number(number)
        response = False
        if partners:
            user = self.env["res.users"].sudo().search([("login", "in", login_list)])
            if len(partners.ids) > 1:
                name = "Multiple Records"
            else:
                name = partners[0].name
            channel = "notify_info_%s" % user.id
            bus_message = {
                "message": _(calltype + " from : " + name),
                "title": _(calltype),
                "action_link_name": "action_link_name",
                "notification": "IncomingNotification",
                "id": partners.ids,
            }
            self.sudo().env["bus.bus"].sendone(channel, bus_message)
            _logger.debug("This action has been sent to user ID %d" % (user.id))
            response = partners[0].name
        return response
