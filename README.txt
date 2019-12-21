
Loxodo -- Password Safe V3 compatible Password Vault
Copyright (C) 2008-2018 Christoph Sommer <mail@christoph-sommer.de>

Loxodo lives at http://www.christoph-sommer.de/loxodo


Setup:
------

Loxodo requires Python 2 or 3 and two add-on python modules: Six and wxPython 4.0.

The simplest way to set things up is to use your distribution's package management to install Python and these two modules.

Alternatively, you can install the Python module `pip` and use it to install the required modules for you.
Note that, at the time of this writing, wxPython 4 ("Phoenix") availability for Linux distributions is rather limited; if you want to avoid building wxPython from source, you can follow the instructins from its download page and use a command like the following (substituting "debian-9" for you distribution's code name):

    python -m pip install --user pip
    python -m pip install --user six
    python -m pip install --user -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-9 wxPython

Alternatively, you can install the Python module `pipenv` and use it to set up a virtual environment for you.
Note that, on Mac OS X, you will likely need to manually (e.g., using homebrew) install a version of python that supports `pipenv` first.

    python -m pip install pip
    python -m pip install pipenv
    python -m pipenv update

Loxodo can then be run as follows:

    python -m pipenv run ./loxodo.py

On Mac OS X, Loxodo can be run after creating a Mac OS X app bundle:
Note that you can supply a `-A` switch to py2app to keep the source code in-tree for easier development.

    python -m pipenv run ./setup.py py2app
    open dist/Loxodo.app

Similar functionality exists for Windows, where ./setup.py py2exe creates an executable.


Quickstart:
-----------

./loxodo.py
	runs Loxodo in GUI mode (if available)

./loxodo.py -h
	displays help about Loxodo's command line mode

./loxodo.py -i
	runs Loxodo in command line interactive mode

