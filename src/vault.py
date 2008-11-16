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

from .twofish.twofish_ecb import TwofishECB
from .twofish.twofish_cbc import TwofishCBC

class Vault(object):

    """
    Represents a collection of password Records in PasswordSafe V3 format.

    The on-disk represenation of the Vault is described in the following file:
    http://passwordsafe.svn.sourceforge.net/viewvc/passwordsafe/trunk/pwsafe/pwsafe/docs/formatV3.txt?revision=2139
    """

    def __init__(self, password, filename=None):
        self.f_tag = None
        self.f_salt = None
        self.f_iter = None
        self.f_sha_ps = None
        self.f_b1 = None
        self.f_b2 = None
        self.f_b3 = None
        self.f_b4 = None
        self.f_iv = None
        self.f_hmac = None
        self.header = self.Header()
        self.records = []
        if not filename:
            self._create_empty(password)
        else:
            self._read_from_file(filename, password)

    class BadPasswordError(RuntimeError):
        pass

    class VaultFormatError(RuntimeError):
        pass

    class VaultVersionError(VaultFormatError):
        pass

    class Field(object):

        """
        Contains the raw, on-disk representation of a record's field.
        """

        def __init__(self, raw_type, raw_len, raw_value):
            self.raw_type = raw_type
            self.raw_len = raw_len
            self.raw_value = raw_value
            
        def is_equal(self, field):
            """
            Return True if this Field and the given one are of the same type and both contain the same value.
            """
            return self.raw_type == field.raw_type and self.raw_value == field.raw_value

    class Header(object):

        """
        Contains the fields of a Vault header.
        """

        def __init__(self):
            self.raw_fields = {}

        def add_raw_field(self, raw_field):
            self.raw_fields[raw_field.raw_type] = raw_field

    class Record(object):

        """
        Contains the fields of an individual password record.
        """

        def __init__(self):
            self.raw_fields = {}
            self._uuid = None
            self._group = ""
            self._title = ""
            self._user = ""
            self._notes = ""
            self._passwd = ""
            self._last_mod = 0
            self._url = ""
            
        @staticmethod
        def create():
            record = Vault.Record()
            record.uuid = uuid.uuid4()
            record.last_mod = int(time.time())
            return record

        def add_raw_field(self, raw_field):
            self.raw_fields[raw_field.raw_type] = raw_field
            if (raw_field.raw_type == 0x01):
                self._uuid = uuid.UUID(bytes_le=raw_field.raw_value)
            if (raw_field.raw_type == 0x02):
                self._group = raw_field.raw_value.decode('utf_8', 'replace')
            if (raw_field.raw_type == 0x03):
                self._title = raw_field.raw_value.decode('utf_8', 'replace')
            if (raw_field.raw_type == 0x04):
                self._user = raw_field.raw_value.decode('utf_8', 'replace')
            if (raw_field.raw_type == 0x05):
                self._notes = raw_field.raw_value.decode('utf_8', 'replace')
            if (raw_field.raw_type == 0x06):
                self._passwd = raw_field.raw_value.decode('utf_8', 'replace')
            if ((raw_field.raw_type == 0x0c) and (raw_field.raw_len == 4)):
                self._last_mod = struct.unpack("<L", raw_field.raw_value)[0]
            if (raw_field.raw_type == 0x0d):
                self._url = raw_field.raw_value.decode('utf_8', 'replace')

        def mark_modified(self):
            self.last_mod = int(time.time())

        # TODO: refactor Record._set_xyz methods to be less repetitive

        def _get_uuid(self):
            return self._uuid

        def _set_uuid(self, value):
            self._uuid = value
            raw_id = 0x01
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, 0, "")
            self.raw_fields[raw_id].raw_value = value.bytes_le
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_group(self):
            return self._group

        def _set_group(self, value):
            self._group = value
            raw_id = 0x02
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_title(self):
            return self._title

        def _set_title(self, value):
            self._title = value
            raw_id = 0x03
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_user(self):
            return self._user

        def _set_user(self, value):
            self._user = value
            raw_id = 0x04
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_notes(self):
            return self._notes

        def _set_notes(self, value):
            self._notes = value
            raw_id = 0x05
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_passwd(self):
            return self._passwd

        def _set_passwd(self, value):
            self._passwd = value
            raw_id = 0x06
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def _get_last_mod(self):
            return self._last_mod

        def _set_last_mod(self, value):
            assert type(value) == int
            self._last_mod = value
            raw_id = 0x0c
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, 0, "0")
            self.raw_fields[raw_id].raw_value = struct.pack("<L", value)
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)

        def _get_url(self):
            return self._url

        def _set_url(self, value):
            self._url = value
            raw_id = 0x0d
            if (not self.raw_fields.has_key(raw_id)):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()

        def is_corresponding(self, record):
            """
            Return True if Records are the same, based on either UUIDs (if available) or title 
            """
            if not self.uuid or not record.uuid:
                return self.title == record.title
            return self.uuid == record.uuid
                    
        def is_newer_than(self, record):
            """
            Return True if this Record's last modifed date is later than the given one's.
            """
            return self.last_mod > record.last_mod

        def merge(self, record):
            """
            Merge in fields from another Record, replacing existing ones
            """
            self.raw_fields = {}
            for field in record.raw_fields.values():
                self.add_raw_field(field)


        uuid = property(_get_uuid, _set_uuid)
        group = property(_get_group, _set_group)
        title = property(_get_title, _set_title)
        user = property(_get_user, _set_user)
        notes = property(_get_notes, _set_notes)
        passwd = property(_get_passwd, _set_passwd)
        last_mod = property(_get_last_mod, _set_last_mod)
        url = property(_get_url, _set_url)

    @staticmethod
    def _stretch_password(password, salt, iterations):
        """
        Generate the SHA-256 value of a password after several rounds of stretching.

        The algorithm is described in the following paper:
        [KEYSTRETCH Section 4.1] http://www.schneier.com/paper-low-entropy.pdf
        """
        sha = hashlib.sha256()
        sha.update(password)
        sha.update(salt)
        stretched_password = sha.digest()
        for dummy in range(iterations):
            stretched_password = hashlib.sha256(stretched_password).digest()
        return stretched_password

    def _read_field_tlv(self, filehandle, cipher):
        """
        Return one field of a vault record by reading from the given file handle.
        """
        data = filehandle.read(16)
        if (not data) or (len(data) < 16):
            raise self.VaultFormatError("EOF encountered when parsing record field")
        if data == "PWS3-EOFPWS3-EOF":
            return None
        data = cipher.decrypt(data)
        raw_len = struct.unpack("<L", data[0:4])[0]
        raw_type = struct.unpack("<B", data[4])[0]
        raw_value = data[5:]
        if (raw_len > 11):
            for dummy in range((raw_len+4)//16):
                data = filehandle.read(16)
                if (not data) or (len(data) < 16):
                    raise self.VaultFormatError("EOF encountered when parsing record field")
                raw_value += cipher.decrypt(data)
        raw_value = raw_value[:raw_len]
        return self.Field(raw_type, raw_len, raw_value)

    @staticmethod
    def _urandom(count):
        try:
            return os.urandom(count)
        except NotImplementedError:
            retval = ""
            for dummy in range(count):
                retval += struct.pack("<B", random.randint(0, 0xFF))
            return retval

    def _write_field_tlv(self, filehandle, cipher, field):
        """
        Write one field of a vault record using the given file handle.
        """
        if (field is None):
            filehandle.write("PWS3-EOFPWS3-EOF")
            return

        assert len(field.raw_value) == field.raw_len

        raw_len = struct.pack("<L", field.raw_len)
        raw_type = struct.pack("<B", field.raw_type)
        raw_value = field.raw_value

        # Assemble TLV block and pad to 16-byte boundary
        data = raw_len + raw_type + raw_value
        if (len(data) % 16 != 0):
            pad_count = 16 - (len(data) % 16)
            data += self._urandom(pad_count)

        data = cipher.encrypt(data)

        filehandle.write(data)

    @staticmethod
    def create(password, filename):
        vault = Vault(password)
        vault.write_to_file(filename, password)
        pass

    def _create_empty(self, password):
        
        assert type(password) != unicode

        self.f_tag = 'PWS3'
        self.f_salt = Vault._urandom(32)
        self.f_iter = 2048
        stretched_password = self._stretch_password(password, self.f_salt, self.f_iter)
        self.f_sha_ps = hashlib.sha256(stretched_password).digest()

        cipher = TwofishECB(stretched_password)
        self.f_b1 = cipher.encrypt(Vault._urandom(16))
        self.f_b2 = cipher.encrypt(Vault._urandom(16))
        self.f_b3 = cipher.encrypt(Vault._urandom(16))
        self.f_b4 = cipher.encrypt(Vault._urandom(16))
        key_k = cipher.decrypt(self.f_b1) + cipher.decrypt(self.f_b2)
        key_l = cipher.decrypt(self.f_b3) + cipher.decrypt(self.f_b4)

        self.f_iv = Vault._urandom(16)
        
        hmac_checker = HMAC(key_l, "", hashlib.sha256)
        cipher = TwofishCBC(key_k, self.f_iv)

        # No records yet

        self.f_hmac = hmac_checker.digest()

    def _read_from_file(self, filename, password):
        """
        Initialize all class members by loading the contents of a Vault stored in the given file.
        """

        assert type(password) != unicode
        
        filehandle = file(filename, 'rb')

        # read boilerplate

        self.f_tag = filehandle.read(4)  # TAG: magic tag
        if (self.f_tag != 'PWS3'):
            raise self.VaultVersionError("Not a PasswordSafe V3 file")

        self.f_salt = filehandle.read(32)  # SALT: SHA-256 salt
        self.f_iter = struct.unpack("<L", filehandle.read(4))[0]  # ITER: SHA-256 keystretch iterations
        stretched_password = self._stretch_password(password, self.f_salt, self.f_iter)  # P': the stretched key
        my_sha_ps = hashlib.sha256(stretched_password).digest()

        self.f_sha_ps = filehandle.read(32) # H(P'): SHA-256 hash of stretched passphrase
        if (self.f_sha_ps != my_sha_ps):
            raise self.BadPasswordError("Wrong password")

        self.f_b1 = filehandle.read(16)  # B1
        self.f_b2 = filehandle.read(16)  # B2
        self.f_b3 = filehandle.read(16)  # B3
        self.f_b4 = filehandle.read(16)  # B4

        cipher = TwofishECB(stretched_password)
        key_k = cipher.decrypt(self.f_b1) + cipher.decrypt(self.f_b2)
        key_l = cipher.decrypt(self.f_b3) + cipher.decrypt(self.f_b4)

        self.f_iv = filehandle.read(16)  # IV: initialization vector of Twofish CBC

        hmac_checker = HMAC(key_l, "", hashlib.sha256)
        cipher = TwofishCBC(key_k, self.f_iv)

        # read header

        while (True):
            field = self._read_field_tlv(filehandle, cipher)
            if not field:
                break
            if field.raw_type == 0xff:
                break
            self.header.add_raw_field(field)
            hmac_checker.update(field.raw_value)

        # read fields

        current_record = self.Record()
        while (True):
            field = self._read_field_tlv(filehandle, cipher)
            if not field:
                break
            if field.raw_type == 0xff:
                self.records.append(current_record)
                current_record = self.Record()
            else:
                hmac_checker.update(field.raw_value)
                current_record.add_raw_field(field)


        # read HMAC

        self.f_hmac = filehandle.read(32)  # HMAC: used to verify Vault's integrity

        my_hmac = hmac_checker.digest()
        if (self.f_hmac != my_hmac):
            raise self.VaultFormatError("File integrity check failed")

        filehandle.close()

    def write_to_file(self, filename, password):
        """
        Store contents of this Vault into a file.
        """

        assert type(password) != unicode
        
        _last_save = struct.pack("<L", int(time.time()))
        self.header.raw_fields[0x04] = self.Field(0x04, len(_last_save), _last_save)
        _what_saved = "Loxodo 0.0-git".encode("utf_8", "replace")
        self.header.raw_fields[0x06] = self.Field(0x06, len(_what_saved), _what_saved)

        # write to temporary file first
        (osfilehandle, tmpfilename) = tempfile.mkstemp('.part', os.path.basename(filename) + ".", os.path.dirname(filename), text=False)
        filehandle = os.fdopen(osfilehandle, "wb")

        # FIXME: choose new SALT, B1-B4, IV values on each file write? Conflicting Specs!

        # write boilerplate

        filehandle.write(self.f_tag)
        filehandle.write(self.f_salt)
        filehandle.write(struct.pack("<L", self.f_iter))

        stretched_password = self._stretch_password(password, self.f_salt, self.f_iter)
        self.f_sha_ps = hashlib.sha256(stretched_password).digest()
        filehandle.write(self.f_sha_ps)

        filehandle.write(self.f_b1)
        filehandle.write(self.f_b2)
        filehandle.write(self.f_b3)
        filehandle.write(self.f_b4)

        cipher = TwofishECB(stretched_password)
        key_k = cipher.decrypt(self.f_b1) + cipher.decrypt(self.f_b2)
        key_l = cipher.decrypt(self.f_b3) + cipher.decrypt(self.f_b4)

        filehandle.write(self.f_iv)

        hmac_checker = HMAC(key_l, "", hashlib.sha256)
        cipher = TwofishCBC(key_k, self.f_iv)

        end_of_record = self.Field(0xff, 0, "")

        for field in self.header.raw_fields.values():
            self._write_field_tlv(filehandle, cipher, field)
            hmac_checker.update(field.raw_value)
        self._write_field_tlv(filehandle, cipher, end_of_record)
        hmac_checker.update(end_of_record.raw_value)

        for record in self.records:
            for field in record.raw_fields.values():
                self._write_field_tlv(filehandle, cipher, field)
                hmac_checker.update(field.raw_value)
            self._write_field_tlv(filehandle, cipher, end_of_record)
            hmac_checker.update(end_of_record.raw_value)

        self._write_field_tlv(filehandle, cipher, None)

        self.f_hmac = hmac_checker.digest()
        filehandle.write(self.f_hmac)
        filehandle.close()

        try:
            tmpvault = Vault(password, filename=tmpfilename)
        except RuntimeError:
            os.remove(tmpfilename)
            raise self.VaultFormatError("File integrity check failed")

        # after writing the temporary file, replace the original file with it
        try:
            os.remove(filename)
        except OSError:
            pass
        os.rename(tmpfilename, filename)
