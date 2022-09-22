# -*- coding: utf:8 -*-
# © 2022 CONINPE Consultores Informaticos: Telmo Suarez Venero <tsuarez@zertek.es>
# License AGPL-3.0 or later (http://gnu.org/license/agpl.html).
import datetime
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class VozTelecomAPICallback(http.Controller):
	@http.route('/vtcrm/callback/', type='json', auth='none', methods=["POST"], csrf=False)
	def authenticate(self, *args, **post):
		response = request.jsonrequest
		_logger.info(response)
		try:
			login = request.httprequest.headers.environ['HTTP_USER']
		except KeyError:
			login = 'voztelecom'
		try:
			password = request.httprequest.headers.environ['HTTP_PASSWORD']
		except KeyError:
			password = 'voztelecom'
		try:
			db = request.httprequest.headers.environ['HTTP_DB']
		except KeyError:
			db = 'VozTelecom'
		uid = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=password)
		user = request.env(user=uid)['res.users'].browse(uid)
		if not user._mfa_url():
			http.request.session.pre_uid = uid
			http.request.session.rotate = True
			http.request.session.db = db
			http.request.session.login = login
			http.request.session.finalize()
		res = request.env['ir.http'].session_info()
		caller = request.env['res.partner'].search(['|',
													('phone_no_spaces', 'ilike', response['displayedExternalNumber']),
													('mobile_no_spaces', 'ilike', response['displayedExternalNumber'])
													])
		partner_id = request.env['res.partner'].search(['|',
														('phone', '=', response['extension']),
														('mobile', '=', response['extension'])])
		user_id = request.env['res.users'].search([('partner_id', 'in', partner_id.ids)], limit=1)
		phonecall = request.env['crm.phonecall'].search([('voz_telecom_call_id', '=', response['callId'])])
		users = request.env['res.users'].search([('partner_id', 'in', partner_id.ids)])
		if response['isIncoming'] == 'true' and response['state'] == 'ringing':
			for user in users:
				if response['isIncoming']:
					user.notify_default(
						message='Llamada entrante de ' + (caller.name or response['displayedNumber']))
				else:
					request.env.user.notify_default(
						message='Llamada entrante de ' + (caller.name or response['displayedNumber']))
				ch_name = user.name + ', ' + request.env.user.name
				ch = request.env['mail.channel'].sudo().search(['|', ('name', 'ilike', str(ch_name)),
																('name', 'ilike',
																 str(request.env.user.name + ', ' + user.name))])
				if not ch:
					ch = request.env['mail.channel'].create({
						'name': str(request.env.user.name + ', ' + user.name),
						'email_send': False,
						'channel_type': 'chat',
						'public': 'public',
						'channel_partner_ids': [(6, 0, [request.env.user.partner_id.id, user.partner_id.id])]
					})
				body = "<h2>Llamada entrante de " \
					   + (caller.name or response['displayedNumber']) + \
					   "</h2><a href='/web?#id=" + str(
					caller.id) + "&model=res.partner'> Abrir cliente</a>"
				if ch:
					ch.message_post(attachment_ids=[], body=body, content_subtype='html',
									message_type='comment', partner_ids=[], subtype_xmlid='mail.mt_comment',
									email_from=request.env.user.partner_id.email,
									author_id=request.env.user.partner_id.id)
		else:
			user_id.notify_default(
				message='Llamando a ' + (caller.name or response['displayedNumber']))

		if not phonecall and response['state'] != 'prompting':
			data = {
				'date': datetime.datetime.today(),
				'partner_id': caller.id or False,
				'name': response['displayedNumber'],
				'direction': 'in',
				'voz_telecom_call_id': response['callId'],
				'voz_telecom_state': response['state']
			}
			request.env['crm.phonecall'].create(data)
		else:
			data = {}
			if (phonecall.voz_telecom_state == 'ringing' or 'alerting') and response['state'] == 'talking':
				if response['isIncoming'] == 'true':
					for user in users:
						user.notify_default(message='Llamada de ' + (
								caller.name or response['displayedNumber']) + ' respondida por ' +
													user_id.name if user_id else response['extension'])
				else:
					user_id.notify_default(
						message='Llamada a ' + (caller.name or response['displayedNumber']) + ' establecida')
				data['user_id'] = user_id.id
				data['voz_telecom_state'] = 'talking'
			if phonecall.voz_telecom_state == 'talking' and response['state'] == 'dropped':
				user_id.notify_default(
					message='Llamada de ' + (caller.name or response['displayedNumber']) + ' finalizada')
				data['end_date'] = datetime.datetime.today()
				data['voz_telecom_state'] = 'dropped'
			phonecall.write(data)
		return response
