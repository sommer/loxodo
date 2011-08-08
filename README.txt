
Loxodo -- Password Safe V3 and V4 compatible Password Vault
Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
Copyright (C) 2011 Adam Hamsik <adam.hamsik@chillisys.com>

Loxodo lives at http://www.christoph-sommer.de/loxodo


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

TODO
----

* It might be good to be able to merge 2 databases together.
* Add option to add users to vault from cli entirely.
* Add support for multiple secondary password which can access database,
  to make database sharing possible with other users without knowing some
  shared password
* Make crypto class and hide all crypto stuff there so we can use different, 
  crypto algorithms e.g. AES
* Add simple web interface ?
* Test suite

