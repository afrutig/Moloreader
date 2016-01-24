#!/bin/env python2

'''
Representation and evaluation of experiment results.
'''

import numpy as np
from collections import namedtuple

from measure import measure_raw
from detection import detectSpots

from measure import measure_raw
import curvefit

import pickle
import zipfile
import tempfile
import os
import plot

from datetime import datetime

# Relative spot radius compared to the width of the image.
_rel_spot_size = 0.04

# IPR file format version
_version = 0

	
'''
Container for experimental results.
'''
class ExpData(object):
	
	'''
	@param signalImage	The image with the relevant data, captured with blue light.
	@param contrastImage	Hight-contrast image for reliable spot detection.
	'''
	def __init__(self, signalImage, contrastImage=None):
		self._signalImage = signalImage
		self._contrastImage = contrastImage
		self._evaluateImage()
	
	'''
	Do the most intensive calculations: spot detection and measurement.
	'''
	def _evaluateImage(self):
		
		signalImage = self._signalImage
		contrastImage = self._signalImage if self._contrastImage is None else self._contrastImage
		
		spot_size = contrastImage.shape[0] * _rel_spot_size
		
		spots = detectSpots(contrastImage, spot_size).astype(float)
		
		# Rescale the coordinates and radii of the spots since 'contrastImage' might have another resolution than 'signalImage'.
		spots[:,0] *= signalImage.shape[0]/contrastImage.shape[0]
		spots[:,1] *= signalImage.shape[1]/contrastImage.shape[1]
		spots[:,2] *= signalImage.shape[1]/contrastImage.shape[1]
		
		spots = np.round(spots)
		spots = spots.astype(int)
	
		
		self._spots = spots
		
		self._values = measure_raw(signalImage, self._spots)
	
	'''
	Get locations of spots on image.
	'''
	@property
	def spot_locations(self):
		return self._spots

	'''
	Get list of raw spot values and their std. deviations.
	Returns: [(mean, stdDev), ...]
	'''
	@property
	def raw_values(self):
		return self._values
	
	'''
	Returns the average intensity of each spot.
	'''
	@property
	def values(self):
		return [v.mean for v in self.raw_values]
	
	'''
	Returns the standard deviation of the pixel values for each spot.
	'''
	@property
	def stdDevs(self):
		return [v.std for v in self.raw_values]

	@property
	def signalImage(self):
		return self._signalImage

	@property
	def contrastImage(self):
		return self._contrastImage
	
	'''
	Generates a number that is uniqe with high probability.
	Used for caching plots.
	'''
	def __hash__(self):
		return hash(np.array(self.raw_values).tostring()) \
		^ hash(self.spot_locations.tostring())*5


