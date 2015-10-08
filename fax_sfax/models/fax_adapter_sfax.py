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
import base64
import time
import urllib
import logging


_logger = logging.getLogger(__name__)


class FaxAdapterSfax(models.Model):
    _name = 'fax.adapter.sfax'
    _description = 'It provides bindings for SFax auth & methods'
    API_ERROR_ID = -1

    @api.one
    def _compute_token(self, ):
        ''' Get security token from SFax '''
        try:
            timestr = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            params = {
                'AppId': self.api_key,
                'AppKey': self.encrypt_key,
                'GenDT': timestr,
                'Client': self.client_ip,
            }
            raw = urllib.urlencode(params) + '&'

            mode = AES.MODE_CBC
            encode_obj = PKCS7Encoder()
            encrypt_obj = AES.new(
                self.encrypt_key, mode, self.vector.encode('ascii')
            )
            padding = encode_obj.encode(raw)
            cipher = encrypt_obj.encrypt(padding)
            enc_cipher = base64.b64encode(cipher)
            self.token = urllib.quote(enc_cipher)

        except Exception as e:
            _logger.warn(
                'Was not able to create security token. Exception: %s', e
            )
            self.token = False

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
    client_ip = fields.Char(
        required=True,
        help='Client IP for API connection',
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
    token = fields.Char(
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
        uri_params.update({
            'token': self.token,
            'ApiKey': self.api_key,
        })
        if post_data is not None or files is not None:
            _logger.debug('POST to %s with params %s', uri, uri_params)
            resp = requests.post(
                uri,
                params=uri_params,
                data=post_data,
                files=files,
            )
        else:
            _logger.debug('GET to %s with params %s', uri, uri_params)
            resp = requests.get(
                uri,
                params=uri_params
            )
        _logger.debug('Raw response: %s', resp.text)
        return resp.json()

    def __get_file_tuple(self, field_name, basename,
                         fp, content_type='application/pdf'):
        '''
        Prepare a file for upload through requests
        :param  field_name:  str Form field name
        :param  basename:    str Of file
        :param  fp:  File like object (open, StringIO, etc)
        :param  content_type: str    main and subtype (application/pdf)
        :return tuple:
        '''
        return (field_name, (basename, fp, content_type, {'Expires': '0'}))
    
    @api.multi
    def _send(self, fax_to, payload_ids, ):
        '''
        Sends fax. Designed to be overridden in submodules
        :param  fax_to: str Number to fax to
        :param  payload_ids: fax.payload record(s) To Send
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

            images.append({
                'name': payload_id.name,
                'io': BytesIO(),
            })
            images[-1]['io'].write(image)
            
        for idx, (name, io) in enumerate(images):
            images[idx] = self.__get_file_tuple(
                field_name='file',
                basename='%s.pdf' % name,
                fp=io,
            )
            
        fax_to = payload_id.convert_to_dial_number(fax_to)
        send_name = payload_id.get_name_from_phone_number(fax_to)
        params = {
            'RecipientFax': fax_to,
            'RecipientName': send_name,
        }
        resp = self.__call_api('SendFax', params, images)
        _logger.debug('Got resp %s', resp)

        vals = {
            
        }
        
        self.write({
            'transmission_ids': (0, 0, vals)
        })

    @api.model
    def _get_transmission_status(self, transmission_id, ):
        '''
        Returns xmission status and msg
        :param  transmission_id: fax.payload.transmission To Check On
        :return (transmission_status: str, status_msg: str)
        '''
        
    
