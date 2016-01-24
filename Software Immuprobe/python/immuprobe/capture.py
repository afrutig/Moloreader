#!/bin/env python2

'''
Controlling camera and illumination.
'''

from skimage.io import imshow, show, imread
from skimage.color import rgb2gray
import numpy as np
import lights
from time import sleep
import raspistill
import lights
# defaults
_iso = 100
_shutter_speed = 20000
_max_resolution = (2592,1944)
_resolution = _max_resolution
_max_exposure_time = 6000000

_initial_shutter_speed = 100000 # first exposure time to try when using auto_exposure

try:
	from picamera.array import PiRGBArray, PiYUVArray, PiBayerArray
	from picamera import PiCamera
	import bayer
	
	'''
	Set camera parameters.
	'''
	def _setup_camera(camera, resolution, shutter_speed, iso):
		
		# fix camera parameters
		camera.resolution = resolution # max. resolution
		camera.framerate = 2
		
		camera.exposure_mode = 'off'
		camera.shutter_speed = int(shutter_speed) # microseconds
		
		#g = camera.awb_gains # get some reasonable gains
		
		camera.awb_mode = 'off'
		camera.awb_gains = (1,1) # (red, blue)
		camera.iso = int(iso)
	
	'''
	Returns: Numpy array of RGB image.
	'''
	def _captureRGB(shutter_speed, resolution):
		camera = None
		try:
			camera = PiCamera()
			_setup_camera(camera, resolution, shutter_speed, _iso)
			
			rawCapture = PiRGBArray(camera)
			print('capture...')
			camera.capture(rawCapture, format="bgr")
			print('done')
			
		except:
			if camera is None:
				raise Exception('Failed to initialize PiCamera.')
			else:
				raise Exception('Failed to capture image.')
			
		finally:
			if camera is not None:
				camera.close()
		
		return rawCapture.array

	'''
	Returns: Numpy array of YUV image.
	'''
	def _captureYUV(shutter_speed, resolution):
		camera = None
		try:
			camera = PiCamera()
			_setup_camera(camera, resolution, shutter_speed, _iso)
			
			rawCapture = PiYUVArray(camera)
			print('capture...')
			camera.capture(rawCapture, format="yuv")
			print('done')
			
		except Exception, e:
			traceback.print_exc()
			if camera is None:
				raise Exception('Failed to initialize PiCamera.')
			else:
				raise Exception('Failed to capture  YUV image.')
			
		finally:
			if camera is not None:
				camera.close()
		
		return rawCapture.array
	
	'''
	Returns: 
	'''
	def _captureBayer(shutter_speed):
		camera = None
		try:
			camera = PiCamera()
			_setup_camera(camera, _max_resolution, shutter_speed, _iso)
			
			rawCapture = PiBayerArray(camera)
			print('capture...')
			bayerCapture = PiBayerArray(camera)
			camera.capture(bayerCapture, 'jpeg', bayer=True) # grab the 10 bit resolution with the raw bayer data

			imageBayer = bayerCapture.demosaic()
			print('done')
			
		except:
			if camera is None:
				raise Exception('Failed to initialize PiCamera.')
			else:
				raise Exception('Failed to capture image.')
			
		finally:
			if camera is not None:
				camera.close()
		
		return imageBayer
		
	'''
	Returns: Numpy array grascale image.
	'''
	def capture(shutter_speed=_shutter_speed, light_color='blue', resolution=_resolution, auto_exposure=False):
		
		if auto_exposure:
			return _auto_exposure(light_color=light_color, resolution=resolution)
		else:
			try:
				lights.setLight(light_color, 1)		# turn the lights on

				if resolution == _max_resolution:
					print('capturing raw bayer data')
					#img = _captureBayer(shutter_speed)
					img = bayer.capture_green(shutter_speed)
					# convert to pseudo 16 bit format
					#img = img << 6
					print(img.dtype)
					print(img.shape)
				else:
					#img = raspistill.capture(shutter_speed=shutter_speed, light_color=light_color, resolution=resolution)
					img = _captureRGB(shutter_speed, resolution)
					img = img[:,:,1] # take green channel

				
				return img
				
			finally:
				lights.setLight(light_color, 0)		# turn the lights off
	
except ImportError:
	from simucapture import SimuCapture
	
	print('PiCamera not supported. Using simulated camera.')
	_simucapture = SimuCapture()
	
	def capture(shutter_speed=_shutter_speed, light_color='blue', resolution=_resolution, auto_exposure=False):
	
		if auto_exposure:
			img = _auto_exposure(light_color=light_color, resolution=resolution)
		else:
			img = _simucapture.capture(shutter_speed=shutter_speed, light_color=light_color, resolution=resolution)
		
		return img


'''
Capture an image and adjust the shutter speed such that the maximum brightness in the image is 'desired_max +/- tolerance'

@param initial_shutter_speed	The shutter speed to try first.
@param desired_max	Desired maximal brighness in the image, must be below 255.
@param tolerance	Tolerance for maximum brighness
@param light_color	blue or green
'''
def _auto_exposure(initial_shutter_speed=_initial_shutter_speed, desired_max=240, tolerance=10, light_color='blue', resolution=_resolution):
	assert(desired_max <= 255)
	shutter_speed = initial_shutter_speed
	max_brightness = float('nan')
	
	while not (np.abs(max_brightness - desired_max) < tolerance and shutter_speed < _max_exposure_time):
		#print('shutter-speed: %i'%shutter_speed)
		img = capture(shutter_speed=shutter_speed, resolution=resolution, light_color=light_color)
		
		highscore = np.sort(img, axis=None)
		max_brightness = np.mean(highscore[-200:]) # average over the brightest pixels to reduce noise
		
		#print('max: %d'%max_brightness)
		
		if max_brightness == 255:
			# saturated
			shutter_speed *= 0.5
		elif max_brightness == 0:
			shutter_speed *= 10
		else:
			shutter_speed *= 1.*desired_max/max_brightness
	print('auto shutter speed: %f'%shutter_speed)		
	return img

# run as standalone script
if __name__ == '__main__':
	print('testing '+__file__)
	
	print('capturing...')
	image = capture(shutter_speed=100000)
	print('display image...')
	imshow(image)
	show()
