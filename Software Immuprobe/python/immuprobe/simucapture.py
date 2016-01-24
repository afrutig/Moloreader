'''
Simulation of the Immuprobe camera hardware. Used for development only.
'''

from skimage import draw
from scipy.ndimage.filters import gaussian_filter
import numpy as np
from numpy.random import normal
from numpy import sqrt, exp
from time import sleep

_number_of_spots = 25

class SimuCapture:
	'''
	Simulated raw data acquisition.

	Simulation of the Immuprobe camera hardware. Used for development only.
	'''

	def __init__(self):
		# sample values
		self._values = np.linspace(0,255,_number_of_spots)#+normal(0, 0.1, 25)
		self._values[0:4] = 0	# negative controlls
		
		# set random values
		self._sample_rotation = normal(0, np.pi/128)

		self._offsetX, self._offsetY = (normal(1./2, 1./10), normal(1./2, 1./10))

		stddev = 0.005
		self._spotOffsetsX = normal(0, stddev, _number_of_spots)
		self._spotOffsetsY = normal(0, stddev, _number_of_spots)
			
		# init radii
		self._rad = normal(1, 0.01, _number_of_spots)

	def capture(self, shutter_speed=None, light_color='blue', resolution=(800, 600)):
		try:
			print('lights on', light_color)
			'''
			Synthesize an image.
			'''
		
			if shutter_speed is None:
				shutter_speed = self._shutter_speed
		
			image = self._createSignal(resolution, high_contrast=(light_color == 'green'))
			
			f = 1 if light_color == 'green' else 0.25	# reduce signal strength when using blue lights
			image = image * (shutter_speed/20000.) * f
			
			image = _applyChannel(image, shutter_speed)	# add noise, ...
			
			sleep(shutter_speed/1e6)
			
			return image
		finally:
			print('lights off', light_color)
				
	# Create the 25 spots.
	def _createSignal(self, resolution, high_contrast=False):
		resolution = (resolution[1], resolution[0])
		image = np.zeros(resolution, dtype=np.float32)
		#image = normal(20, 200, resolution)	# 'noise' on the sample
		#image = gaussian_filter(image, 16)
		
		w,h = image.shape
		
		# center
		x0, y0 = (self._offsetX*w, self._offsetY*h)
		
		theta = self._sample_rotation # angle of sample
		d = image.shape[0]*0.1	# distance between spots
		
		
		l = 5	# grid size
		stddev = 0.01
		cordy = -(np.floor(np.arange(l**2)%l)-l/2)
		cordx = np.floor(np.arange(l**2)/l)-l/2
		
		
		cordx += self._spotOffsetsX
		cordy += self._spotOffsetsY
		
		cordx, cordy = (np.cos(theta)*cordx+np.sin(theta)*cordy, np.sin(theta)*cordx - np.cos(theta)*cordy)
		
		cordx *= d
		cordy *= d
		
		cordx += x0
		cordy += y0
		
		rad = self._rad*0.08*d # radii of spots
		
		if not high_contrast:
			values = self._values
		else:
			values = [200]*_number_of_spots
		
		for (x,y,r,v) in zip(cordx,cordy,rad,values):
			_drawSpot(image, (x, y), r, v)
		
		return image


def _drawSpot(image, coords, radius, brightness):
	'''
	Draw a single spot at given location.
	
	@param image	Container numpy array.
	@param coords	Location of spot.
	@param radius	Spot size.
	@param	brightness	Spot luminosity.
	'''

	maskX, maskY = _createMask(radius*4)
	
	b = np.exp(-(maskX**2+maskY**2)/(16*radius**2))*brightness
	#b = brightness

	maskX = np.uint(maskX + np.round(coords[0]))
	maskY = np.uint(maskY + np.round(coords[1]))
	
	image[maskX, maskY] += b

def _createMask(radius):
	assert(radius > 0)
	return draw.circle(0, 0, radius)	# indices to filled circle around (0,0)

		
# add noise, offset, distortion, ...
def _applyChannel(image, shutter_speed):
	# add gaussian noise
	
	# blur
	image = gaussian_filter(image, 2)
	#noise_sigma = 2000/(sqrt(shutter_speed)+100)
	noise_sigma = 4
	hf_noise = normal(noise_sigma, noise_sigma, image.shape)
	image += hf_noise
	
	#nf_noise = gaussian_filter(normal(0, 200, image.shape), image.shape[0]/10)
	#image += nf_noise
	
	
	# camera chip limits
	image = np.maximum(image, 0)
	image = np.minimum(image, 255)
	image = np.uint8(image)
	
	return image
