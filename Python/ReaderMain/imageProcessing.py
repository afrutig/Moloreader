import cameraFunctions as cF
import numpy as np 
import preferences as pref



'''
Isolates the red channel, e.g. sets the others to 0.
'''
def isolateRED(image):

	try:
		image[:,:,[1,2]] = 0
	print('RED channel is isolated...')
	return image

'''
Gets rid of dark (not bright, with values under the treshold) red tones in the image, by setting them to 0. 
'''
def cutoffRED(image):
	

	(rowlength,columnlength,depth) = image.shape 

	for row in range(0,rowlength)
		for column in range(0,columnlength)
			if image[row,column,pref.color_channel]<= pref.treshold
				image[row,column,pref.color_channel] = 0

	return image
'''	
Counts the number of non-zero entries in the red-matrix of the image
'''
	
def getPixels(image):

	pixels = np.count_nonzero(image[:,:,pref.color_channel])

	return pixels

