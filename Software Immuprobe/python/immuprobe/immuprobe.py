#!/bin/env python2

'''
High-level access to the IMMUPROBE fluorescence reader.
'''

import numpy as np
from statistics import ExpData, ExpResult, deserialize_exp_result
import capture
from measure import measure_raw

from skimage.io import imshow, show, imread, imsave
from skimage.color import rgb2gray

import plot
import lights

_contrast_image_resolution = (2592/4,1944/4)
_contrast_image_exposure_time = 40000

class Immuprobe(object):
	
	def __init__(self):
		self._calibrationData = dict()
		self._iso = 100
		self._shutter_speed = 30000
		self._resolution = (2592,1944)
		#self._resolution = (1600,1200)
		
		# init default category map
		d = dict()
		for i in range(0,25):
			d[i] = str(i)
			
		self._categoryMap = d
	
	'''
	Calibrate the experiment with previously known concentrations.
	
	Params: calibrationData	=	List of concentrations. TODO: dict[spot => value]
		
	'''
	def calibrate(self, calibrationData):
		def isnumeric(obj):
			try:
				obj + 0
				return True
			except TypeError:
				return False
		
		'''
		Check if input is apropriate.
		'''
		if(type(calibrationData) is dict):
			for k,v in calibrationData.items():
				assert(type(k) is int)
				assert(isnumeric(v))
		else:
			for v in calibrationData:
				assert(isnumeric(v))
		
				
		self._calibrationData = calibrationData

	
	#Returns: the available categories as list
	@property
	def categories(self):
		return list(set(self._categoryMap.values()))
		
	@property
	def categoryMap(self):
		return self._categoryMap
	
	'''
	Params: cat = dict of spot categories, {number of spot : category name}
	Post: categories are set to cat
	'''
	@categoryMap.setter
	def categoryMap(self, cat):
		for k,v in cat.items():
			assert(k >=0 and k < 25)
		self._categoryMap.update(cat)
	
	@property
	def caldata(self):
		if(self._calibrationData is None):
			raise Exception('Immuprobe is not calibrated.')

		return self._calibrationData
		

	@property
	def iso(self):
		return self._iso
		
	@iso.setter
	def iso(self, value):
		self._iso = value
		
	@property
	def shutter_speed(self):
		return self._shutter_speed
		
	@shutter_speed.setter
	def shutter_speed(self, value):
		self._shutter_speed = int(value)
		
	@property
	def resolution(self):
		return self._resolution
		
	@resolution.setter
	def resolution(self, val):
		self._resolution = val

	# capture an image for preview
	def image_preview(self, shutter_speed=None, resolution=None, light_color='blue', auto_exposure=False):
		img = capture.capture(shutter_speed=shutter_speed or self.shutter_speed, resolution=resolution or self.resolution, light_color=light_color, auto_exposure=auto_exposure)	
		return img

	'''
	Does the measurement and evaluation.
	Call calibrate() first
	
	@param image Evaluate this image instead of a picture taken with the camera.
	
	Returns:	A dict containing all experiment data.
				dict keys:	values	=	The concentrations.
							std_dev =	Standard deviation of values. (standard deviation of pixel noise)
							raw_image	=	The captured image.
							calibration_data	=	The datapoints used for calibration as a dict. {index: calibratoin value}
	
	Throws: Might throw exception
	'''
	def measure(self, blueImage=None, contrastImage=None):
		if(self._calibrationData is None):
			raise Exception('Immuprobe is not calibrated!')
		
		if blueImage is None:
			# get raw data
			contrastImage = self.capture_green()
			blueImage = self.capture_blue()
		
		expData = ExpData(signalImage=blueImage, contrastImage=contrastImage)
		expResult = ExpResult(expData)
		#expData._evaluateImage()
		
		expResult.calibrationMap = self._calibrationData
		expResult.categoryMap = self.categoryMap

		return expResult
		
	def capture_blue(self):
		#return capture.capture_auto_exposure(initial_shutter_speed=self.shutter_speed, resolution=_contrast_image_resolution, light_color='blue')
		return capture.capture(shutter_speed=self.shutter_speed, resolution=self.resolution, light_color='blue')
		
	def capture_green(self):
		#return capture.capture_auto_exposure(initial_shutter_speed=self.shutter_speed, resolution=_contrast_image_resolution, light_color='green')
		return capture.capture(shutter_speed=_contrast_image_exposure_time, resolution=_contrast_image_resolution, light_color='green')
		

			

'''
Returns: ExpResult
'''
def deserialize_result(serialized):
	return deserialize_exp_result(serialized)
	

def setLight(color, value):
	lights.setLight(color, value)

if __name__ == '__main__':
	print('testing '+__file__)
	
	ip = Immuprobe()
	ip.shutter_speed = 10000
	
	# calibration with dict
	ip.calibrate({0:0,1:0,2:0,3:0,4:4,5:5,6:6,7:7,8:8})
	
	ip.categoryMap = {4:'fred', 5:'fred', 6: 'fred', 8: 'henry', 9: 'henry'}
	
	result = ip.measure()
	
	
	print('calibration data: ', result.calibration_data)
	print('concentrations: ', result.concentrations)
	print('categorized: ', result.categorized)
	print('negative controls', result.negative_controls_indices)
	print('background intensity: ', result.background_intensity)
	print('background concentration: ', result.intensity_to_concentration(result.background_intensity))
	print('LoD', result.limit_of_detection)
	print('LoQ', result.limit_of_quantification)
	print('fitted curve', result._intensity_to_concentration(1)-result._intensity_to_concentration(0), result._intensity_to_concentration(0))
	
	ser = result.serialize
	result = deserialize_exp_result(ser)
	
	print(result.asCSV)

	fig = plot.plot_overview(result, encoding=None)
	print(fig)
	#plot.plot_standard_curve(result, encoding=None, show=True)
	#plot.plot_signal_to_noise(result, encoding=None, show=True)
	
