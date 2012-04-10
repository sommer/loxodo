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

WEB interface
-------------

To start web interface you need to install flask python module. This is used to render
templates and manage controller. To install flask user need to run this command

easy_install flask

After installation of flask user can start web interface on port 5000 with command

$ ./web-loxodo.py


Changelog
---------

June 2011: Add more command line options to create new vault from shell, dump database to csv
file. Make some small improvements to cmd loop to (tab completition, vi mode).
August 2011: Add support for multiple secondary password which can access database,
to make database sharing possible with other users without knowing some
shared password. With this change we introduce new version of vault database called version 4
with multiple password support.
August 2011: Add option to add db passwords to vault from cli entirely.
December 2011: Add simple web interface, based on flask.

TODO
----

[Bugs]
* mod command doesn't work I can't modify existing entries with it.

[Features]
* It might be good to be able to merge 2 databases together.
* Make crypto class and hide all crypto stuff there so we can use different,
  crypto algorithms e.g. AES
* Add option to add users/passwords to vault from cli entirely.
* Use javascript to request password from vault, do not put passwords to html.
* Test suite
    [1] http://docs.python.org/library/unittest.html
* Cleanup, a lot of code is quite messy, add comments, support for pydoc
    [1] http://docs.python.org/library/pydoc.html

Pythonbrew setup
~~~~~~~~~~~~~~~~

[haad@cid chillisys-pass]$ pythonbrew install --force 2.7.2
Use the previously fetched /Users/haad/.pythonbrew/dists/Python-2.7.2.tgz
Extracting Python-2.7.2.tgz into /Users/haad/.pythonbrew/build/Python-2.7.2

This could take a while. You can run the following command on another shell to track the status:
  tail -f /Users/haad/.pythonbrew/log/build.log

Patching Python-2.7.2
Installing Python-2.7.2 into /Users/haad/.pythonbrew/pythons/Python-2.7.2

Downloading distribute_setup.py as /Users/haad/.pythonbrew/dists/distribute_setup.py
######################################################################## 100.0%
Installing distribute into /Users/haad/.pythonbrew/pythons/Python-2.7.2
Installing pip into /Users/haad/.pythonbrew/pythons/Python-2.7.2

Installed Python-2.7.2 successfully. Run the following command to switch to Python-2.7.2.
  pythonbrew switch 2.7.2
[haad@cid chillisys-pass]$ pythonbrew use python-2.7.2
ERROR: `Python-python-2.7.2` is not installed.
[haad@cid chillisys-pass]$ pythonbrew use 2.7.2
Using `Python-2.7.2`
[haad@cid chillisys-pass]$ pythonbrew switch 2.7.2
Switched to Python-2.7.2
[haad@cid chillisys-pass]$ python -V
Python 2.7.2
[haad@cid chillisys-pass]$ pythonbrew venv init
Downloading virtualenv.tar.gz as /Users/haad/.pythonbrew/dists/virtualenv.tar.gz
######################################################################## 100.0%
Extracting virtualenv into /Users/haad/.pythonbrew/etc/virtualenv
[haad@cid chillisys-pass]$ pythonbrew venv create chillisys-pass
Creating `chillisys-pass` environment into /Users/haad/.pythonbrew/venvs/Python-2.7.2
Already using interpreter /Users/haad/.pythonbrew/pythons/Python-2.7.2/bin/python
New python executable in /Users/haad/.pythonbrew/venvs/Python-2.7.2/chillisys-pass/bin/python
Installing setuptools............done.
Installing pip...............done.
[haad@cid chillisys-pass]$ pythonbrew venv list
# virtualenv for Python-2.7.2 (found in /Users/haad/.pythonbrew/venvs/Python-2.7.2)
chillisys-pass
[haad@cid chillisys-pass]$ pythonbrew venv use chillisys-pass
# Using `chillisys-pass` environment (found in /Users/haad/.pythonbrew/venvs/Python-2.7.2)
# To leave an environment, simply run `deactivate`
(chillisys-pass)[haad@cid chillisys-pass]$ pip install flask
Downloading/unpacking flask
  Downloading Flask-0.7.2.tar.gz (469Kb): 469Kb downloaded
  Running setup.py egg_info for package flask

    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
    warning: no previously-included files matching '*.pyc' found under directory 'tests'
    warning: no previously-included files matching '*.pyo' found under directory 'tests'
    warning: no previously-included files matching '*.pyc' found under directory 'examples'
    warning: no previously-included files matching '*.pyo' found under directory 'examples'
    no previously-included directories found matching 'docs/_build'
    no previously-included directories found matching 'docs/_themes/.git'
Downloading/unpacking Werkzeug>=0.6.1 (from flask)
  Downloading Werkzeug-0.7.1.tar.gz (1.1Mb): 1.1Mb downloaded
  Running setup.py egg_info for package Werkzeug

    warning: no files found matching '*' under directory 'werkzeug/debug/templates'
    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
    warning: no previously-included files matching '*.pyc' found under directory 'tests'
    warning: no previously-included files matching '*.pyo' found under directory 'tests'
    warning: no previously-included files matching '*.pyc' found under directory 'examples'
    warning: no previously-included files matching '*.pyo' found under directory 'examples'
    no previously-included directories found matching 'docs/_build'
Downloading/unpacking Jinja2>=2.4 (from flask)
  Downloading Jinja2-2.6.tar.gz (389Kb): 389Kb downloaded
  Running setup.py egg_info for package Jinja2

    warning: no previously-included files matching '*' found under directory 'docs/_build'
    warning: no previously-included files matching '*.pyc' found under directory 'jinja2'
    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'jinja2'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
Installing collected packages: flask, Werkzeug, Jinja2
  Running setup.py install for flask

    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
    warning: no previously-included files matching '*.pyc' found under directory 'tests'
    warning: no previously-included files matching '*.pyo' found under directory 'tests'
    warning: no previously-included files matching '*.pyc' found under directory 'examples'
    warning: no previously-included files matching '*.pyo' found under directory 'examples'
    no previously-included directories found matching 'docs/_build'
    no previously-included directories found matching 'docs/_themes/.git'
  Running setup.py install for Werkzeug

    warning: no files found matching '*' under directory 'werkzeug/debug/templates'
    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
    warning: no previously-included files matching '*.pyc' found under directory 'tests'
    warning: no previously-included files matching '*.pyo' found under directory 'tests'
    warning: no previously-included files matching '*.pyc' found under directory 'examples'
    warning: no previously-included files matching '*.pyo' found under directory 'examples'
    no previously-included directories found matching 'docs/_build'
  Running setup.py install for Jinja2

    warning: no previously-included files matching '*' found under directory 'docs/_build'
    warning: no previously-included files matching '*.pyc' found under directory 'jinja2'
    warning: no previously-included files matching '*.pyc' found under directory 'docs'
    warning: no previously-included files matching '*.pyo' found under directory 'jinja2'
    warning: no previously-included files matching '*.pyo' found under directory 'docs'
Successfully installed flask Werkzeug Jinja2
Cleaning up...

