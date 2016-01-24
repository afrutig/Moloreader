import numpy 
import picamera
import time

with picamera.Picamera() as camera

def setupCamera():

	with picamera.PiCamera() as camera:
	
		camera.resolution = (2592,1944)
		camera.framerate = 15

		time.sleep(2)

		print('Camera is ready...')

def captureRGB(shutter_speed, resolution):
	camera = None
	try:
		setupCamera()

		rawCapture = PiRGBArray(camera)
		print('capture...')

		camera.capture(rgbCapture, format="rbg")
		print('done')
			
	except:
		if camera is None:
			raise Exception('Failed to initialize PiCamera.')
		else:
			raise Exception('Failed to capture image.')
			
	finally:
		if camera is not None:
			camera.close()
		
	return rgbCapture.array