# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
import time
import logging

_logger = logging.getLogger('smsclient')


class ServerAction(osv.osv):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    _columns = {
        'sms_server': fields.many2one('sms.smsclient', 'SMS Server', help='Select the SMS Gateway configuration to use with this action'),
    }

    def run(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        act_ids = []
        for action in self.browse(cr, uid, ids, context=context):
            obj_pool = self.pool.get(action.model_id.model)
            obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
            cxt = {
                'context': context,
                'object': obj,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid
            }

            expr = eval(str(action.condition), cxt)
            if not expr:
                continue

            if action.state == 'sms':
                _logger.info('send SMS')
                sms_pool = self.pool.get('sms.smsclient')
                mobile = str(action.mobile)
                to = None
                try:
                    cxt = {
                        'context': context,
                        'object': obj,
                        'gateway': action.sms_server,
                        'time': time,
                        'cr': cr,
                        'pool': self.pool,
                        'uid': uid
                    }
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')

                    text = eval(action.sms, cxt)
                    if sms_pool.send_message(cr, uid, action.sms_server.id, to, text) == True:
                        _logger.info('SMS successfully send to : %s' % (to))
                    else:
                        _logger.error('Failed to send SMS to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)

        if act_ids:
            return super(ServerAction, self).run(cr, uid, act_ids, context=context)
        return False

ServerAction()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
