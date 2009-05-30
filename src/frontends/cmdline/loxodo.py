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

import os
import sys
import getopt
from getpass import getpass
import readline
import cmd

from ...vault import Vault

class InteractiveConsole(cmd.Cmd):
	
	def __init__(self):
		self.vault = None
		
		cmd.Cmd.__init__(self)
		if sys.platform == "darwin":
			readline.parse_and_bind('bind ^I rl_complete')
		self.intro = 'Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit.'
		self.prompt = "[none]> "

		
	def open_vault(self, fname):

		print "Opening " + fname + "..."
		try:
			passwd = getpass("Vault password: ")
		except EOFError:
			print ""
			print ""
			print "Bye."
			raise RuntimeError("No password given")
		try:
			self.vault = Vault(passwd, filename=fname)
			self.prompt = "[" + os.path.basename(fname) + "]> "
		except Vault.BadPasswordError:
			print "Bad password."
			raise
		except Vault.VaultVersionError:
			print "This is not a PasswordSafe V3 Vault."
			raise
		except Vault.VaultFormatError:
			print "Vault integrity check failed."
			raise
		print "... done."
		print ""


	def postloop(self):
		print


	def emptyline(self):
		pass


	def do_help(self, line):
		"""
		Displays this message.
		"""
		if line:
			cmd.Cmd.do_help(self, line)
			return
		
		print
		print "Commands:"
		print "  ".join(("ls", "show", "quit"))
		print

	def do_quit(self, line):
		"""
		Exits interactive mode.
		"""
		return True


	def do_EOF(self, line):
		"""
		Exits interactive mode.
		"""
		return True
	
	
	def do_ls(self, line):
		"""
		Show contents of this Vault.
		"""
		if not self.vault:
			raise RuntimeError("No vault opened")
		
		vault_records = self.vault.records[:]
		vault_records.sort(lambda e1, e2: cmp(e1.title, e2.title))

		for record in vault_records:
			print record.title.encode('utf-8', 'replace') + " [" + record.user.encode('utf-8', 'replace') + "]"
			
			
	def do_show(self, line):
		"""
		Show the specified entry (including its password).
		"""

		if not self.vault:
			raise RuntimeError("No vault opened")

		if line.startswith('"') and line.endswith('"'):
			title = line[1:-1]
		else:
			title = line
		
		matches = [record for record in self.vault.records if record.title == title]

		if not matches:
			print 'No entry found for "%s"' % title
			return

		for record in matches:
			if record.notes.strip():
				print record.notes.encode('utf-8', 'replace')
				print
			print "Title   : " + record.title.encode('utf-8', 'replace')
			print "Username: " + record.user.encode('utf-8', 'replace')
			print "Password: " + record.passwd.encode('utf-8', 'replace')
			

	def complete_show(self, text, line, begidx, endidx):
		vault_records = self.vault.records[:]
		vault_records.sort(lambda e1, e2: cmp(e1.title, e2.title))

		if text.startswith('"') and line.endswith('"'):
			text = text[1:]
		
		if not text:
			completions = [record.title for record in vault_records]
		else:
			completions = [record.title for record in vault_records if record.title.startswith(text)]

		return [['%s', '"%s"'][" " in s] % s for s in completions]


def usage():
	print
	print "Usage:"
	print "loxoxo.py Vault.psafe3"
	print "loxoxo.py --ls Vault.psafe3"
	print "loxodo.py --show Title Vault.psafe3"


def main(argv):
	try:								
		opts, args = getopt.getopt(argv, "hls:", ("help", "ls", "show="))
	except getopt.GetoptError:
		print str(err)
		usage()
		sys.exit(2)					 
	do_ls = False
	do_show = None
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-l", "--ls"):
			do_ls = True
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

	interactiveConsole = InteractiveConsole()
	interactiveConsole.open_vault(fname)
	if do_ls:
		interactiveConsole.do_ls("")
	elif do_show:
		interactiveConsole.do_show(do_show)
	else:
		interactiveConsole.cmdloop()

	sys.exit(0)
			

main(sys.argv[1:])

