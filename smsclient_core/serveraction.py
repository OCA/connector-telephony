# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
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

from openerp import models, fields, api
import time
import logging
import urllib

_logger = logging.getLogger('smsclient')


class ServerAction(models.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    mobile = fields.Char('Mobile No', size=512, help="Provides fields that "
                         "be used to fetch the mobile number, e.g. you select"
                         " the invoice, then "
                         "`object.invoice_address_id.mobile` is the field "
                         "which gives the correct mobile number")
    sms = fields.Char('SMS', size=160, translate=True)
    sms_server = fields.Many2one('sms.smsclient', 'SMS Server',
                                 help='Select the SMS Gateway configuration'
                                 ' to use with this action')
    sms_template_id = fields.Many2one('email.template', 'SMS Template',
                                      help='Select the SMS Template'
                                      ' configuration to use with this action')

    @api.model
    def _get_states(self):
        """ Override me in order to add new states in the server action. Please
        note that the added key length should not be higher than
        already-existing ones. """
        states = super(ServerAction, self)._get_states()
        states.append(('sms', 'SMS'))
        return states

    @api.multi
    def run(self):
        act_ids = []
        for action in self:
            obj_pool = self.env[action.model_id.model]
            obj = obj_pool.browse(self._context['active_id'])
            email_template_obj = self.env['email.template']
            cxt = {
                'context': self._context,
                'object': obj,
                'time': time,
                'cr': self.env.cr,
                'pool': self.pool,
                'uid': self.env.uid
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue
            if action.state == 'sms':
                _logger.info('Send SMS')
                queue_obj = self.env['sms.smsclient.queue']
                mobile = str(action.mobile)
                to = None
                try:
                    cxt.update({'gateway': action.sms_server})
                    gateway = action.sms_template_id.gateway_id
                    if mobile:
                        to = action.mobile
                    else:
                        _logger.error('Mobile number not specified !')
                    res_id = self._context['active_id']
                    template = email_template_obj.get_email_template(
                        action.sms_template_id.id, res_id)
                    values = {}
                    for field in ['subject', 'body_html', 'email_from',
                                  'email_to', 'email_cc', 'reply_to']:
                        values[field] = email_template_obj.render_template(
                            getattr(template, field),
                            template.model, res_id) \
                            or False

                    name = gateway.url
                    if gateway.method == 'http':
                        prms = {}
                        for p in gateway.property_ids:
                            if p.type == 'user':
                                prms[p.name] = p.value
                            elif p.type == 'password':
                                prms[p.name] = p.value
                            elif p.type == 'to':
                                prms[p.name] = to
                            elif p.type == 'sms':
                                prms[p.name] = values['body_html']
                            elif p.type == 'extra':
                                prms[p.name] = p.value
                        params = urllib.urlencode(prms)
                        name = gateway.url + "?" + params
                    vals = {
                        'name': name,
                        'gateway_id': gateway.id,
                        'state': 'draft',
                        'mobile': to,
                        'msg': values['body_html'],
                        'validity': gateway.validity,
                        'classes': gateway.classes,
                        'deferred': gateway.deferred,
                        'priority': gateway.priority,
                        'coding': gateway.coding,
                        'tag': gateway.tag,
                        'nostop': gateway.nostop,
                    }
                    sms_in_q = queue_obj.search([
                        ('name', '=', gateway.url),
                        ('gateway_id', '=', gateway.id),
                        ('state', '=', 'draft'),
                        ('mobile', '=', to),
                        ('msg', '=', values['body_html']),
                        ('validity', '=', gateway.validity),
                        ('classes', '=', gateway.classes),
                        ('deferred', '=', gateway.deferred),
                        ('priority', '=', gateway.priority),
                        ('coding', '=', gateway.coding),
                        ('tag', '=', gateway.tag),
                        ('nostop', '=', gateway.nostop)
                        ])
                    print sms_in_q
                    if not sms_in_q:
                        queue_obj.create(vals)
                        _logger.info('SMS successfully send to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)
        if act_ids:
            return super(ServerAction, self).run()
        return False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
