# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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
    transmission_ids = fields.Many2many(
        'fax.payload.transmission'
    )
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
    def __call_api(self, action, uri_params, post_data=None, files=None):
        '''
        Call SFax api action (/api/:action e.g /api/sendfax)
        :param  action: str Action to perform (uri part)
        :param  uri_params: dict Params to pass as GET params
        :param  post_data: dict Data to pass as POST
        :param  files: list of file tuples to upload. (__get_file_tuple)
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
        if post_data is not None or files is not None:
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
        try:
            return resp.json()
        except ValueError:
            return False

    def __get_file_tuple(self, basename, fp, content_type='application/pdf'):
        '''
        Prepare a file for upload through requests
        :param  field_name:  str Form field name
        :param  basename:    str Of file
        :param  fp:  File like object (open, StringIO, etc)
        :param  content_type: str    main and subtype (application/pdf)
        :return tuple:
        '''
        return (basename, fp, content_type, {'Expires': '0'})
    
    @api.multi
    def _send(self, dialable, payload_ids, send_name=False, ):
        '''
        Sends payload using _send on proprietary adapter
        :param  dialable: str Number to fax to (convert_to_dial_number)
        :param  payload_ids: fax.payload record(s) To Send
        :param  send_name: str Name of person to send to
        :return fax.payload.transmission: Representing fax transmission
        '''
        self.ensure_one()
        images = []
        for payload_id in payload_ids:

            image = payload_id.image

            if payload_id.image_type != 'PDF':
                image = payload_id._convert_image(image, 'PDF', False)
            else:
                image = image.decode('base64')

            images.append([
                payload_id.name,
                BytesIO(),
            ])
            images[-1][1].write(image)
            
        for idx, (name, io) in enumerate(images):
            images[idx] = self.__get_file_tuple(
                basename='%s.pdf' % name,
                fp=io,
            )

        params = {
            'RecipientFax': dialable,
            'RecipientName': send_name if send_name else '',
        }

        for image in images:
            resp = self.__call_api('SendFax', params, files={
                'file': image
            })
            _logger.debug('Got resp %s', resp)

            state = 'transmit' if resp.get('isSuccess') else 'transmit_except'
            vals = {
                'remote_fax': dialable,
                'direction': 'out',
                'state': state,
                'status_msg': resp.get('message'),
                'timestamp': fields.Datetime.now(),
                'response_num': resp.get('SendFaxQueueId'),
                'payload_id': payload_id.id,
            }
            
            self.write({
                'transmission_ids': (0, 0, vals)
            })
            
            if not resp.get('isSuccess'):
                raise IOError("Fax transmission failure. Got resp %s", resp)

    @api.model
    def _get_transmission_status(self, transmission_id, ):
        '''
        Returns xmission status and msg
        :param  transmission_id: fax.payload.transmission To Check On
        :return (transmission_status: str, status_msg: str)
        '''
        pass
    
