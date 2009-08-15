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
from optparse import OptionParser
from getpass import getpass
import readline
import cmd
import re

from ...vault import Vault
from ...config import config

class InteractiveConsole(cmd.Cmd):
	
	def __init__(self):
		self.vault = None
		self.vault_file_name = None
		self.vault_password = None
		
		cmd.Cmd.__init__(self)
		if sys.platform == "darwin":
			readline.parse_and_bind('bind ^I rl_complete')
		self.intro = 'Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit.'
		self.prompt = "[none]> "

		
	def open_vault(self):

		print "Opening " + self.vault_file_name + "..."
		try:
			self.vault_password = getpass("Vault password: ")
		except EOFError:
			print ""
			print ""
			print "Bye."
			raise RuntimeError("No password given")
		try:
			self.vault = Vault(self.vault_password, filename=self.vault_file_name)
			self.prompt = "[" + os.path.basename(self.vault_file_name) + "]> "
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
		Show contents of this Vault. If an argument is added a case insensitive
		search of titles is done, entries can also be specified as regular expressions.
		"""
		if not self.vault:
			raise RuntimeError("No vault opened")
	
		if line != None:
			vault_records = self.find_titles(line)
		else:
			vault_records = self.vault.records[:]
			vault_records.sort(lambda e1, e2: cmp(e1.title, e2.title))

		if vault_records == None:
			print "No matches found."
			return

		for record in vault_records:
			print record.title.encode('utf-8', 'replace') + " [" + record.user.encode('utf-8', 'replace') + "]"
			
	def do_show(self, line):
		"""
		Show the specified entry (including its password).
		A case insenstive search of titles is done, entries can also be specified as regular expressions.
		"""

		if not self.vault:
			raise RuntimeError("No vault opened")

		matches = self.find_titles(line)

		if matches == None:
			print 'No entry found for "%s"' % line
			return

		for record in matches:
			if record.notes.strip():
				print record.notes.encode('utf-8', 'replace')
				print
			print "\nTitle   : " + record.title.encode('utf-8', 'replace')
			print "Username: " + record.user.encode('utf-8', 'replace')
			print "Password: " + record.passwd.encode('utf-8', 'replace')
			

	def complete_show(self, text, line, begidx, endidx):
	
		if not text:
			completions = [record.title for record in self.vault.records]
		else:
			fulltext = line[5:]
			lastspace = fulltext.rfind(' ')
			if lastspace == -1:
				completions = [record.title for record in self.vault.records if record.title.upper().startswith(text.upper())]
			else:
				completions = [record.title[lastspace+1:] for record in self.vault.records if record.title.upper().startswith(fulltext.upper())]

		completions.sort(lambda e1, e2: cmp(e1.title, e2.title))
		return completions

	def find_titles(self, regexp):
		"Finds titles matching a regular expression. (Case insensitive)"
		matches = []
		pat = re.compile(regexp, re.IGNORECASE)
		for record in self.vault.records:
			if pat.match(record.title) != None:
				matches.append(record)

		if len(matches) == 0:
			return None
		else:
			return matches


def main(argv):

	# Options
	usage = "usage: %prog [options] [Vault.psafe3]"
	parser = OptionParser(usage=usage)
	parser.add_option("-l", "--ls", dest="do_ls", default=False, action="store_true", help="list contents of vault")
	parser.add_option("-s", "--show", dest="do_show", default=None, action="store", type="string", help="show entries matching REGEX", metavar="REGEX")
	parser.add_option("-i", "--interactive", dest="interactive", default=False, action="store_true", help="use command line interface")
	(options, args) = parser.parse_args()

	interactiveConsole = InteractiveConsole()

	if (len(args) < 1):
		if (config.recentvaults):
			interactiveConsole.vault_file_name = config.recentvaults[0]
			print "No Vault specified, using " + interactiveConsole.vault_file_name
		else:
			print "No Vault specified, and none found in config."
			sys.exit(2)
	elif (len(args) > 1):
		print "More than one Vault specified"
		sys.exit(2)
	else:
		interactiveConsole.vault_file_name = args[0]

	interactiveConsole.open_vault()
	if options.do_ls:
		interactiveConsole.do_ls("")
	elif options.do_show:
		interactiveConsole.do_show(options.do_show)
	else:
		interactiveConsole.cmdloop()

	sys.exit(0)
			

main(sys.argv[1:])

