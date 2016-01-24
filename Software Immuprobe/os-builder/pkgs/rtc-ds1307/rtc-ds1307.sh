#!/bin/sh

# required modules
#snd-bcm2835
#i2c-dev
#i2c-bcm2708
#rtc-ds1307


# register the i2c device
# TODO: systemd service for this
hwclock -s
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device

# read the clock
hwclock -r

# set the time on the rpi (ntp, manually, ...)
# write time to ds1307
hwclock -w

# verify:
hwclock -r
