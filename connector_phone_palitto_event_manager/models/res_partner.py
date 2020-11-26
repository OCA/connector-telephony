from odoo import api, models, _
from odoo.addons.web.controllers.main import clean_action
import logging
logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def call_notification(self):
        # TODO 
        # Put the real code
        # Just to test the Incoming Pop up this method is added later will remove.
        rec = self.env['phone.common'].incall_notify_by_login(
            self.phone, [self.env.user.login])

    @api.multi
    def incoming_call_notification(self):
        action = {
            'name': _('Customer'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'target': 'new',
            'res_id': self.id
        }
        return action


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def incall_notify_by_login(self, number, login_list):
        assert isinstance(login_list, list), 'login_list must be a list'
        res = self.get_record_from_phone_number(number)
        res_id = 0
        if res:
            res_id = self.env['res.partner'].search(
                [('phone', '=', number)]).id
        users = self.env['res.users'].search(
            [('login', 'in', login_list)])
#         logger.info(
#             'Notify incoming call from number %s to user IDs %s'
#             % (number, users.ids))
        action = self._prepare_incall_pop_action(res, number)
        action = clean_action(action)
        if action:
            for user in users:
                channel = 'notify_info_%s' % user.id
                bus_message = {
                    'message': _('Incoming call : ' + user.name),
                    'title': _('Incoming call'),
                    'action': action,
                    # 'sticky': True,
                    'action_link_name': 'action_link_name',
                    'notification': 'OutGoingNotification',
                    'id': res_id,
                }

                self.sudo().env['bus.bus'].sendone(
                    channel, bus_message)
                logger.debug(
                    'This action has been sent to user ID %d: %s'
                    % (user.id, action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid
