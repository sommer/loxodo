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
import sys

from ..twofish.twofish_ecb import TwofishECB
from ..twofish.twofish_cbc import TwofishCBC

from .vaultver4 import VaultVer4
from .vaultver3 import VaultVer3

prog_version = '1.0.0-git'
prog_name = 'Loxodo'

class Vault(object):
    """
    Represents a collection of password Records in PasswordSafe V3 format.

    The on-disk represenation of the Vault is described in the following file:
    http://passwordsafe.svn.sourceforge.net/viewvc/passwordsafe/trunk/pwsafe/pwsafe/docs/formatV3.txt?revision=2139

    Introduction of pwsafe file 4.0 version.
    
    To be able to share one file with more than one user we need to change
    database look little bit. Way how we can support more users than one is
    by using secondary passwords. During creation of database we ask
    generate master password and create db. Later we ask for secondary 
    one to encrypt master password on disk.
    
    Database with one Master password:
    TAG|SALT|ITER|H(P')|B1|B2|B3|B4|IV|HDR|R1|R2|...|Rn|EOF|HMAC
    
    During adding secondary password to database, program will ask for 
    secondary passwd and store them before Database tag. Program asks 
    for secondary password with which we encrypts master one and stores it in 
    |PTAG|MASTERPASSWORD| entry.
    
    PTAG can be one of PSTW or PSAE where
    
    PSTW means that PASSWORD is encrypted with Twofish
    PSAE means that PASSWORD is encrypted with AES
    
    Database with one secondary password:
    TAG|PTAG|MASTERPASSWORD|PTAG|MASTERPASSWORD|DTAG|SALT|ITER|H(P')|B1|B2|B3|B4|IV|HDR|R1|R2|...|Rn|EOF|HMAC
      1T         1P       2T        2P        MT
    Each couple |PTAG|MASTERPASSWORD| is encrypted by different secondary 
    password. During start application will ask for secondary password 
    and try to findout version of database.
    
    First 4bytes of db are used as DTAG for old v3 db it's PWS3 for new
    multi-password enabled db it's PWS4. Then each encryption of master 
    password is started with PTAG [PSTW, PSAE]. Then after passwords we have 
    DTAG which marks start of actuall database data for us.
    
    PWS4|PSTW|password Twofish|PSAE|password AES|PWDB|-> DATABASE
    
    """
    def __init__(self, password, filename=None, format="v3"):
        self.db_ver = None
        self.db_format = format
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
            if not os.path.isfile(filename):
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
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, 0, "")
            self.raw_fields[raw_id].raw_value = value.bytes_le
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()
        
        def _get_group(self):
            return self._group
        
        def _set_group(self, value):
            self._group = value
            raw_id = 0x02
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()
        
        def _get_title(self):
            return self._title
        
        def _set_title(self, value):
            self._title = value
            raw_id = 0x03
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()
        
        def _get_user(self):
            return self._user
        
        def _set_user(self, value):
            self._user = value
            raw_id = 0x04
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()
        
        def _get_notes(self):
            return self._notes
        
        def _set_notes(self, value):
            self._notes = value
            raw_id = 0x05
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, len(value), value)
            self.raw_fields[raw_id].raw_value = value.encode('utf_8', 'replace')
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
            self.mark_modified()
        
        def _get_passwd(self):
            return self._passwd
        
        def _set_passwd(self, value):
            self._passwd = value
            raw_id = 0x06
            if (raw_id not in self.raw_fields):
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
            if (raw_id not in self.raw_fields):
                self.raw_fields[raw_id] = Vault.Field(raw_id, 0, "0")
            self.raw_fields[raw_id].raw_value = struct.pack("<L", value)
            self.raw_fields[raw_id].raw_len = len(self.raw_fields[raw_id].raw_value)
        
        def _get_url(self):
            return self._url
        
        def _set_url(self, value):
            self._url = value
            raw_id = 0x0d
            if (raw_id not in self.raw_fields):
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
        
        def __cmp__(self, other):
            """
            Compare Based on Group, then by Title
            """
            return cmp(self._group+self._title, other._group+other._title)
        
    
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
    
    def _read_field_tlv(self, cipher):
        """
        Return one field of a vault record by reading from the given file handle.
        """
        data = self.db_ver.db_read_data(16)
        if (not data) or (len(data) < 16):
            raise self.VaultFormatError("EOF encountered when parsing record field")
        if self.db_ver.db_test_end_tag(data):
            return None
        data = cipher.decrypt(data)
        raw_len = struct.unpack("<L", data[0:4])[0]
        raw_type = struct.unpack("<B", data[4])[0]
        raw_value = data[5:]
        if (raw_len > 11):
            for dummy in range((raw_len+4)//16):
                data = self.db_ver.db_read_data(16)
                if (not data) or (len(data) < 16):
                    raise self.VaultFormatError("EOF encountered when parsing record field")
                raw_value += cipher.decrypt(data)
        raw_value = raw_value[:raw_len]
        return self.Field(raw_type, raw_len, raw_value)
    
    def urandom(self, count):
        try:
            return os.urandom(count)
        except NotImplementedError:
            retval = ""
            for dummy in range(count):
                retval += struct.pack("<B", random.randint(0, 0xFF))
            return retval
    
    def _write_field_tlv(self, cipher, field):
        """
        Write one field of a vault record using the given file handle.
        """
        assert len(field.raw_value) == field.raw_len

        raw_len = struct.pack("<L", field.raw_len)
        raw_type = struct.pack("<B", field.raw_type)
        raw_value = field.raw_value

        # Assemble TLV block and pad to 16-byte boundary
        data = raw_len + raw_type + raw_value
        if (len(data) % 16 != 0):
            pad_count = 16 - (len(data) % 16)
            data += self.urandom(pad_count)

        data = cipher.encrypt(data)

        self.db_ver.db_write_data(data)

    @staticmethod
    def create(password, filename, format="v3"):
        vault = Vault(password, filename, format)
        vault.write_to_file(filename, password)

    def _create_empty(self, password):

        assert type(password) != unicode

        if self.db_format == "v3":
          self.db_ver = VaultVer3()
        else:
          self.db_ver = VaultVer4()

        self.db_ver.db_create_header(password, self)

    def export(self, password, filename):
        #self._read_from_file(filename, password)
        print "# passwordsafe version "+self.db_format+" database"
        print "uuid,group,name,login,passwd,notes,url"
        for record in self.records:
            print "\"" + str(record.uuid) + "," + record.group + "," + record.title + "," + record.user + "," + record.passwd + "," + record.notes + "," + record.url

    def get_vault_format(self):
        return self.db_format

    def add_user_passwd(self, existing_user_password, new_user_password):
        if self.db_format != "v4":
          print "Multiple users psaswords are supported only in version 4 of vault database."
          sys.exit(2)
        self.db_ver.db_add_user(self, existing_user_password, new_user_password)
    
    def _read_from_file(self, filename, password):
        """
        Initialize all class members by loading the contents of a Vault stored in the given file.
        """
        assert type(password) != unicode

        ver3 = VaultVer3()
        ver4 = VaultVer4()

        # Read begining database tag and set db_ver db file access class
        tag = file(filename, 'rb').read(4)

        # Auto detect database type for existing vaults
        if (ver3.db_test_bg_tag(tag)):
          self.db_ver = ver3
        elif (ver4.db_test_bg_tag(tag)):
          self.db_ver = ver4
        else:
          raise self.VaultVersionError("Not a PasswordSafe V3 and V4 compatible file")

        if self.db_format != self.db_ver.db_format:
          if self.db_format == "auto":
            self.db_format = self.db_ver.db_format
          else:
            print "Database version missmatch I was asked to open database with version %s and it's a %s version" % (self.db_format, self.db_ver.db_format)
            sys.exit(1)

        # Open password database
        self.db_ver.db_open(filename)

        # Read database header to Vault class fill all required fields
        self.db_ver.db_read_header(password, self)

        # Get Stretched master password from db
        stretched_password = self.db_ver.db_get_stretched_passwd(self, password)  # P': the stretched key
        my_sha_ps = hashlib.sha256(stretched_password).digest()
        if (self.f_sha_ps != my_sha_ps):
            raise self.BadPasswordError("Wrong password")

        cipher = TwofishECB(stretched_password)
        key_k = cipher.decrypt(self.f_b1) + cipher.decrypt(self.f_b2)
        key_l = cipher.decrypt(self.f_b3) + cipher.decrypt(self.f_b4)

        hmac_checker = HMAC(key_l, "", hashlib.sha256)
        cipher = TwofishCBC(key_k, self.f_iv)

        # read header
        while (True):
            field = self._read_field_tlv(cipher)
            if not field:
                break
            if field.raw_type == 0xff:
                break
            self.header.add_raw_field(field)
            hmac_checker.update(field.raw_value)

        # read fields
        current_record = self.Record()
        while (True):
            field = self._read_field_tlv(cipher)
            if not field:
                break
            if field.raw_type == 0xff:
                self.records.append(current_record)
                current_record = self.Record()
            else:
                hmac_checker.update(field.raw_value)
                current_record.add_raw_field(field)

        # read HMAC
        self.f_hmac = self.db_ver.db_read_data(32)  # HMAC: used to verify Vault's integrity

        my_hmac = hmac_checker.digest()
        if (self.f_hmac != my_hmac):
            raise self.VaultFormatError("File integrity check failed")

        self.records.sort()

        self.db_ver.db_close()
    
    def clear_records(self):
        i = 0

        while (i < len(self.records)):
                self.records[i] = "deadbeefx0"
                i += 1

    def write_to_file(self, filename, password):
        """
        Store contents of this Vault into a file.
        """
        assert type(password) != unicode

        _last_save = struct.pack("<L", int(time.time()))
        self.header.raw_fields[0x04] = self.Field(0x04, len(_last_save), _last_save)
        _what_saved = prog_name+" "+prog_version.encode("utf_8", "replace")
        self.header.raw_fields[0x06] = self.Field(0x06, len(_what_saved), _what_saved)

        # write to temporary file first
        (osfilehandle, tmpfilename) = tempfile.mkstemp('.part', os.path.basename(filename) + ".", os.path.dirname(filename), text=False)

        self.db_ver.db_open(tmpfilename, 'wb')

        # f_sha_ps should be already defined, why we want to regen it here.
        stretched_password = self.db_ver.db_get_stretched_passwd(self, password)
        self.f_sha_ps = hashlib.sha256(stretched_password).digest()
        
        self.db_ver.db_write_header(self, password)

        cipher = TwofishECB(stretched_password)
        key_k = cipher.decrypt(self.f_b1) + cipher.decrypt(self.f_b2)
        key_l = cipher.decrypt(self.f_b3) + cipher.decrypt(self.f_b4)

        hmac_checker = HMAC(key_l, "", hashlib.sha256)
        cipher = TwofishCBC(key_k, self.f_iv)

        end_of_record = self.Field(0xff, 0, "")

        for field in self.header.raw_fields.values():
            self._write_field_tlv(cipher, field)
            hmac_checker.update(field.raw_value)
        self._write_field_tlv(cipher, end_of_record)
        hmac_checker.update(end_of_record.raw_value)

        for record in self.records:
            for field in record.raw_fields.values():
                self._write_field_tlv(cipher, field)
                hmac_checker.update(field.raw_value)
            self._write_field_tlv(cipher, end_of_record)
            hmac_checker.update(end_of_record.raw_value)

        self.db_ver.db_end_data()

        self.f_hmac = hmac_checker.digest()

        self.db_ver.db_write_data(self.f_hmac)
        self.db_ver.db_close()

        try:
            tmpvault = Vault(password, filename=tmpfilename, format=self.db_ver.db_format)
        except RuntimeError:
            os.remove(tmpfilename)
            raise self.VaultFormatError("File integrity check failed")

        # after writing the temporary file, replace the original file with it
        try:
            os.remove(filename)
        except OSError:
            pass
        os.rename(tmpfilename, filename)
