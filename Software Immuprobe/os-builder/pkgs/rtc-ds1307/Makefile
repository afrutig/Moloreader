# install script for rtc-ds1307 hardware clock


INSTALL=install --group=root --owner=root --mode=644
	
.PHONY .SILENT: all
all:
	echo 'use: make prepare or make install'

.PHONY: prepare
prepare:

.PHONY: clean
clean:

.PHONY: install
install: modules-load i2c systemd

.PHONY: systemd
systemd: rtc-ds1307.service
	$(INSTALL) rtc-ds1307.service /usr/lib/systemd/system/
	systemctl daemon-reload
	systemctl enable rtc-ds1307.service
	
.PHONY: i2c
i2c:
	echo dtparam=i2c1=on >> /boot/config.txt
	echo dtparam=i2c_arm=on >> /boot/config.txt

.PHONY: modules-load
modules-load: rtc-ds1307-modules.conf
	$(INSTALL) rtc-ds1307-modules.conf /etc/modules-load.d/
	
