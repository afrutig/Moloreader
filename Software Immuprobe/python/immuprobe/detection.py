#!/bin/env python2

'''
Detection of sample spots in the raw image.
'''

from math import sqrt
import numpy as np
from skimage import draw
from skimage.transform import rescale, hough_circle
from skimage.filters import gaussian_filter, threshold_adaptive, threshold_otsu, sobel
from skimage.feature import blob_dog, blob_log, blob_doh
from skimage.feature import peak_local_max, canny
from skimage.morphology import watershed
from scipy.signal import argrelmax
from scipy import ndimage as ndi

from skimage.io import imshow, show

_spot_size_margin = 0.707 # makes detected radii smaller to avoid evaluating pixels at the border

'''
Finds the 25 spots in the image and returns their locations.

Performance is best if contrast is high.

@param image	High contrast image.
@param spot_size	Radius of spots to be detected.
@param scaledown	Rescale the image by this amount before processing. Leads to a remarkable speedup.
'''
def detectSpots(image, spot_size, scaledown=1):
	print('detectSpots')
	if(scaledown <= 1):
		smallImg = rescale(image, scaledown)
	else:
		# Scaling up would not make sense.
		scaledown = 1
		smallImg = image
	
	seg = _segment_watershed(smallImg)
	#seg = _segment_threshold(smallImg)
	spots = _detect_spots_from_segmentation(seg)

	#spots = _detect_spots_localmax(smallImg, spot_size*scaledown)
	#spots = _detect_spots_hough_circle(smallImg, spot_size*scaledown)
	#spots = _detect_spots_blob_log(smallImg, spot_size*scaledown)
	spots = spots/scaledown
	spots = np.round(spots)
	spots = spots.astype(int)
	
	if(len(spots) < 25):
		raise Exception('Did not find all spots. %i instead %i'%(len(spots), 25))
	
	spots = _sortPoints(spots);
	
	return spots
'''
Detect bright spots in the image.
No filtering or ordering is done.

Params:
	image	=	The image showing detectable spots.

Returns: list of (x, y, radius)-tuples
'''
def _detect_spots_localmax(image, radius):

	orig_image = image
	image = gaussian_filter(image, radius/2)
	
	
	mindist = radius*2	# find local max. that have a distance of at least 2*radius
	m = peak_local_max(image, min_distance=mindist)	# find local maxima which are exptected to be on the spots
	m = sorted(m, key=lambda s: -image[s[0], s[1]])	# sort by intensity
	
	m = m[0:25]	# take the 25 spots with maximum intensity

	blobs = np.array([(x,y,radius) for x,y in m])

	return blobs

'''
Use simple threshold to distinguish spots from background.
'''
def _segment_threshold(image):
	
	thresh = threshold_otsu(image)
	seg = image > thresh

	seg = ndi.binary_fill_holes(seg)	# fill holes
	
	return seg

'''
Use watershed segmentation to distinguish spots from background.
'''
def _segment_watershed(image):
	elevation_map = sobel(image)
	markers = np.zeros(image.shape) # initialize markers as zero array 

	
	# determine thresholds for markers
	sorted_pixels = np.sort(image, axis=None)
	max_int = np.mean(sorted_pixels[-10:])
	min_int = np.mean(sorted_pixels[:10])
	#max_int = np.max(orig_image)
	#min_int = np.min(orig_image)
	
	alpha_min = 0.01
	alpha_max = 0.4
	thresh_background = (1-alpha_min)*min_int	+	alpha_min*max_int
	thresh_spots = 		(1-alpha_max)*min_int	+	alpha_max*max_int
	
	markers[image < thresh_background] = 1 # mark background
	markers[image > thresh_spots] = 2 # mark background
	
	segmentation = watershed(elevation_map, markers)
	segmentation = segmentation-1
	segmentation = ndi.binary_fill_holes(segmentation)	# fill holes
	
	return segmentation

'''
Extracts spot locations and radii from segmented image.
@param	segmentation An image segmented into spots and background.

@return [(x,y,radius), ...]
'''
def _detect_spots_from_segmentation(segmentation):

	labeled, n = ndi.label(segmentation)
	#imshow(markers)
	#show()
	#imshow(labeled)
	#show()
	if n != 25:
		print('Found %i spots instead of 25.'%n)
		
	centers = ndi.center_of_mass(segmentation, labeled, np.arange(0,25)+1)
	
	def radius(x,y):
		i = labeled[x,y]
		area = np.sum(labeled == i)
		r = np.sqrt(area/np.pi)
		return r

	blobs = np.array([(x,y,radius(x,y)*_spot_size_margin) for x,y in centers])
	blobs = _reduceToCluster(blobs)
	return blobs
	
def _detect_spots_hough_circle(image, radius):
	edges = canny(image)
	imshow(edges)
	show()
	hough_radii = np.arange(radius/2, radius*2, 10)
	hough_circles = hough_circle(edges, hough_radii)
	
	print(hough_circles)
	# TODO .....
	
'''
Use scikit-image blob_log algorithm to detect spots. This is rather slow.
'''
def _detect_spots_blob_log(image, minSpotSize):
	
	maxSpotSize = minSpotSize
	spotSizeSteps = 1
	
	# find blobs starting from min_sigma to max_sigma in num_sigma steps
	blobs = blob_log(image, min_sigma=minSpotSize, max_sigma=maxSpotSize, num_sigma=spotSizeSteps, threshold=.005) # blobs_log = (y, x, r)
	
	return blobs

'''
Sort points lying on a 5x5 grid such that indices look like:
 
 0	1	2	3	4
 5	6	7	8	9
10	11	...
			...	24

Params:
		points	=	List of (x,y,...)-tuples.

Returns: sorted list, same data type as input.
'''
def _sortPoints(points):
	points = sorted(points, key=lambda p: p[0]) # sort by y
	
	for i in range(0,5):
		points[5*i:5*i+5] = sorted(points[5*i:5*i+5], key=lambda p: p[1]) # sort by x

	return np.array(points)


'''
Remove outliers by successively removing the point that is the furthest away from the center of gravity.

Returns: A list of at most 'clusterSize' points.
'''
def _reduceToCluster(blobs, clusterSize=25):
	# arithmetic center of the blobs
	mean = np.mean(blobs, axis=0)
	
	# Calculate distance between two points squared.
	def hyp2(a, b):
		return (a[0]-b[0])**2 + (a[1]-b[1])**2
	
	# As long as there are more than 25 points remove the one furthest from the average.
	while len(blobs) > clusterSize:
		blobs = sorted(blobs, key=lambda p: hyp2(p, mean))
		blobs = blobs[:-1]
		mean = np.mean(blobs, axis=0)
		
	assert(len(blobs) <= clusterSize)
	return np.array(blobs)
