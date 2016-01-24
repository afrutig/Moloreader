# install script for python picamera driver

.PHONY .SILENT: all
all:
	echo 'use: make prepare or make install'

.PHONY: prepare
prepare:
	#get from github
	#test -d picamera-git || git clone https://github.com/waveform80/picamera.git picamera-git
	#bash -c 'cd picamera-git; git pull'
	
	# get from python.org
	wget https://pypi.python.org/packages/source/p/picamera/picamera-1.10.tar.gz

.PHONY: clean
clean:
	#rm -rf picamera-git
	rm -rf picamera*

.PHONY: install
install:
	# install from git repo
	#bash -c 'cd picamera-git; python setup.py install'
	
	tar -xzf picamera*.tar.gz
	bash -c 'cd picamera*; python2 setup.py install'
	
	sed -i '/^gpu_mem=/d' /boot/config.txt
	
	echo gpu_mem=128 >> /boot/config.txt
	echo start_file=start_x.elf >> /boot/config.txt
	echo fixup_file=fixup_x.dat >> /boot/config.txt
	echo disable_camera_led=1 >> /boot/config.txt

