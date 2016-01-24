import numpy as np
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

def isolateRED(image):

	try:
		image[:,:,[1,2]] = 0
	print('RED channel is isolated...')
	return image

def cutoffRED(image,treshold):
	

	(rowlength,columnlenth,depth) = image.shape 

	for row in range(0,rowlength
		for column in range(0,columnlength)
			if image[row,column,0]<= threshold
				image[row,column.channel] = 0

	return image				
	
def getPixels(image):

	pixels = np.count_nonzero(image[:,:,0])

	print('the ')

	return pixels








