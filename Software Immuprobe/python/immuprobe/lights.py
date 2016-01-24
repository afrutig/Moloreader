#!/bin/env python2
'''
Controller for GPIO attached LEDs.
'''

import gpio

# GPIO pin definitions
_pins = {'blue': 20, 'white': 21, 'green': 21}


gpio.setup_output_pins(_pins.values())

'''
Switch LEDs on or off.

Params:
	color = green, blue
	value = True or False
'''
def setLight(color, value):
	
	if color in [None, 'none']:
		return
	
	if color not in _pins:
		raise Exception('Unsupported light color.')
	print('set light', color, value)
	gpio.write(_pins[color], value)

