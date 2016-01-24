#!/bin/sh

PACKAGE_LIST=/opt/firstboot/packages.conf
CUSTOM_PACKAGE_DIR=/opt/firstboot/pkgs

echo 'upgrading the system...'
pacman -Su --noconfirm --force || (echo 'Package upgrade failed!'; exit)

echo 'installing packages...'

# cut-grep-thing: remove comments and empty lines from package.conf file
pacman -S --noconfirm --force $(cat $PACKAGE_LIST | cut -f1 -d\# | grep -v ^$) || (echo 'Package installation failed!'; exit)

# /etc/sudoers has been overwritten. Reset it.
mv /etc/sudoers.pacorig /etc/sudoers


echo 'installing custom packages...'
make -C $CUSTOM_PACKAGE_DIR install

systemctl enable xlogin@alarm

echo 'disabling this script'
systemctl disable firstboot


echo 'done'

reboot
