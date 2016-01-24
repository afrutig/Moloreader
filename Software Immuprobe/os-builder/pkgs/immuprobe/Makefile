# install script for immuprobe

.PHONY .SILENT: all
all:
	echo 'use: make prepare or make install'

.PHONY: prepare
prepare:
	cp -r ../../../gui .
	cp -r ../../../python .
	cp -r ../../../resources .

.PHONY: clean
clean:
	rm -rf gui python 

.PHONY: install
install:
	mkdir -p /opt/immuprobe
	cp -r gui python samples /opt/immuprobe
	chown -R root:root /opt/immuprobe
	chmod -R 755 /opt/immuprobe
