
.PHONY: prepare
prepare:

.PHONY: clean
clean:

.PHONY: install
install:
	sudo install --group=root --owner=root --mode=644 *.service /usr/lib/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable firstboot
