
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