'''
Evaluates experimental results.
'''
class ExpResult(object):
	
	def __init__(self, expData, calibrationMap=None, categoryMap=None):
		self._calibrationMap = calibrationMap
		self._expData = expData
		self.meta = dict()	# container for meta tags such as date and time
		
		
		self._categoryMap = categoryMap
			
		if categoryMap is None:
			self._categoryMap = dict()
			# default categories
			for i in range(0,25):
				self._categoryMap[i] = str(i)
				
		self.meta['timestamp'] = datetime.now()

	@property
	def categoryMap(self):
		return self._categoryMap
		
	# Set a dict mapping spot numbers to category names.
	@categoryMap.setter
	def categoryMap(self, value):
		assert(type(value) is dict)
		assert(len(value.items()) <= 25)
		for k,v in value.items():
			assert(type(k) is int)
			assert(k >=0 and k<25)
			value[k] = str(v)
		self._categoryMap = value

	# Returns true if and only if calibrationMap is set.
	@property
	def isCalibrated(self):
		return self._calibrationMap is not None and len(self._calibrationMap.keys()) >= 2

	@property
	def calibrationMap(self):
		return self._calibrationMap or {0:0,1:0}
		
	@calibrationMap.setter
	def calibrationMap(self, calibMap):
		self._calibrationMap = calibMap

	'''
	Returns: The calibration points. x: given concentration, y: measured intensity.
		([x1, ...], [y1, ...])
	'''
	@property
	def calibration_data(self):
		concentrations = self.calibrationMap.values()
		intensities = [self.raw.values[i] for i in self.calibrationMap.keys()]
		
		return (concentrations, intensities)

	
	@property
	def calibration_data_indices(self):
		return self._calibrationMap.keys()

	# Returns raw experimental data as ExpData object.
	@property
	def raw(self):
		return self._expData
	
	'''
	Calculate the concentrations.
	If calibrationMap is not set raw intensities will be returned.
	'''
	@property
	def concentrations(self):
		
		if not self.isCalibrated:
			return self.intensities
		
		c,i = self.calibration_data
		return curvefit.evaluate_stddev(i,c, self.intensity_values, self.intensity_stddev) # cx,cy swapped to get inverse function
	
	@property
	def intensities(self):
		return (self.raw.values, self.raw.stdDevs)

	@property
	def intensity_values(self):
		return np.array(self.intensities[0])

	@property
	def intensity_stddev(self):
		return np.array(self.intensities[1])
		
	@property
	def concentration_values(self):
		return self.concentrations[0]	
			
		
	@property
	def concentration_stddev(self):
		return self.concentrations[1]
	
	'''
	Returns: f: concentration -> intensity
	'''
	@property
	def _concentration_to_intensity(self):
		c,i = self.calibration_data
		curve = curvefit.fittedCurve(c,i)
		return curve
			
	'''
	Returns: f: intensity -> concentration
	'''
	@property
	def _intensity_to_concentration(self):
		c,i = self.calibration_data
		curve = curvefit.fittedCurve(i,c)
		return curve
	
	# convert intensity to concentration
	def concentration_to_intensity(self, concentration):
		curve = self._concentration_to_intensity
		return curve(concentration)

	
	# convert concentration to intensity
	def intensity_to_concentration(self, intensity):
		curve = self._intensity_to_concentration
		return curve(intensity)
		
	# Returns a list of where the negative controls are.(example [0,12,15,24] -> negative controls at 0, 12, 15 and 24)
	@property
	def negative_controls_indices(self):
		x = self._calibrationMap
		lst = [i for i in x.keys() if x[i]==0]
		return lst
	
	#returns average background intensity.
	@property
	def background_intensity(self):
		val = np.array(self.raw.values)
		neg = val[self.negative_controls_indices]
		
		if len(neg) > 0:
			mean = np.mean(neg)
			std = np.std(neg)
			
			return (mean, std)
		else:
			# find background by extrapolation
			#cToI = self._concentration_to_intensity
			#return (cToI(0), 0)	# find intensity of zero concentration
			return (0,0)

	@property
	def limit_of_detection(self):
		bg_mean, bg_std = self.background_intensity
		lod = 1+ 3*bg_std
		return lod
		
	@property
	def limit_of_quantification(self):
		bg_mean, bg_std = self.background_intensity
		loq = 1+ 10*bg_std
		return loq

	'''
	Get locations of spots on image.
	'''
	@property
	def spot_locations(self):
		return self.raw.spot_locations
	
	'''
	Calculate mean over each category.
	Params:
		categoryMap = a dict {spot number: 'category name'}
		
	Returns: A dict: {'category name': mean}
	'''
	def _categorized(self, categoryMap):
		
		values, stdDevs = self.concentrations
		values = np.array(values)
		cats = categoryMap
		result = dict()
		for c in set(cats.values()):
			keys = [k for k in cats if cats[k] == c]
			avg = np.mean(values[keys])	# average over all spots in that category
			
			result[c] = avg
			
		return result

	'''
	Calculate mean over each category.
	Params:
		categoryMap = a dict {spot number: 'category name'}
		
	Returns: A dict: {'category name': mean}
	'''
	@property
	def categorized(self):
		return self._categorized(self.categoryMap)

	'''
	Generates a number that is uniqe with high probability.
	Used for caching plots.
	'''
	def __hash__(self):
		print(self.categoryMap.items())
		return hash(self.raw) \
		^ hash(np.array(self.concentrations).tostring())*17 \
		^ hash(np.array(sorted(self.categoryMap.items())).tostring())*23

	'''
	Convert ExpResult object to zip file.
	'''
	@property
	def serialize(self):
		temp = tempfile.NamedTemporaryFile(suffix='.zip.tmp', delete=True)
		zf = zipfile.ZipFile(temp.name, 'w')

		zf.writestr('.type', 'ExpResult')
		zf.writestr('.version', str(_version))
		
		# raw data
		zf.writestr('capture/signalImage', plot.img_compress(self.raw.signalImage, encoding='tiff'))
		if self.raw.contrastImage is not None:
			zf.writestr('capture/contrastImage', plot.png(self.raw.contrastImage))
			
		# calibration data
		zf.writestr('calibrationMap', pickle.dumps(self.calibrationMap))
		
		# categories
		zf.writestr('categoryMap', pickle.dumps(self.categoryMap))
		
		# meta data
		zf.writestr('meta', pickle.dumps(self.meta))
		
		zf.close()
		data = temp.read()
		temp.close()
		
		return data
		
	@property
	def asCSV(self):
		csv = ""
		
		header = "spot;category;intensity;concentration"
		
		csv += header+"\n"
		
		for s,i,cval in zip(range(25), self.intensity_values, self.concentration_values):
			cat = self.categoryMap[s] if s in self.categoryMap else ""
			line = "%i;%s;%f;%f\n"%(s,cat,i,cval)
			csv += line
		
		return csv
	
	'''
	Returns the time and date of the experiment.
	'''
	@property
	def timestamp(self):
		return self.meta['timestamp']

'''
Convert binary data to ExpResult object.
Counterpart to ExpResult.serialize.
'''
def deserialize_exp_result(binary_data):
	temp = tempfile.NamedTemporaryFile(suffix='.zip.tmp', delete=False)
	temp.write(binary_data)
	temp.close()
	zf = zipfile.ZipFile(temp.name, 'r')
	
	dataType = zf.read('.type')
	
	if dataType != 'ExpResult':
		raise Exception('Format error: not a ExpResult object.')
	
	version = zf.read('.version')
	if str(version) != str(_version):
		raise Exception('Version mismatch.')
		
	calibrationMap = pickle.loads(zf.read('calibrationMap'))
	categoryMap = pickle.loads(zf.read('categoryMap'))
	
	# load metadata
	try:
		meta = pickle.loads(zf.read('meta'))
	except:
		meta = dict()
		
	signalImage = plot.img_decompress(zf.read('capture/signalImage'))
	contrastImage = None
	
	try:
		contrastImage = plot.img_decompress(zf.read('capture/contrastImage'))
	except:
		print('No contrast image found.')
		
	zf.close()
	
	os.remove(temp.name)
	
	expData = ExpData(signalImage, contrastImage)
	
	expResult = ExpResult(expData, calibrationMap=calibrationMap, categoryMap=categoryMap)
	expResult.meta = meta
	
	return expResult
