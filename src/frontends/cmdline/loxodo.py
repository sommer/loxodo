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

import sys
import getopt
from getpass import getpass

from ...vault import Vault

def usage():
	print
	print "Usage:"
	print "loxoxo.py --list Vault.psafe3"
	print "loxodo.py --show Title Vault.psafe3"

def show_entry(record):
	if record.notes.strip():
		print record.notes.encode('utf-8', 'replace')
		print
	print "Title   : " + record.title.encode('utf-8', 'replace')
	print "Username: " + record.user.encode('utf-8', 'replace')
	print "Password: " + record.passwd.encode('utf-8', 'replace')

def main(argv):
	try:								
		opts, args = getopt.getopt(argv, "hls:", ("help", "list", "show="))
	except getopt.GetoptError:
		print str(err)
		usage()
		sys.exit(2)					 
	do_list = False
	do_show = None
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-l", "--list"):
			do_list = True
		elif o in ("-s", "--show"):
			do_show = a
		else:
			assert False, "unhandled option"
	if (len(args) < 1):
		print "No Vault specified"
		usage()
		sys.exit(2)
	if (len(args) > 1):
		print "More than one Vault specified"
		usage()
		sys.exit(2)
	fname = args[0]

	passwd = None
	try:
		passwd = getpass("Vault password: ")
	except EOFError:
		print ""
		print ""
		print "Bye."
		sys.exit(0)

	print ""
	print "Opening " + fname + "..."
	vault_records = []
	try:
		vault = Vault(passwd, filename=fname)
		vault_records = vault.records[:]
		vault_records.sort(lambda e1, e2: cmp(e1.title, e2.title))
	except Vault.BadPasswordError:
		print "Bad password."
		sys.exit(1)
	except Vault.VaultVersionError:
		print "This is not a PasswordSafe V3 Vault."
		sys.exit(1)
	except Vault.VaultFormatError:
		print "Vault integrity check failed."
		sys.exit(1)
	print "... done."
	print ""

	i = 0	
	for record in vault_records:
		print "" + str(i) + ") " + record.title + " [" + record.user + "]"
		i+=1

	print ""

	inp = None
	try:
		inp = raw_input("Show which entry? ")
		print
	except EOFError:
		print ""
		print ""
		print "Bye."
		sys.exit(0)

	if not inp:
		print "Bye."
		sys.exit(0)

	inp_no = -1
	try:
		inp_no = int(inp)
	except:
		pass

	if (inp_no >= 0):
		if (inp_no >= len(vault_records)):
			print "No such entry." 
			sys.exit(2)
		show_entry(vault_records[inp_no])
		sys.exit(0)

	for record in vault_records:
		if (record.title.lower().find(inp.lower()) >= 0):
			show_entry(record)
			sys.exit(0)

	for record in vault_records:
		if (record.group.lower().find(inp.lower()) >= 0):
			show_entry(record)
			sys.exit(0)

	for record in vault_records:
		if (record.user.lower().find(inp.lower()) >= 0):
			show_entry(record)
			sys.exit(0)
			
	print "No such entry." 
	sys.exit(2)

main(sys.argv[1:])

