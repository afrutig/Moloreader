#!/bin/env python2
# see http://picamera.readthedocs.org/en/release-1.10/
# http://picamera.readthedocs.org/en/release-1.10/api_array.html#piyuvarray


from picamera.array import PiRGBArray, PiBayerArray
from picamera import PiCamera
import time
from skimage.io import imshow, show, imsave
import numpy as np
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
 
# allow the camera to warmup
time.sleep(1)

# fix camera parameters
camera.resolution = (2592,1944) # max. resolution
camera.framerate = 1

camera.exposure_mode = 'off'
camera.shutter_speed = 50000 # microseconds
print("shutter", camera.shutter_speed)

g = camera.awb_gains # get some reasonable gains

camera.awb_mode = 'off'
camera.awb_gains = (1,1) # (red, blue)
camera.iso = 10
print("iso", camera.iso)

# raw bayer capture
bayerCapture = PiBayerArray(camera)
camera.capture(bayerCapture, 'jpeg', bayer=True) # grab the 10 bit resolution with the raw bayer data

imageBayer = bayerCapture.demosaic()
#imageBayer = imageBayer / 4
#imageBayer = imageBayer.astype(np.uint8)
print(imageBayer)

#camera.capture(rawCapture, format="yuv") # using yuv instead of rgb
#camera.capture(rawCapture, format="bgr") # using yuv instead of rgb
image = imageBayer

imsave('bayer.tiff', image)
