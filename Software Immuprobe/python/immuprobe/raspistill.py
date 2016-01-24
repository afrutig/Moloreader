#!/bin/env python2

'''
Python wrapper for /opt/vc/bin/raspistill
'''

import os
from skimage.io import imread, imshow, show
import numpy as np
from PIL import Image
_raspistill_cmd = '/opt/vc/bin/raspistill'
_raspiyuv_cmd = '/opt/vc/bin/raspiyuv'
_capture_tmp = '/tmp/capture.tmp'
_resolution = (2592,1944)


def _raspistill(shutter_speed, light_color, resolution):
	# call raspistill
	args = (_capture_tmp, shutter_speed, resolution[0], resolution[1])
	os.system(_raspistill_cmd + ' -t 1 -o %s -n -ex off -awb off --shutter %i -w %i -h %i -e bmp'%args)

def _raspistill_yuv(shutter_speed, light_color, resolution):
	# call raspistill
	args = (_capture_tmp, shutter_speed, resolution[0], resolution[1])
	os.system(_raspiyuv_cmd + ' -t 1 -o %s -n -ex off -awb off --shutter %i -w %i -h %i -rgb'%args)
	
def capture_yuv(shutter_speed=100000, light_color='blue', resolution=_resolution):

	_raspistill_yuv(shutter_speed=shutter_speed, light_color=light_color, resolution=resolution)
	
	file = open(_capture_tmp, 'rb')
	img = Image.frombytes('RGB', resolution, file.read())
	img = np.array(img)	
	return img

def capture(shutter_speed=100000, light_color='blue', resolution=_resolution):

	_raspistill(shutter_speed=shutter_speed, light_color=light_color, resolution=resolution)
	
	img = imread(_capture_tmp)
	
	return img
	
# run as standalone script
if __name__ == '__main__':
	print('testing '+__file__)
	
	print('capturing...')
	image = capture(shutter_speed=100000)
	print('display image...')
	imshow(image)
	show()
