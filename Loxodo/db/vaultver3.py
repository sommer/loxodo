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

import hashlib
import struct
from hmac import HMAC
import random
import os
import tempfile
import time
import uuid

from ..twofish.twofish_ecb import TwofishECB
from ..twofish.twofish_cbc import TwofishCBC

class VaultVer3(object):
  """
    PWD database version 3 access class
  """
  def __init__ (self):
    self.db_version_tag = 'PWS3'
    self.db_end_tag = 'PWS3-EOFPWS3-EOF'
    self.db_format = 'v3'
    
    self.db_filename = None
    self.__filehandle = None
  
  def db_open(self, filename=None, mode='rb'):
    self.db_filename = filename
    if self.db_filename:
      self.__filehandle = file(filename, mode)
  
  def db_close(self):
    self.db_filename = None
    self.__filehandle.close()
  
  def db_end_data(self):
    # Write end tag only if file was opened for write.
    if self.__filehandle.mode == 'wb':
      self.__filehandle.write(self.db_end_tag)
  
  # Read length of bytes from db file version 3
  def db_read_data (self, length):
    return self.__filehandle.read(length)
  
  # Write length of bytes to db file version 3  
  def db_write_data (self, data):
    return self.__filehandle.write(data)
  
  # Test if we have correct begin tag for version 3 db
  def db_test_bg_tag (self, tag):
    if (self.db_version_tag == tag):
      return True
    else:
      return False
  
  # Test if we got correct end tag for db v3
  def db_test_end_tag (self, tag):
    if (self.db_end_tag == tag):
      return True
    else:
      return False
  
  # Read header from file to Vault
  def db_read_header(self, password, vault):
    vault.f_tag = self.__filehandle.read(4)  # TAG: magic tag
    vault.f_salt = self.__filehandle.read(32)  # SALT: SHA-256 salt
    vault.f_iter = struct.unpack("<L", self.__filehandle.read(4))[0]  # ITER: SHA-256 keystretch iterations
    vault.f_sha_ps = self.__filehandle.read(32) # H(P'): SHA-256 hash of stretched passphrase
    vault.f_b1 = self.__filehandle.read(16)  # B1
    vault.f_b2 = self.__filehandle.read(16)  # B2
    vault.f_b3 = self.__filehandle.read(16)  # B3
    vault.f_b4 = self.__filehandle.read(16)  # B4
    vault.f_iv = self.__filehandle.read(16)  # IV: initialization vector of Twofish CBC
  
  # Create empty Vault for v3 db
  def db_create_header(self, password, vault):
    vault.f_tag = self.db_version_tag
    vault.f_salt = vault.urandom(32)
    vault.f_iter = 2048
    
    stretched_password = vault._stretch_password(password, vault.f_salt, vault.f_iter)
    vault.f_sha_ps = hashlib.sha256(stretched_password).digest()
    
    cipher = TwofishECB(stretched_password)
    vault.f_b1 = cipher.encrypt(vault.urandom(16))
    vault.f_b2 = cipher.encrypt(vault.urandom(16))
    vault.f_b3 = cipher.encrypt(vault.urandom(16))
    vault.f_b4 = cipher.encrypt(vault.urandom(16))
    key_k = cipher.decrypt(vault.f_b1) + cipher.decrypt(vault.f_b2)
    key_l = cipher.decrypt(vault.f_b3) + cipher.decrypt(vault.f_b4)

    vault.f_iv = vault.urandom(16)

    hmac_checker = HMAC(key_l, "", hashlib.sha256)
    # XXX this is not needed here ?
    cipher = TwofishCBC(key_k, vault.f_iv)

    # No records yet
    vault.f_hmac = hmac_checker.digest()
    

  def db_write_header(self, vault, password):
    # FIXME: choose new SALT, B1-B4, IV values on each file write? Conflicting Specs!

    # write boilerplate
    self.__filehandle.write(vault.f_tag)
    self.__filehandle.write(vault.f_salt)
    self.__filehandle.write(struct.pack("<L", vault.f_iter))

    self.__filehandle.write(vault.f_sha_ps)

    self.__filehandle.write(vault.f_b1)
    self.__filehandle.write(vault.f_b2)
    self.__filehandle.write(vault.f_b3)
    self.__filehandle.write(vault.f_b4)

    self.__filehandle.write(vault.f_iv)
    