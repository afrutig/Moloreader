# Build script for Archlinux-ARM image on a Raspberry PI 2.

IMGFILE=immuprobe.img

# The loopback device: 'losetup -f' gives you the name of the first free loopback device, something like /dev/loop0.
#LOOPBACK=$(shell losetup -f)
LOOPBACK=/dev/loop0

# The root filesystem type. (f2fs is convenient for flash based memory)
FILESYSTEM=ext4
IMAGESIZE=3000M
IMGROOT=$(shell pwd)/root

# config file for armv7h packet manager
PACMAN_CONF=pacman.conf
PACMAN=sudo pacman --config $(PACMAN_CONF)
PACKAGE_LIST=packages.conf

PACKAGE_CACHE=pkg_cache

.PHONY: all
all: img

.PHONY: img
img: clean sources format copy install-config-files download-packages setup-firstboot umount

$(IMGFILE):
	touch $(IMGFILE)
	truncate -s $(IMAGESIZE) $(IMGFILE)	

.PHONY: partition
partition: $(IMGFILE)
	# create two partitions. First is 100MB, second as large as it can be.
	printf "o\nn\np\n1\n\n+100M\nt\nc\nn\np\n2\n\n\nw\n" | fdisk $(IMGFILE)

.PHONY: format
format: partition loopBack
	# format loop back
	sudo mkfs.vfat $(LOOPBACK)p1
	sudo mkfs.$(FILESYSTEM) $(LOOPBACK)p2

.PHONY: mount
mount: loopBack
	mkdir -p root
	sudo mount $(LOOPBACK)p2 root
	sudo mkdir -p root/boot
	sudo mount $(LOOPBACK)p1 root/boot
	
.PHONY: umount
umount:
	sudo umount root/boot || true
	sudo umount root || true
	sudo losetup -d $(LOOPBACK)
	
# extract tar.gz
.PHONY: copy
copy: sources mount
	sudo tar -xpf ArchLinuxARM-rpi-2-latest.tar.gz -C root
	sync

# create loop back device
# TODO auto delete loop0
.PHONY: loopBack
loopBack: $(IMGFILE)
	#sudo losetup --show -f -P $(LOOPBACK) $(IMGFILE)
	sudo losetup --show -P $(LOOPBACK) $(IMGFILE)
	sudo partprobe $(LOOPBACK)
	sleep 1
	
	# test if kernel recognized the partitions
	test -b $(LOOPBACK)p1
	test -b $(LOOPBACK)p2
	

# Download sources
.PHONY: sources
sources: ArchLinuxARM-rpi-2-latest.tar.gz

# Download ArchlinuxARM
ArchLinuxARM-rpi-2-latest.tar.gz:
	wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-2-latest.tar.gz

# Download ArchlinuxARM packages onto the image.
# Installation is done on the first boot of the RaspberryPI.
.PHONY: download-packages
download-packages:

	# load downloaded packages from cache
	(test -d $(PACKAGE_CACHE) && sudo rsync -r -u $(PACKAGE_CACHE)/* $(IMGROOT)/var/cache/pacman/pkg/) || true
	
	$(PACMAN) -Syy
	$(PACMAN) -Suw --noconfirm
	$(PACMAN) -Sw --noconfirm `cat $(PACKAGE_LIST) | cut -f1 -d\# | grep -v ^$$`
	
	# chache downloaded archlinux packages for next build
	mkdir -p $(PACKAGE_CACHE)
	# copy downloaded packages into cache
	sudo rsync -r -u $(IMGROOT)/var/cache/pacman/pkg/* $(PACKAGE_CACHE)

.PHONY: install-config-files
install-config-files:
	# TODO set permissions
	sudo cp -r config-files/* $(IMGROOT)
	sudo chown -R 1000 $(IMGROOT)/home/alarm

# Install firstboot scripts to image.
.PHONY: setup-firstboot
setup-firstboot: prepare-packages
	sudo bash -c 'echo "--- IMMUPROBE ---" > $(IMGROOT)/etc/motd'
	# copy firstboot script and package list
	sudo install -D --group=root --owner=root --mode=644 firstboot/*.sh $(PACKAGE_LIST) -t $(IMGROOT)/opt/firstboot/
	
	# install systemd service
	sudo install --group=root --owner=root --mode=644 firstboot/firstboot.service $(IMGROOT)/usr/lib/systemd/system/
	sudo ln -sf /usr/lib/systemd/system/firstboot.service $(IMGROOT)/etc/systemd/system/multi-user.target.wants
	
	sudo cp -r pkgs $(IMGROOT)/opt/firstboot

.PHONY: prepare-packages
prepare-packages:
	$(MAKE) -C pkgs


# Remove generated files but preserve large downloaded files.
.PHONY: clean
clean:
	$(MAKE) -C pkgs clean
	echo 'Keeping large downloads.'
	sudo umount root/boot root || echo "umount failed"
	sudo losetup -d $(LOOPBACK) || echo "loop back device not deleted"
	rm -f $(IMGFILE) || echo '$(IMGFILE) not deleted'
	rm -rf root

# Also remove large downloaded files
.PHONY: clean-all
clean-all: clean
	rm -rf $(PACKAGE_CACHE)
	rm -rf ArchLinuxARM-rpi-2-latest.tar.gz
