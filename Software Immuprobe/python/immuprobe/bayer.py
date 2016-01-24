#!/bin/env python2

'''
Capture raw bayer data from the RaspberryPi camera.

Source: http://picamera.readthedocs.org/en/release-1.10/recipes2.html#raw-bayer-data-captures
'''

import io
import time
import picamera
import numpy as np
from numpy.lib.stride_tricks import as_strided
from skimage.io import imshow, show

'''
Capture the green channel of raw bayer data.
'''
def capture_green(shutter_speed, iso=100):
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		# Let the camera warm up for a couple of seconds
		time.sleep(1)
		camera.framerate = 1
		camera.exposure_mode = 'off'
		camera.shutter_speed = int(shutter_speed)
		camera.awb_mode = 'off'
		camera.awb_gains = (1,1) # (red, blue)
		camera.iso = int(iso)
		# Capture the image, including the Bayer data
		camera.capture(stream, format='jpeg', bayer=True)

	# Extract the raw Bayer data from the end of the stream, check the
	# header and strip if off before converting the data into a numpy array

	data = stream.getvalue()[-6404096:]
	if data[:4] != 'BRCM':
		raise Exception('Invalid bayer data format!')
		
	data = data[32768:]
	data = np.fromstring(data, dtype=np.uint8)

	# The data consists of 1952 rows of 3264 bytes of data. The last 8 rows
	# of data are unused (they only exist because the actual resolution of
	# 1944 rows is rounded up to the nearest 16). Likewise, the last 24
	# bytes of each row are unused (why?). Here we reshape the data and
	# strip off the unused bytes

	data = data.reshape((1952, 3264))[:1944, :3240]

	# Horizontally, each row consists of 2592 10-bit values. Every four
	# bytes are the high 8-bits of four values, and the 5th byte contains
	# the packed low 2-bits of the preceding four values. In other words,
	# the bits of the values A, B, C, D and arranged like so:
	#
	#  byte 1   byte 2   byte 3   byte 4   byte 5
	# AAAAAAAA BBBBBBBB CCCCCCCC DDDDDDDD AABBCCDD
	#
	# Here, we convert our data into a 16-bit array, shift all values left
	# by 2-bits and unpack the low-order bits from every 5th byte in each
	# row, then remove the columns containing the packed bits

	data = data.astype(np.uint16) << 2
	for byte in range(4):
		data[:, byte::5] |= ((data[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
	data = np.delete(data, np.s_[4::5], 1)

	# Now to split the data up into its red, green, and blue components. The
	# Bayer pattern of the OV5647 sensor is BGGR. In other words the first
	# row contains alternating green/blue elements, the second row contains
	# alternating red/green elements, and so on as illustrated below:
	#
	# GBGBGBGBGBGBGB
	# RGRGRGRGRGRGRG
	# GBGBGBGBGBGBGB
	# RGRGRGRGRGRGRG
	#
	# Please note that if you use vflip or hflip to change the orientation
	# of the capture, you must flip the Bayer pattern accordingly
	'''
	rgb = np.zeros(data.shape + (3,), dtype=data.dtype)
	rgb[1::2, 0::2, 0] = data[1::2, 0::2] # Red
	rgb[0::2, 0::2, 1] = data[0::2, 0::2] # Green
	rgb[1::2, 1::2, 1] = data[1::2, 1::2] # Green
	rgb[0::2, 1::2, 2] = data[0::2, 1::2] # Blue
	'''
	
	green = data[0::2, 0::2] + data[1::2, 1::2]
	green <<= 5
	
	return green


# run as standalone script
if __name__ == '__main__':
	print('capturing bayer...')
	green_bayer = capture_green(shutter_speed=50000)
	print('shape: ', green_bayer.shape)
	imshow(green_bayer)
	show()
	
