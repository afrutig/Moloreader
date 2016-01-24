#!/bin/bash


# Setup GPIO output pins.
# usage: sudo bash gpio-setup.sh [pins...]


pins=$@

base='/sys/class/gpio'

echo setting up $pins

for p in $pins; do
		test -d $base/gpio${p} && echo $p > $base/unexport
		echo $p > $base/export
		echo out > $base/gpio${p}/direction
		
		chmod 666 $base/gpio${p}/value
done;
