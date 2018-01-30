
Loxodo -- Password Safe V3 compatible Password Vault
Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>

Loxodo lives at http://www.christoph-sommer.de/loxodo


Setup:
------

Loxodo requires Python 2.7 and wxWidgets 4.0 (currently available as a beta version).

Execute the following commands to create a virtual environment called 'venv', install wxpython there, and build a Mac OS X app bundle:

python2 -m pip install virtualenv
python2 -m virtualenv venv
source venv/bin/activate
pip install wxpython==4.0.0b2
python setup.py py2app
deactivate

As an alternative to building an app bundle, Loxodo can also be started from the virtual environment like so:

PYTHONHOME=venv python2 ./loxodo.py


Quickstart:
-----------

./loxodo.py
	runs Loxodo in GUI mode (if available)

./loxodo.py -h
	displays help about Loxodo's cmdline mode

./setup.py py2app
	creates a stand-alone .app (Mac OS X)

./setup.py py2exe
	creates a stand-alone .exe (Windows)

./loxodo.py -i
	runs Loxodo in CLI Interactive mode

