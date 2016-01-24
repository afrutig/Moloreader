# Prepare and install all packages listed in PACKAGES.

PACKAGES ?=
PACKAGES += rtc-ds1307
PACKAGES += picamera
PACKAGES += immuprobe gpio-setup
PACKAGES += xlogin

.PHONY .SILENT: prepare
prepare:
	for p in $(PACKAGES); do \
		echo preparing $$p; \
		$(MAKE) -C $$p prepare; \
	done

.PHONY .SILENT: install
install:
	for p in $(PACKAGES); do \
		echo installing $$p; \
		$(MAKE) -C $$p install; \
	done

.PHONY .SILENT: clean
clean:
	for p in $(PACKAGES); do \
		echo cleaning $$p; \
		$(MAKE) -C $$p clean; \
	done
