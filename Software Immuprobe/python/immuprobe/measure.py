#!/bin/env python2

'''
Provides high level functions to measure the intensity of spots in an image.
'''

from detection import detectSpots

from collections import namedtuple
from math import sqrt
import numpy as np
from skimage import draw
from skimage.transform import rescale
from skimage.filters import gaussian_filter
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.color import rgb2gray

import argparse
import os.path
from skimage.io import imread, imshow, show


from matplotlib import pyplot as plt # for testing

Spot = namedtuple('Spot', 'mean std x y')

'''
High-level measurement function.
Takes an image, finds the spots and measures them.

@param image 	The raw data array.
@param spots	The locations and radii of the spots. [(x,y,r), ...]
@param inspectionMask	Undocumented feature. (used to see which pixels really get evaluated)

Returns: Uncalibrated raw measurements. [(mean, std_dev), ...]
'''
def measure_raw(image, spots, inspectionMask=None):
		
	# test if spots don't cross image borders
	w, h = image.shape
	for x,y,r in spots:
		# calculate min. distances to image borders
		dx = min(x, w-x)
		dy = min(y, h-y)
		
		if dx <= r or dy <= r:
			raise Exception('Spot intersects image borders (%i, %i)'%(x,y))
		
	values = _measureSpots(image, spots, inspectionMask)
	
	return values
	

 
'''
Create a list of indices pointing to the filled circle with 'radius' around (0, 0)

Returns: list of (x,y) tuples.
'''
def __createMask(radius):
	assert(radius > 0)
	return draw.circle(0, 0, radius)	# indices to filled circle around (0,0)

'''
Calculate average and standard deviation over the mask.

Params:
	image	=	The 2D array containing the raw data.
	mask	=	Not actually a mask but a array of indices pointing to the area of a filled circle around (0,0).
	offset	=	The location of the spot. This is added to the mask indices an thus the mask gets shifted by 'offset'.
	
Returns: Average value and standard deviation of pixels referred by mask+offset: (mean, standard deviation)
'''
def __measureSpot(image, mask, offset, inspectionMask=None):
	x, y = mask
	x0, y0 = offset
	
	#mean = np.mean(image[x+x0, y+y0])
	
	s = sorted(image[x+x0, y+y0])	# sort values
	start = int(round(len(s)*0.1))
	end = int(round(len(s)*0.9))
	
	s = s[start:end]
	
	mean = np.mean(s)	# average
	std = np.std(s)/np.sqrt(len(s))	# standard deviation
	
	# median
	#medianIndex = int(round(len(s)*0.5))
	#mean = s[medianIndex]
	
	#image[x+x0, y+y0] = 255 # mark measured area
	
	if inspectionMask is not None:
		# copy the measured pixels into the inspection array
		inspectionMask[x+x0, y+y0] = image[x+x0, y+y0]
		
	
	return Spot(mean, std, x0, y0)


'''
Returns: List of measured (value, standard deviation) tuples.

Params:
	image	=	Raw data.
	spots	=	Location and size of spots. (x,y,r)-Tuples.
'''
def _measureSpots(image, spots, inspectionMask=None):
	
	assert(len(spots) > 0)
	
	# determine radius
	radius = int(round(np.mean(spots[:,2])))
	
	# create the mask indices
	mask = __createMask(radius)
	
	#values = [(measureSpot(image, mask, blob[:2]), blob[:2]) for blob in spots] # (value, x, y)
	values = [__measureSpot(image, mask, blob[:2], inspectionMask) for blob in spots]

	return values


# run as standalone script
# used for testing
if __name__ == '__main__':
	
	from capture import capture
	
	# Get the filename form the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = False,
		help = "Path to the image to be scanned")
	args = vars(ap.parse_args())

	if(args["image"] is None):
		print("usage: measure.py -i [image]")
		print("using capture.py for image aquisition")
		
		image = capture(shutter_speed=200000)
	else:	
		if(not os.path.isfile(args["image"])):
			print("not a file")
			exit()

		# read image as grayscale
		image = imread(args["image"], as_grey=True)
	
	#image = rescale(image, scale=0.5)
	# remove noise
	#image = gaussian_filter(image, 1)
	
	inspectionMask = np.zeros(image.shape)
	
	spot_size=image.shape[0] * 0.05
	locations = detectSpots(image, spot_size)
	rawValues = measure_raw(image, locations, inspectionMask=inspectionMask)
	
	values = [v.mean for v in rawValues]
	stdDevs = [v.std for v in rawValues]
	
	print("raw measurement: ", rawValues)
	
	# plot results
	
	fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 4.5))
	
	ax1.imshow(image, cmap='gray')
	ax1.set_title('Original')
	
	ax2.imshow(image, cmap='gray')
	ax2.set_title('Borders')
	
	ax3.imshow(inspectionMask)
	ax3.set_title('Masked')
	
	radius = np.mean(locations[:,2])
	index = 0
	for spot in locations:
		x, y, r = spot
		c = plt.Circle((y, x), radius, color=(1, 0, 0), linewidth=2, fill=False)
		ax2.add_patch(c)
		# text label
		ax2.text(y, x-radius, '%d'%index,
                ha='center', va='bottom', color='w')
		#ax3.add_patch(c)
		index += 1
		
	# plot values
	ax4.set_title('raw measurements')
	ax4.grid(True)
	ind = np.arange(len(values))
	bars_raw = ax4.bar(ind, values, width=0.25, color='gray', yerr=stdDevs)
	
	fig.subplots_adjust(hspace=0.2, wspace=0.2)
	
	
	plt.show()
	
	'''
	# TODO: plot histogram of pixels
	pixels = np.reshape(inspectionMask, len(inspectionMask)*len(inspectionMask[0]))
	pixels = [p for p in pixels if p > 0] # filter 0s
	
	num_bins = 50
	# the histogram of the data
	n, bins, patches = plt.hist(pixels, num_bins, normed=1, facecolor='green', alpha=0.5)
	
	plt.show()
	'''
	
