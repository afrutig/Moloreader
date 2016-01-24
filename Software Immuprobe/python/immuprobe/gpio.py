#!/bin/env python2

'''
A minimalistic GPIO binding for switching on an off some ports.

Setting up the GPIO pins requires root privileges. Therefore a seperate shell script
takes care of this task. It is located at '_gpio_setup_script'.
The user running gpio.py must be allowed to call this script via sudo without password promt.
So something similar to this must be in /etc/sudoers:
ALL ALL=(ALL) NOPASSWD: /opt/gpio-setup.sh
'''

import os
import subprocess

_gpio_base = '/sys/class/gpio/'
_gpio_setup_script = '/opt/gpio-setup.sh'


# returns True iff the gpio setup scripts are available on the system.
def _gpio_setup_available():
	retval = subprocess.call('test -f %s'%_gpio_setup_script, shell=True)
	return retval == 0
	
if _gpio_setup_available():
	def setup_output_pins(pins):
		pins = [str(p) for p in pins if type(p) is int]
		pins = ' '.join(pins)
		os.system('sudo %s %s'%(_gpio_setup_script,pins))
		
	def _write(path, value):
		os.system('echo %i > %s%s'%(value, _gpio_base, path))
		
else:
	print('%s not available'%_gpio_setup_script)
	
	def setup_output_pins(pins):
		pins = [str(p) for p in pins if type(p) is int]
		pins = ' '.join(pins)
		print('simulating: sudo %s %s'%(_gpio_setup_script,pins))
		
	def _write(path, value):
		print('simulating: echo %i > %s%s'%(value, _gpio_base, path))
		
def write(pin, value):
	_write('gpio%s/value'%pin, value)

