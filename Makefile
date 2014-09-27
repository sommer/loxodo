.PHONY: locale app exe

locale:
	make -C locale

app:
	rm -fr build dist
	python setup.py py2app

exe:
	rm -fr build dist
	python setup.py py2exe

builddeb:
	python setup.py sdist --dist-dir=../
	rename -f 's/loxodo-(.*)\.tar\.gz/loxodo_$$1\.orig\.tar\.gz/' ../*
	debuild -us -uc

xdg:
	xdg-desktop-menu install --mode system --novendor loxodo.desktop

clean:
	rm -fr build loxodo.egg-info debian/*.substvars debian/*.log debian/files debian/loxodo debian/loxodo-qt4 debian/loxodo-wx

