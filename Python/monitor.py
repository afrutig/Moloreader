import time 
import picamera
import preferences

#Settings 

fullscreen_mode = False

window_width = 800
window_heigth = 0.75*window_width

screen_width = 1920
screen_heigth = 1080

v_flip = True
h_flip = True

#main

with picamera.PiCamera() as camera:
	
	camera.resolution = (2592,1944)
	camera.framerate = 15

	camera.start_preview(fullscreen=fullscreen_mode, vflip=v_flip, hflip=h_flip, window=(screen_width-window_width,screen_height-window_height,window_width,window_height))

	while True:
		
		time.sleep(1)
