.PHONY: locale app exe

locale:
	make -C locale

app:
	python setup.py py2app

exe:
	python setup.py py2exe

