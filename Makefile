.PHONY: locale app exe

locale:
	make -C locale

app:
	rm -fr build dist
	python setup.py py2app

exe:
	rm -fr build dist
	python setup.py py2exe

