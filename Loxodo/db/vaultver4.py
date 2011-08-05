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

class VaultVer4(object):
  """
    PWD database version 4 access class
  """
  def __init__ (self, filename):
    self.db_filename = filename
    self.db_version_tag = 'PWS4'
    self.db_end_tag = 'PWS4-EOFPWS4-EOF'
    self.db_ptag = ['PSTW', 'PSAE']
    self.db_dbtag = 'PWDB'
  
  def db_test_bg_tag (self, tag):
    if (self.db_version_tag == tag):
      return True
    else:
      return False
  
  