from odoo import http
from odoo.http import request


class PCS_VOIP(Home):

    def create_cdr_record(self, **kw):
        vals = {'guid' : kw.get('GUID'),
                'inbound_flag' : kw.get('Inbound'),
                'call_start_time' : kw.get('StartTime'),
                'caller_id' : kw.get('CallerID'),
                'caller_id_name' : kw.get('CalledIDName'),
                'state' : 'offering',
        }
        request.env['phone.cdr'].create(vals)
        return True

    @http.route('/web/incomingCall', type='http', auth='public', website=True, sitemap=False)
    def pcs_incoming_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        self.create_cdr_record(**kw)
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])

    @http.route('/web/Call', type='http', auth='public', website=True, sitemap=False)
    def pcs_outgoing_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        self.create_cdr_record(**kw)
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])

    @http.route('/web/missedCall', type='http', auth='public', website=True, sitemap=False)
    def pcs_missedCall_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        cdr = request.env['phone.cdr'].search([('guid', '=', kw.get('GUID'))], limit=1)
        # ToDo Calculate End time
        cdr.write({
                'state' : 'missed',
        })
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])

    @http.route('/web/Completed', type='http', auth='public', website=True, sitemap=False)
    def pcs_completed_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        cdr = request.env['phone.cdr'].search([('guid', '=', kw.get('GUID'))], limit=1)
        #ToDo - Calculate ring time & talk time
        cdr.write({
                'state' : 'completed',
        })
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])

    @http.route('/web/heldCall', type='http', auth='public', website=True, sitemap=False)
    def pcs_completed_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        cdr = request.env['phone.cdr'].search([('guid', '=', kw.get('GUID'))], limit=1)
        #ToDo - Calculate hold time
        cdr.write({
                'state' : 'on_hold',
        })
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])

    @http.route('/web/unheldCall', type='http', auth='public', website=True, sitemap=False)
    def pcs_completed_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone', '=', kw.get('CallerID'))], limit=1)
        cdr = request.env['phone.cdr'].search([('guid', '=', kw.get('GUID'))], limit=1)
        #ToDo - Calculate unheld time
        cdr.write({
                'state' : 'connected',
        })
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])
