.PHONY: locale app exe

locale:
	make -C locale

app:
	rm -fr build dist
	python setup.py py2app

exe:
	rm -fr build dist
	python setup.py py2exe

sdist:
	python setup.py sdist -d ..

xdg:
	xdg-desktop-menu install --mode system --novendor loxodo.desktop

clean:
	rm -fr build loxodo.egg-info
