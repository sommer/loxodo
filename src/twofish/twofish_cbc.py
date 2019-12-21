#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from . import twofish
import operator

import six

class TwofishCBC:
    """
    Cipher-block chaining (CBC) Twofish operation mode.
    """
    def __init__(self, key, init_vec=0):
        """
        Set the key to be used for en-/de-cryption and optionally specify an initialization vector (aka seed/salt).
        """
        self.twofish = twofish.Twofish()
        self.twofish.set_key(key)
        self.state = init_vec

    def encrypt(self, plaintext):
        """
        Encrypt the given string using Twofish CBC.
        """
        if len(plaintext) % 16:
            raise RuntimeError("Twofish ciphertext length must be a multiple of 16")
        ciphertext = b""
        while len(plaintext) >= 16:
            block = self.twofish.encrypt(self._xor_block(plaintext[0:16], self.state))
            ciphertext += block
            plaintext = plaintext[16:]
            self.state = block
        return ciphertext

    def decrypt(self, ciphertext):
        """
        Decrypt the given string using Twofish CBC.
        """
        if len(ciphertext) % 16:
            raise RuntimeError("Twofish ciphertext length must be a multiple of 16")
        plaintext = b""
        while len(ciphertext) >= 16:
            block = ciphertext[0:16]
            plaintext += self._xor_block(self.twofish.decrypt(block), self.state)
            ciphertext = ciphertext[16:]
            self.state = block
        return plaintext

    @staticmethod
    def _xor_block(text1, text2):
        """
        Return the bitwise xor of two arbitrary-length blocks of data
        """
        return b"".join(
                       map(
                           lambda c1, c2: six.int2byte(operator.xor(six.byte2int([c1]), six.byte2int([c2]))),
                           text1,
                           text2
                           )
                       )


def test_twofish_cbc():
    __testkey = b"Now Testing Crypto-Functions...."
    __testivc = b"Initialization V"
    __testenc = b"Passing nonsense through crypt-API, will then do assertion check"
    __testdec = b"\x38\xd1\xe3\xb1\xe6\x0d\x41\xa7\xe7\xba\xf1\xeb\x34\x4b\xc3\xdb\x88\x38\xf5\x47\x41\x15\x3f\x26\xa4\x2d\x53\xd8\xd2\x80\x25\x0a\xf3\xe4\xbe\xe4\xba\xe1\xeb\x18\x18\x66\x8a\xa6\xe2\xd0\x2b\x6e\x62\x36\x91\xf7\x72\x28\x5e\xc6\x40\x89\x70\x91\x2c\x35\x71\x39"
    assert TwofishCBC(__testkey, __testivc).decrypt(__testenc) == __testdec
    assert TwofishCBC(__testkey, __testivc).encrypt(__testdec) == __testenc


test_twofish_cbc()

