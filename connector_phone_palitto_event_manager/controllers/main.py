from odoo import http
from odoo.http import request


class PCS_VOIP(Home):

    @http.route('/web/incomingCall', type='http', auth='public', website=True, sitemap=False)
    def pcs_incoming_calls(self, *args, **kw):
        user = request.env['res.users'].search([('phone','=',kw.get('CallerID'))], limit=1)
        return request.env.incall_notify_by_login(kw.get('CallerID'), [user.login])
