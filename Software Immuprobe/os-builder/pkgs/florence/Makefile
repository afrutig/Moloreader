# install script for florence on screen keyboard


INSTALL=install --group=root --owner=root --mode=644
	
.PHONY .SILENT: all
all:
	echo 'use: make prepare or make install'

.PHONY: prepare
prepare:

.PHONY: clean
clean:

.PHONY: install
install: systemd
	sudo pacman -U florence05*.tar.xz

.PHONY: systemd
systemd: florence.service
	# TODO
