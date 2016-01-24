import preferences as pref
import picamera
import 




'''
Setting up the camera
'''
def setupCamera():
	with picamera.PiCamera() as camera:
	
		camera.resolution = pref.resolution
		camera.framerate = pref.framerate
		camera.iso = pref.iso
		camera.awb_mode = 'off'

		time.sleep(2)

		print('Camera is ready...')

'''
Capture an RGB Image 
'''
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
	
	#returns numpy array
	return rgbCapture.array

'''
Streams the camera view on the screen
'''
def monitor():
	fullscreen_mode = False

	window_width = int(pref.monitor_size*800)
	window_heigth = int(0.75*window_width)

	screen_width = 1920
	screen_heigth = 1080

	v_flip = True
	h_flip = True

	setupCamera()

	camera.start_preview(fullscreen=fullscreen_mode, vflip=v_flip, hflip=h_flip, window=(screen_width-window_width,screen_height-window_height,window_width,window_height))

	print('Monitor is streaming...')

	while True:
		
		time.sleep(2)
