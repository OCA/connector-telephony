# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright: https://gist.github.com/chrix2
#
##############################################################################
import binascii
import StringIO


class PKCS7Encoder(object):

    def __init__(self, k=16):
        self.k = k

    def decode(self, text):
        '''
        Remove the PKCS#7 padding from a text string
        :param text: str The padded text for which the padding is to be
            removed.
        :exception ValueError: Raised when the input padding is
            missing/corrupt.
        '''
        nl = len(text)
        val = int(binascii.hexlify(text[-1]), 16)
        if val > self.k:
            raise ValueError('Input is not padded or padding is corrupt')

        l = nl - val
        return text[:l]

    def encode(self, text):
        '''
        Pad an input string according to PKCS#7
        :param text: str The text to encode.
        '''
        l = len(text)
        output = StringIO.StringIO()
        val = self.k - (l % self.k)
        for _ in xrange(val):
            output.write('%02x' % val)
        return text + binascii.unhexlify(output.getvalue())
