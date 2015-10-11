# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs Inc..
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
from .pkcs7 import PKCS7Encoder
from Crypto.Cipher import AES
from io import BytesIO
from datetime import timedelta
import requests
import time
import urllib
import logging


_logger = logging.getLogger(__name__)


class FaxAdapterSfax(models.Model):
    _name = 'fax.adapter.sfax'
    _description = 'SFax Adapter'
    API_ERROR_ID = -1

    @api.one
    def _compute_token(self, ):
        ''' Get security token from SFax '''
        try:
            timestr = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
            raw = 'Username=%(uname)s&ApiKey=%(key)s&GenDT=%(timestr)s&' % {
                'uname': self.username,
                'key': self.api_key,
                'timestr': timestr,
            }

            mode = AES.MODE_CBC
            encode_obj = PKCS7Encoder()
            encrypt_obj = AES.new(
                self.encrypt_key, mode, self.vector.encode('ascii')
            )
            padding = encode_obj.encode(raw)
            cipher = encrypt_obj.encrypt(padding)
            enc_cipher = cipher.encode('base64')
            _logger.debug('Got SFax token %s', enc_cipher)
            self.token = enc_cipher

        except Exception as e:
            _logger.warn(
                'Was not able to create security token. Exception: %s', e
            )
            self.token = False

    name = fields.Char(
        required=True,
        default='SFax',
    )
    company_id = fields.Many2one('res.company')
    username = fields.Char(
        required=True,
        help='SFax Username / Security Context for API connection',
    )
    encrypt_key = fields.Char(
        required=True,
        help='SFax PassKey for API connection',
    )
    vector = fields.Char(
        required=True,
        help='SFax Vector for API connection',
    )
    api_key = fields.Char(
        required=True,
        string='API Key',
        help='Key for this API connection',
    )
    uri = fields.Char(
        required=True,
        default='https://api.sfaxme.com/api',
        help='URI for API (usually don\'t want to change this)',
    )
    token = fields.Text(
        readonly=True, compute='_compute_token',
    )
    
    @api.multi
    def validate_token(self, token):
        '''
        Decrypt token and validate authenticity
        :param  token: str
        :return valid: bool
        '''
        self.ensure_one()
        mode = AES.MODE_CBC
        encode_obj = PKCS7Encoder()
        encrypt_obj = AES.new(
            self.encrypt_key, mode, self.vector.encode('ascii')
        )
        token = token.decode('base64')
        enc_cipher = encrypt_obj.decrypt(token)
        decoded = encode_obj.decode(enc_cipher)
        _logger.debug('Decoded SFax token %s', decoded)
        token_obj = {}
        for i in token.split('&'):
            try:
                k, v = i.split('=')
                token_obj[k] = v
            except ValueError:
                continue
        time_obj = time.strptime(token_obj['GenDT'], "%Y-%m-%dT%H:%M:%SZ")
        delta = time.gmtime() - time_obj
        if delta >= timedelta(minutes=15):
            _logger.debug('Token expired (Got %s, expect less than %s)',
                          delta, timedelta(minutes=15))
            return False
        if token_obj['ApiKey'] != self.api_key:
            _logger.debug('Incorrect Api key (Got %s, expect %s)',
                          token_obj['ApiKey'], self.api_key)
            return False
        if token_obj['Username'] != self.username:
            _logger.debug('Incorrect Username (Got %s, expect %s)',
                          token_obj['Username'], self.username)
            return False
        _logger.debug('Valid token!')
        return True

    @api.multi
    def __call_api(self, action, uri_params, post=None, files=None, json=True):
        '''
        Call SFax api action (/api/:action e.g /api/sendfax)
        :param  action: str Action to perform (uri part)
        :param  uri_params: dict Params to pass as GET params
        :param  post: dict Data to pass as POST
        :param  files: list of file tuples to upload. (__get_file_tuple)
        :param  json: bool Whether to decode response as json
        :return response: mixed
        '''
        self.ensure_one()
        uri = '%(uri)s/%(action)s' % {
            'uri': self.uri,
            'action': action,
        }
        params = {
            'token': self.token,
            'ApiKey': self.api_key,
        }
        params.update(uri_params)
        if post_data or files is not None:
            _logger.debug('POST to %s with params %s and files %s',
                          uri, params, files)
            resp = requests.post(
                uri,
                params=params,
                data=post_data,
                files=files,
            )
        else:
            _logger.debug('GET to %s with params %s', uri, params)
            resp = requests.get(
                uri,
                params=params
            )
        _logger.debug('Raw (%s) response: %s', resp.status_code, resp.text)
        _logger.debug('Response headers: %s', resp.headers)
        
        if not resp.ok:
            _logger.error('Received error from AP')
            return False
        
        try:
            if json:
                return resp.json()
            resp.raw.decode_content = True
            return resp.raw
        except ValueError:
            return False
    
    @api.multi
    def _send(self, dialable, payload_ids, send_name=False, ):
        '''
        Sends payload using _send on proprietary adapter
        :param  dialable: str Number to fax to (convert_to_dial_number)
        :param  payload_ids: fax.payload record(s) To Send
        :param  send_name: str Name of person to send to
        :return vals: dict To create a fax.payload.transmission
        '''
        self.ensure_one()
        images = []
        files = {}
        for payload_id in payload_ids:

            image = payload_id.image

            if payload_id.image_type != 'PDF':
                image = payload_id._convert_image(image, 'PDF', False)
            else:
                image = image.decode('base64')

            files[payload_id.name + '.pdf'] = image

        params = {
            'RecipientFax': dialable,
            'RecipientName': send_name if send_name else '',
            'OptionalParams': '',
        }

        resp = self.__call_api('SendFax', params, files=files)
        _logger.debug('Got resp %s', resp)

        state = 'transmit' if resp.get('isSuccess') else 'transmit_except'
        vals = {
            'remote_fax': dialable,
            'direction': 'out',
            'state': state,
            'status_msg': resp.get('message'),
            'timestamp': fields.Datetime.now(),
            'response_num': resp.get('SendFaxQueueId'),
            'payload_ids': [(4, p.id, 0) for p in payload_ids],
        }
        return vals

    @api.one
    def _fetch_payloads(self, transmission_ids):
        '''
        Fetches payload for transmission_ids from API
        :param  transmission_ids: fax.payload.transmissions To fetch for
        '''
        for transmission_id in transmission_ids:
    
            if transmission_id.direction == 'out':
                to = transmission_id.remote_fax
                frm = transmission_id.local_fax
                api_direction = 'outbound'
            else:
                to = transmission_id.local_fax
                frm = transmission_id.remote_fax
                api_direction = 'inbound'
    
            pdf_data = self.__call_api(
                'download%(dir)sfaxaspdf' % {'dir': api_direction},
                {'FaxID': transmission_id.response_num},
            )
    
            name = '[%(id)s] %(to)s => %(from)s' % {
                'id': transmission_id.response_num,
                'to': to,
                'from': frm,
            }
            payload_vals = {
                'image': pdf_data,
                'image_type': 'PDF',
                'name': name,
            }
    
            transmission_id.write({
                'payload_ids': (0, 0, payload_vals)
            })
