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
import getpass
import readline
import cmd
import re
import time

from ...db.vault import Vault
from ...config import config

class InteractiveConsole(cmd.Cmd):

    def __init__(self):
        self.vault = None
        self.vault_file_name = None
        self.vault_password = None
        self.vault_modified = False
        self.vault_status = ""
        self.vault_format = "v3"

        self.vi = False
        self.tabcomp = True
        self.echo = False
        self.mod = False
        # options for sorting are 'alpha' and 'mod'
        self.sort_key = 'alpha'
        # options are brief or verbose
        self.output = 'brief'

        cmd.Cmd.__init__(self)
        if sys.platform == "darwin":
            readline.parse_and_bind('bind ^I rl_complete')
        self.intro = 'Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit. Database format is: '
        self.prompt = "[none]> "

    def create_vault(self):
        print "Creating " + self.vault_file_name + "..."
        try:
            self.vault_password = getpass.getpass("Vault password: ")
        except EOFError:
            print "\n\nBye."
            raise RuntimeError("No password given")

        Vault.create(self.vault_password, filename=self.vault_file_name, format=self.vault_format)
        print "... Done.\n"

    def set_prompt(self):
        if self.vault_modified:
            self.vault_status = "*"
        else:
            self.vault_status = ""
        self.prompt = "[%s%s]> " % (os.path.basename(self.vault_file_name), self.vault_status)

    def open_vault(self):
        vault_action = "Opening"
        if not os.path.isfile(self.vault_file_name):
            vault_action = "Creating"
        print "%s %s ..." % (vault_action, self.vault_file_name)
        try:
            self.vault_password = getpass.getpass("Vault password: ")
            if self.vault_password == "":
                raise EOFError
        except EOFError:
            print "\n\nBye."
            raise RuntimeError("No password given")
        try:
            self.vault = Vault(self.vault_password, filename=self.vault_file_name, format=self.vault_format)
        except Vault.BadPasswordError:
            print "Bad password."
            raise
        except Vault.VaultVersionError:
            print "This is not a PasswordSafe V3 or V4 Vault."
            raise
        except Vault.VaultFormatError:
            print "Vault integrity check failed."
            raise
        print "... Done.\n"

    def postloop(self):
        print

    def postcmd(self, stop, line):
        if stop == True:
            return True

        self.set_prompt()

    def emptyline(self):
        pass

    def do_password(self):
      if not self.vault:
        raise RuntimeError("No vault opened")

      new_user_password = getpass.getpass("New User Vault password: ")
      self.vault.add_user_passwd(self.vault_password, new_user_password)
      self.vault.write_to_file(self.vault_file_name, self.vault_password)

    def do_help(self, line):
        """
        Displays this message.
        """
        if line:
            cmd.Cmd.do_help(self, line)
            return

        print "\nCommands:"
        print "  ".join(("ls", "show", 'add', 'mod', 'del', "save", 'quit', 'echo', 'sort', 'output', 'uuid', 'vi', 'tab', 'export'))
        print
        print "echo is %s" % self.echo
        print "uuid is %s" % self.uuid
        print "sort is %s" % self.sort_key
        print "output is %s" % self.output
        print
        print "vi editing mode is %s" % self.vi
        print "tab completition is %s" % self.tabcomp
        print
        print "Database format is set to %s" % self.vault_format

    # This method should clear all data in self.vault.records because we
    # can't control when will this be Garbadge collected we replace it
    # for strange text
    def clear_vault(self):
        self.vault.clear_records()

    def do_quit(self, line):
        """
        Exits interactive mode.
        """
        self.do_save()
        self.clear_vault()
        return True

    def do_save(self, line=None):
        """
        Save the vault without exiting.
        """
        if self.vault_modified and self.vault_file_name and self.vault_password:
            self.vault.write_to_file(self.vault_file_name, self.vault_password)
            self.vault_modified = False
            print "Changes Saved"

    def do_EOF(self, line):
        """
        Exits interactive mode.
        """
        return True

    def do_add(self, line=None):
        """
        Adds an entry to the vault
        """
        entry = self.vault.Record.create()
        while True:
            entry.title = getpass._raw_input('Entry\'s title: ')
            if entry.title == "":
                accept_empty = getpass._raw_input("Entry is empty. Enter Y to accept ")
                if accept_empty.lower() == 'y':
                    break
            else:
                break
        entry.group = getpass._raw_input('Entry\'s group: ')
        entry.user = getpass._raw_input('Username: ')
        entry.notes = getpass._raw_input('Entry\'s notes: ')
        entry.url = getpass._raw_input('Entry\'s url: ')

        entry.passwd = self.prompt_password()

        self.vault.records.append(entry)
        self.vault_modified = True
        print "Entry Added, but vault not yet saved"

    def do_export(self, line=None):
        print "Exporting file " + self.vault_file_name + "..."
        self.vault.export(self.vault_password, self.vault_file_name)

    def prompt_password(self, old_password=None):
        created_random_password = False

        while True:
            message = "New password. [.] for none, [ENTER] for random.\n"
            if old_password is not None:
                message = "New password. [.] for none, [..] to keep the same. [ENTER] for random\n"
            passwd = getpass.getpass("%sPassword: " % message)
            if passwd == "":
                from ...random_password import random_password
                #TODO(climent): move the options to the config file
                password_policy = {'L': True, 'R': True, 'U': True, 'l': True, '2': True, 's': True, 'S': True}
                while True:
                    passwd = random_password().generate_password(password_policy)
                    created_random_password = True
                    print "Generated password: %s" % passwd
                    while True:
                        accept_password = getpass._raw_input('Enter [y] to accept, [ENTER] for random ')
                        if accept_password in password_policy:
                            if password_policy[accept_password] is True:
                                password_policy[accept_password] = False
                            else:
                                password_policy[accept_password] = True
                            print password_policy
                        else:
                            break
                    if accept_password.lower() == "y":
                        break
                break
            elif old_password is not None and passwd == "..":
                return old_password
            elif passwd == '.':
                passwd = ''
            if created_random_password is False:
                passwd2 = getpass.getpass("Re-Type Password: ")
                if passwd2 == '.':
                    passwd2 = ''
                if passwd != passwd2:
                    print "Passwords don't match"
                elif passwd == "":
                    empty_passwd = getpass.getpass("Password is empty. Enter Y to accept ")
                    if empty_passwd.lower() == "y":
                        break
                else:
                    break
        return passwd

    def do_del(self, line=None):
        """
        Delete an entry from the vault.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        vault_records = None
        match_records = None
        nomatch_records = None

        uuid = None
        title = None
        user = None
        group = None

        uuid_regexp = '^[a-f0-9]{8}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{12}$'
        pattern = re.compile(uuid_regexp, re.IGNORECASE)

        if pattern.search(line) is not None:
            uuid = line

        match_records, nonmatch_records = self.mod_titles(title=title, uuid=uuid, user=user, group=group)

        if match_records is None:
            print "No matches found."
            return

        if len(match_records) > 1:
            print "Too many records matched your search criteria"
            for record in match_records:
                print "%s [%s] " % (record.title.encode('utf-8', 'replace'), record.user.encode('utf-8', 'replace'))
                return

        if len(match_records) == 1:
            print "Deleting the following record:"
            self.do_show(str(match_records[0].uuid))
            confirm_delete = getpass._raw_input("Confirm you want to delete the record [YES]: ")
            if confirm_delete.lower() == 'yes':
                self.vault.records = nonmatch_records
                print "Entry Deleted, but vault not yet saved"
                self.vault_modified = True

        print ""

    # There must be better way to do this, this is quite unpleasant for user do work with.
    # maybe sometuing like mod u [name], mod t [title], mod g [group], mod group.title
    def do_mod(self, line=None):
        """
        Modify an entry from the vault. Every record is identified by group.title 
        locators if they are not provided entry is considered as title we try to match it against db.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        vault_records = None
        match_records = None
        nomatch_records = None

        uuid = None
        uuid_regexp = '[a-f0-9]{8}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{12}'
        pattern = re.compile(uuid_regexp, re.IGNORECASE)
        title = ""
        user = None
        group = None
        
        
        if pattern.match(line) is not None:
            uuid = line
        else:
            if len(line.split(".")) == 2 and " " not in line:
                group = line.split(".")[0]
                title = line.split(".")[1]
            else:
                line_elements = line.split(" ")
                title = line_elements[0]
                
                if len(line_elements) == 2:
                    group = line_elements[1]
                if len(line_elements) == 3:
                    user = line_elements[2]
        
        match_records, nonmatch_records = self.mod_titles(title=title, uuid=uuid, user=user, group=group)

        if match_records is None:
            print "No matches found."
            return

        if len(match_records) > 1:
            print "Too many records matched your search criteria"
            for record in match_records:
                print "%s [%s] " % (record.title.encode('utf-8', 'replace'), record.user.encode('utf-8', 'replace'))
                return

        _vault_modified = False
        record = match_records[0]
        new_record = {}

        print ''
        if self.uuid is True:
            print 'Uuid: [%s]' % str(record.uuid)
        print 'Modifying: [%s.%s]' % (record.group.encode('utf-8', 'replace'), record.title.encode('utf-8', 'replace'))
        print 'Enter a single dot (.) to clear the field.'
        print ''

        new_record['group'] = getpass._raw_input('Group [%s]: ' % record.group)

        if new_record['group'] == ".":
            new_record['group'] = ""
        if new_record['group'] == "":
            new_record['group'] = record.group
        if new_record['group'] != record.group:
            _vault_modified = True

        new_record['title'] = getpass._raw_input('Title [%s]: ' % record.title)

        if new_record['title'] == ".":
            new_record['title'] = ""
        if new_record['title'] == "":
            new_record['title'] = record.title
        if new_record['title'] != record.title:
            _vault_modified = True

        new_record['user'] = getpass._raw_input('User  [%s]: ' % record.user)

        if new_record['user'] == ".":
            new_record['user'] = ""
        if new_record['user'] == "":
            new_record['user'] = record.user
        if new_record['user'] != record.user:
            _vault_modified = True

        new_record['password'] = self.prompt_password(old_password=record.passwd)
        if new_record['password'] != record.passwd:
            _vault_modified = True

        if record.notes.encode('utf-8', 'replace') != "":
            print '[NOTES]'
            print '%s' % record.notes

        new_record['notes'] = getpass._raw_input('Entry\'s notes: ')

        if new_record['notes'] == ".":
            new_record['notes'] = ""
        if new_record['notes'] == "":
            new_record['notes'] = record.notes
        if new_record['notes'] != record.notes:
            _vault_modified = True

        new_record['url'] = getpass._raw_input('Entry\'s url [%s]: ' % record.url)

        if new_record['url'] == ".":
            new_record['url'] = ""
        if new_record['url'] == "":
            new_record['url'] = record.url
        if new_record['url'] != record.url:
            _vault_modified = True

        if _vault_modified == True:
            record.title = new_record['title']
            record.user = new_record['user']
            record.group = new_record['group']
            record.notes = new_record['notes']
            record.url = new_record['url']
            record.passwd = new_record['password']

            self.vault.records = nonmatch_records
            self.vault.records.append(record)
            print "Entry Modified, but vault not yet saved"
            self.vault_modified = True

        print ""
    
    def do_ls(self, line):
        """
        Show contents of this Vault. If an argument is added a case insensitive
        search of titles is done, entries can also be specified as regular expressions.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        if line is not None:
            vault_records = self.find_titles(line)
        else:
            vault_records = self.vault.records[:]

        if self.sort_key == 'alpha':
            vault_records.sort(lambda e1, e2: cmp(e1.title, e2.title))
        elif self.sort_key == 'mod':
            vault_records.sort(lambda e1, e2: cmp(e1.last_mod, e2.last_mod))

        if vault_records is None:
            print "No matches found."
            return

        print ""
        print "[group.title] username"
        print "URL: url"
        print "Notes: notes"
        print "Last mod: modification time"
        print "-"*10
        for record in vault_records:
            print "[%s.%s] %s" % (record.group.encode('utf-8', 'replace'),
                                   record.title.encode('utf-8', 'replace'),
                                   record.user.encode('utf-8', 'replace'))
            if self.output == 'verbose':
              if record.url:
                  print "    URL: %s" % (record.url.encode('utf-8', 'replace'))
              if record.notes:
                  print "    Notes: %s" % (record.notes.encode('utf-8', 'replace'))
              if record.last_mod != 0:
                  print "    Last mod: %s" % time.strftime('%Y/%m/%d',time.gmtime(record.last_mod))
        print "-"*15
        print ""

    def do_output(self, line=None):
        """
        Change status of output
        """
        if self.output == 'brief':
            self.output = 'verbose'
        else:
            self.output = 'brief'
        print "output is %s" % self.output

    def do_sort(self, line=None):
        """
        Change status of sort key
        """
        if self.sort_key == 'alpha':
            self.sort_key = 'mod'
        else:
            self.sort_key = 'alpha'
        print "sort key is %s" % self.sort_key

    def do_format(self, line=None):
        """
        Change database format to v4
        """
        print "Database format used is %s" % self.vault_format
    
    def do_uuid(self, line=None):
        """
        Change status of uuid
        """
        if self.uuid == False:
            self.uuid = True
        else:
            self.uuid = False
        print "uuid is %s" % self.uuid

    def do_echo(self, line=None):
        """
        Change status of echo
        """
        if self.echo == False:
            self.echo = True
        else:
            self.echo = False
        print "echo is %s" % self.echo

    def do_vi(self, line=None):
        """
        Set vi editing mode for commandline
        """
        if self.vi == False:
            self.vi = True
            readline.parse_and_bind('set editing-mode vi')
        else:
            self.vi = False
            readline.parse_and_bind('set editing-mode emacs')

        print "Vi Editing mode is %s" % self.vi

    def do_tab(self, line=None):
        """
        Enable Tab completition for cmd interface
        """
        if self.tabcomp == False:
            self.tabcomp = True
            readline.parse_and_bind('tab: complete')
        else:
            self.tabcomp = False
            readline.parse_and_bind('tab: noncomplete')

        print "TAB completition mode is %s" % self.tabcomp

    def do_show(self, line, echo=True, passwd=False, uuid=False):
        """
        Show the specified entry (including its password).
        A case insenstive search of titles is done, entries can also be specified as regular expressions.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        matches = self.find_titles(line)

        if matches is None:
            print 'No entry found for "%s"' % line
            return

        if self.echo is not None:
            do_echo = self.echo
        else:
            do_echo = echo

        if self.uuid is not None:
            do_uuid = self.uuid
        else:
            do_uuid = uuid

        print ""
        for record in matches:
            if do_uuid == True:
                print "[%s]" % record.uuid
            print """[%s.%s]
Username : %s""" % (record.group.encode('utf-8', 'replace'),
                    record.title.encode('utf-8', 'replace'),
                    record.user.encode('utf-8', 'replace'))

            if do_echo is True:
                print "Password : %s" % record.passwd.encode('utf-8', 'replace')

            if record.notes.strip():
                print "Notes    : %s" % record.notes.encode('utf-8', 'replace')

            if record.url:
                print "URL      : %s" % record.url.encode('utf-8', 'replace')

            if record.last_mod != 0:
                print "Last mod : %s" % time.strftime('%Y/%m/%d',time.gmtime(record.last_mod))

            print ""
    
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

    def mod_titles(self, title=None, uuid=None, user=None, group=None):
        """Finds titles, user, group, uuid, or a combination as an exact expression. (Case insensitive)"""
        matches = []
        nonmatches = []
        if uuid is not None:
            for record in self.vault.records:
                if str(record.uuid) == uuid:
                    matches.append(record)
                else:
                    nonmatches.append(record)
        else:
            pat_title = re.compile("^%s$" % title, re.IGNORECASE)
            for record in self.vault.records:
                if pat_title.match(record.title) is not None:
                    if user is not None and user != "":
                        pat_title = re.compile("^%s$" % user, re.IGNORECASE)
                        if pat_user.match(record.user) is None:
                            nonmatches.append(record)
                            continue
                    if group is not None and group != "":
                        pat_group = re.compile("^%s$" % group, re.IGNORECASE)
                        if pat_group.match(record.group) is None:
                            nonmatches.append(record)
                            continue
                    matches.append(record)
                else:
                    nonmatches.append(record)
                    continue

        if len(matches) == 0:
            return None, nonmatches
        else:
            return matches, nonmatches
    
    def find_titles(self, regexp):
        "Finds titles, username, group, or combination of all 3 matching a regular expression. (Case insensitive)"
        matches = []
        pat = re.compile(regexp, re.IGNORECASE)
        for record in self.vault.records:
            if pat.match(record.title) is not None:
                matches.append(record)
            elif pat.match(record.user) is not None:
                matches.append(record)
            elif pat.match(record.group) is not None:
                matches.append(record)
            elif pat.match(str(record.uuid)) is not None:
                matches.append(record)
            elif pat.match("%s.%s [%s]" % (record.group, record.title, record.user)) is not None:
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
    parser.add_option("-s", "--show", dest="do_show", default=None, action="store", type="string", help="Show entries matching REGEX", metavar="REGEX")
    parser.add_option("-i", "--interactive", dest="interactive", default=False, action="store_true", help="Use command line interface")
    parser.add_option("-n", "--new", dest="create_new_vault", default=False, action="store_true", help="Create and initialize new Vault.")
    parser.add_option("-c", "--console_only", dest="console", default=False, action="store_true", help="Disable interaction with clipboard")
    parser.add_option("-p", "--password", dest="passwd", default=False, action="store_true", help="Auto adds password to clipboard. (GTK Only)")
    parser.add_option("-e", "--echo", dest="echo", default=False, action="store_true", help="Passwords are displayed on the screen")
    parser.add_option("-u", "--uuid", dest="uuid", default=False, action="store_true", help="Show uuid while processing passwords")
    parser.add_option("-x", "--export", dest="export", default=False, action="store_true", help="Export database to csv")
    parser.add_option("-f", "--format", dest="format", default=False, action="store", type="string", help="Open vault with format version v4 with multi password support options [v3, v4]")
    parser.add_option("-P", "--passwd", dest="do_password", default=False, action="store_true", help="Add new password to v4 database while user must know any existing password.")

    (options, args) = parser.parse_args()

    interactiveConsole = InteractiveConsole()

    if (len(args) < 1):
        if (config.recentvaults):
            interactiveConsole.vault_file_name = config.recentvaults[0]
            print "No Vault specified, using %s" % interactiveConsole.vault_file_name
        else:
            print "No Vault specified, and none found in config."
            sys.exit(2)
    elif (len(args) > 1):
        print "More than one Vault specified"
        sys.exit(2)
    else:
        interactiveConsole.vault_file_name = args[0]

    if options.format:
      interactiveConsole.vault_format = options.format
    else:
      interactiveConsole.vault_format = "auto"

    if options.create_new_vault:
      # If we do not know, which version of db build go for v3
      if interactiveConsole.vault_format == "auto":
        interactiveConsole.vault_format = "v3"
      interactiveConsole.create_vault()
    else:
        interactiveConsole.open_vault()
        if options.do_ls:
            interactiveConsole.do_ls("")
        elif options.do_show:
            interactiveConsole.do_show(options.do_show, options.echo, options.passwd, options.uuid)
        elif options.export:
            interactiveConsole.do_export()
        elif options.do_password:
          if interactiveConsole.vault.get_vault_format() != "v4":
            print "Can't use -P option with non v4 database format which is used by default."
            sys.exit(2)
          interactiveConsole.do_password()
        else:
            interactiveConsole.intro +=  interactiveConsole.vault_format
            interactiveConsole.uuid = options.uuid
            interactiveConsole.echo = options.echo
            interactiveConsole.set_prompt()
            interactiveConsole.cmdloop()

    sys.exit(0)


main(sys.argv[1:])
