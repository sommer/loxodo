
Loxodo -- Password Safe V3 and V4 compatible Password Vault
Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
Copyright (C) 2011 Adam Hamsik <adam.hamsik@chillisys.com>

Loxodo lives at http://www.christoph-sommer.de/loxodo

This source code is from https://github.com/haad/loxodo


Quickstart
----------

./loxodo.py
	runs Loxodo in GUI mode (if available)

./loxodo.py -h
	displays help about Loxodo's cmdline mode

./loxodo.py -i
	runs Loxodo in CLI Interactive mode

## Add Password to vault version 4 first ask for already existing password 
##  later submit new user password.
$ ./loxodo.py -P /tmp/test4.db 
Opening /tmp/test4.db ...
Vault password: PASSWORD1
... Done.

New User Vault password: PASSWORD2

$ ./loxodo.py -i /tmp/test4.db 
Opening /tmp/test4.db ...
Vault password: PASSWORD2
... Done.

Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit. Database format is: auto
[test4.db]> add
Entry's title: 567
Entry's group: 567
Username: popo
Entry's notes: 
Entry's url: 
New password. [.] for none, [ENTER] for random.
Password: 
Generated password: veBbR`aM
Enter [y] to accept, [ENTER] for random y
Entry Added, but vault not yet saved
[test4.db*]> save
Changes Saved
[test4.db]> quit

$ ./loxodo.py -i /tmp/test4.db 
Opening /tmp/test4.db ...
Vault password: PASSWORD2
... Done.

Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit. Database format is: auto
[test4.db]> ls

[group.title] username
URL: url
Notes: notes
----------------------
[567.567] popo
URL: 
Notes: 
----------
[test123.test] jozo
URL: 
Notes: 
----------

[test4.db]> quit

$ ./loxodo.py -i /tmp/test4.db 
Opening /tmp/test4.db ...
Vault password: PASSWORD1
... Done.

Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit. Database format is: auto
[test4.db]> ls

[group.title] username
URL: url
Notes: notes
----------------------
[567.567] popo
URL: 
Notes: 
----------
[test123.test] jozo
URL: 
Notes: 
----------

[test4.db]> quit


Changelog
---------

June 2011: Add more command line options to create new vault from shell, dump database to csv
file. Make some small improvements to cmd loop to (tab completition, vi mode).
August 2011: Add support for multiple secondary password which can access database,
to make database sharing possible with other users without knowing some
shared password. With this change we introduce new version of vault database called version 4 
with multiple password support.
August 2011: Add option to add db passwords to vault from cli entirely.

TODO
----

[Bugs]
* mod command doesn't work I can't modify existing entries with it.

[Features]
* It might be good to be able to merge 2 databases together.
* Make crypto class and hide all crypto stuff there so we can use different, 
  crypto algorithms e.g. AES
* Add option to add users/passwords to vault from cli entirely.
* Add simple web interface ?
    [1] http://flask.pocoo.org/docs/quickstart/
* Test suite
    [1] http://docs.python.org/library/unittest.html
* Cleanup, a lot of code is quite messy, add comments, support for pydoc
    [1] http://docs.python.org/library/pydoc.html
