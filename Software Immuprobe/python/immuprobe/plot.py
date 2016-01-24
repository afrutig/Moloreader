#!/bin/env python2

'''
Plotting experiment results in different ways.
'''

from multiprocessing import Process, Queue
from matplotlib.figure import Figure 
from matplotlib.backends.backend_svg import FigureCanvasSVG # SVG plotting

import numpy as np
import math
from skimage import draw
from skimage.color import rgb2gray

import argparse
import os.path
import os

from skimage.io import imsave, imread, imshow, show
from skimage.transform import rescale

from matplotlib import pyplot as plt
import tempfile

from curvefit import fittedCurve

# constants, colors, ...
plot_bgcolor = 'white'
_concentration_units = 'mg/ml'

# Saturation threshold normalized to 1.
_saturation_threshold = 0.75

_plot_size = (6,4) # inches :-/ at 100 dpi -> 600x400 px

_plot_cache_hash = 0	# Hash of 'data' that has been used to generate the cached plots.
_plot_cache = dict()	# Contains cached plots.

'''
Draw a plot of 'data' as SVG image.
Plots get cached for a little speedup on poor RaspberryPi.

@param data	The experimental results: ExpResult object.
@param plotType overview, categorized, standard_curve, ... (see _plot_svg())
'''
def plot_svg(data, plotType, encoding='svg'):
	global _plot_cache_hash
	global _plot_cache
	
	data_hash = hash(data)
	print('makePlot')
	print('hash: %s'%data_hash)
	
	if data_hash != _plot_cache_hash:
		print('clear cache')
		_plot_cache_hash = data_hash
		_plot_cache.clear()
	
	print(_plot_cache.keys())
	
	if plotType not in _plot_cache.keys():
		print('plot not in cache: %s'%plotType)
		# draw plot and add it to cache
		#p = _plot_svg(data, plotType, encoding)
		p = _mp_plot(data, plotType, encoding)
		_plot_cache[plotType] = p
		
	return _plot_cache[plotType]


'''
Draw plot as SVG.
'''
def _plot_svg(data, plotType, encoding='svg'):
	
	plotMap = {
		'overview':			plot_overview,
		'categorized':		plot_categorized,
		'standard_curve':	plot_standard_curve,
		'signal_to_noise':	plot_signal_to_noise,
		'intensity':	plot_intensity,
		'signal_image': plot_signal_image,
		'contrast_image': plot_contrast_image
	}
	
	if plotType not in plotMap.keys():
		raise Exception('Invalid plot type: %s'%plotType)
		
	fig = plotMap[plotType](data)
	
	if encoding is None:
		return fig
	
	img = figure_to_svg(fig)
	
	return img

# multiprocess plot
def _mp_plot(data, plotType, encoding):
	def task(queue, data, plotType, encoding):
		img = _plot_svg(data, plotType, encoding)
		queue.put(img)
	
	q = Queue()
	p = Process(target=task, args=(q, data, plotType, encoding))
	p.start()
	img = q.get()
	p.join()
	return img

'''
Convert 2D np array into binary jpg, png, ...
'''
def img_compress(img, encoding='png'):
	temp = tempfile.NamedTemporaryFile(suffix='.%s'%encoding, delete=True)
	#saving the np array as png in tmp
	imsave(temp.name, img)
	binary = temp.read()
	temp.close()
	
	return binary

'''
Convert jpg, png, ... to 2D numpy array
'''
def img_decompress(img):
	encoding='tmp'
	temp = tempfile.NamedTemporaryFile(suffix='.%s'%encoding, delete=False)
	#saving the np array as png in tmp
	temp.write(img)
	temp.close()
	npImage = imread(temp.name)
	
	os.remove(temp.name)
	
	return npImage
	
'''
Convert numpy image to png.
'''
def png(npImage):
	return img_compress(npImage, 'png')

'''
Convert a pyplot figure (fig) into a 2D numpy image.
'''
def figure_to_img(fig):
	fig.canvas.draw()
	data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
	data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
	return data

'''
Convert a matplotlib figure to binary SVG data.
'''
def figure_to_svg(fig):
	tempFile = tempfile.NamedTemporaryFile(suffix='.svg.tmp', delete=False)
	canvas = FigureCanvasSVG(fig)
	canvas.print_svg(tempFile.name)
	svgImg = tempFile.read()
	os.remove(tempFile.name)
	return svgImg

'''
Convert a pyplot figure (fig) to binary image.

Returns: Binary data of image. Default: png.
'''
def figure_to_compressed(fig, encoding='png', _dpi=100):
	temp = tempfile.NamedTemporaryFile(suffix='.%s'%encoding, delete=True)
	fig.savefig(temp.name, dpi=_dpi)
	data = temp.read()
	temp.close()
	return data

def plot_signal_image(result):
	return result.raw.signalImage

def plot_contrast_image(result):
	return result.raw.signalImage
	
'''
Plot the results.

Return: Binary of specified encoding. Default: png.
		Returns numpy array if encoding=None.
'''
def plot_overview(result, encoding='jpg', show=False):
	
	image = result.raw.signalImage
	maxValue = np.iinfo(image.dtype).max
	saturation_threshold = maxValue * _saturation_threshold
	
	locations = np.array(result.spot_locations)
	
	# crop image
	minX = np.min(locations[:,0])
	maxX = np.max(locations[:,0])
	minY = np.min(locations[:,1])
	maxY = np.max(locations[:,1])
	
	margin = max(maxX-minX, maxY-minY)*0.2
	minX -= margin
	minY -= margin
	maxX += margin
	maxY += margin
	
	minX = max(0, minX-margin)
	minY = max(0, minY-margin)
	maxX = min(image.shape[0], maxX+margin)
	maxY = min(image.shape[1], maxY+margin)
	
	if (maxX-minX) > 100 and (maxY-minY) > 100:
		image = image[minX:maxX,minY:maxY]
		
		# shift locations accordingly
		locations[:,0] = locations[:,0]-minX
		locations[:,1] = locations[:,1]-minY
	
	targetWidth = 300
	
	downscaleFactor = min(1, 1.*targetWidth/image.shape[0])	# scale down the image before plotting
	image = rescale(image, downscaleFactor)
	
	# rescale locations
	locations = locations*downscaleFactor
	
	values = result.intensity_values
	
	fig = Figure()
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122) 
	
	fig.set_size_inches(_plot_size[0],_plot_size[1], forward=True)
	fig.set_facecolor(plot_bgcolor)
	
	ax1.imshow(image, cmap='gray')
	ax1.set_title('Raw Image')
	ax1.axis('off')
	
	ax2.imshow(image, cmap='gray')
	ax2.set_title('Spots')
	ax2.axis('off')
	
	radius = np.mean(locations[:,2])
	index = 0
	for spot, value in zip(locations,values):
		x, y, r = spot
		
		if value < saturation_threshold:
			c = plt.Circle((y, x), radius+1, color=(0, 1, 0), linewidth=1, fill=False)
		else:
			# warning of saturated points
			c = plt.Circle((y, x), radius+4, color=(1, 0.5, 0), linewidth=3, fill=False)
			
		ax2.add_patch(c)
		# text label
		ax2.text(y, x-radius, '%d'%index,
                ha='center', va='bottom', color='w')
		#ax3.add_patch(c)
		index += 1

	#fig.tight_layout()
		
	return fig

def plot_intensity(result, encoding='jpg'):
	
	fig = Figure()
	ax3 = fig.add_subplot(111)

	values = result.intensity_values
	
	fig.set_size_inches(_plot_size[0],_plot_size[1], forward=True)
	fig.set_facecolor(plot_bgcolor)

		
	# plot values
	ax3.set_title('Intensities')
	ax3.grid(True)
	ax3.set_xlabel('spot')
	ax3.set_ylabel('intensity')
	ind = np.arange(len(values))
	bars_raw = ax3.bar(ind, values, width=0.25, color='black', yerr=result.intensity_stddev)
	
	#fig.tight_layout()
	
	return fig

'''
Plot the results.

Return: Binary of specified encoding. Default: png.
		Returns numpy array if encoding=None.
'''
def plot_categorized(result, encoding='jpg'):
	
	fig = Figure()
	ax1 = fig.add_subplot(111) 
	
	categoryMap = result.categoryMap
	categorized = result.categorized
	
	isCalibrated = result.isCalibrated
	
	labels = categorized.keys()
	labels = sorted(labels, key=lambda l: categorized[l])
	x = np.arange(len(labels))+1
	
	values = np.array(result.concentration_values)

	avgValues = [categorized[k] for k in labels]
	
	fig.set_size_inches(_plot_size[0],_plot_size[1], forward=True)
	fig.set_facecolor(plot_bgcolor)
	
	ax1.set_title('results')
	ax1.grid(True)

	
	# plot all values
	i = 0
	for cat in labels:
		indices = [idx for idx, c in categoryMap.items() if c==cat]
		y = values[indices]
		ax1.plot([x[i]]*len(y), y, marker='x', color='gray', linewidth=0)
		
		i = i+1
	
			
	# plot mean values
	ax1.plot(x, avgValues, marker='o', color='black', linewidth=0)
	
	#ax1.set_xticks(x, labels, rotation='horizontal')
	ax1.set_xticks(x, labels)
	ax1.legend(loc=4)

	fig.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.15)
	
	ax1.set_xlabel('category')
	if isCalibrated:
		ax1.set_ylabel('concentration [%s]'%_concentration_units)
	else:
		ax1.set_ylabel('intensity')
	
	#fig.tight_layout()

	return fig


# Plot fitted curve with signal/background y-axis.
def plot_standard_curve(result, encoding='jpg'):
	
	if not result.isCalibrated:
		raise Exception('Can not plot standard curve if experiment is not calibrated.')
	
	fig = Figure()
	ax1 = fig.add_subplot(111) 
	
	fig.set_size_inches(_plot_size[0],_plot_size[1], forward=True)
	fig.set_facecolor(plot_bgcolor)
	
	ax1.set_title('fitted curve')
	ax1.grid(True)

	background_mean, background_std = result.background_intensity

	# avoid division by zero with perfect testing images
	if background_mean == 0:
		print('warning: background is zero')
		background_mean = np.float64(1e-8)

	calibX, calibY = result.calibration_data
	calibY_snr = calibY / background_mean
	calibY_snr_err = result.intensity_stddev[result.calibration_data_indices] / background_mean
	curve = fittedCurve(calibX, calibY_snr)
	
	# plot fitted curve
	x = np.linspace(0,np.max(calibX),10)
	y = map(curve,x)
	ax1.plot(x, y, color='black', linewidth=1, label='fitted curve')
	
	# plot calibration points
	#ax1.plot(calibX, calibY_snr, marker='x', color='black', linewidth=0) #, yerr=calibY_snr_err)
	ax1.errorbar(calibX, calibY_snr, yerr=calibY_snr_err, marker='x', color='black', linewidth=0)
	
	ax1.set_xlabel('concentration [%s]'%_concentration_units)
	ax1.set_ylabel('signal / background')
	

	
	if background_std > 0:
		# don't plot lod, and loq if std_dev of background is not known.
		
		# limit of detection
		lod = result.limit_of_detection / background_mean
		ax1.axhline(y=lod, linewidth=1, color='g', label='LoD', linestyle='--')
		
		# limit of quantification
		loq = result.limit_of_quantification / background_mean
		ax1.axhline(y=loq, linewidth=1, color='b', label='LoQ', linestyle='-.')
	
	ax1.legend(loc=0)
           
	#plt.margins(0.2)
	#fig.subplots_adjust(hspace=0.2, wspace=0.2, bottom=0.15)
	
	#fig.tight_layout()

	return fig

# Plot fitted curve with signal/background y-axis.
def plot_signal_to_noise(result, encoding='jpg', show=False):
	
	fig = Figure()
	ax1 = fig.add_subplot(111) 
	
	fig.set_size_inches(_plot_size[0],_plot_size[1], forward=True)
	fig.set_facecolor(plot_bgcolor)
	
	ax1.set_title('Signal to Background')
	ax1.grid(True)

	background_mean, background_std = result.background_intensity

	# avoid division by zero with perfect testing images
	if background_mean == 0:
		print('warning: background is zero')
		background_mean = np.float64(1e-8)

	y = result.intensity_values
	x = np.arange(len(y))+1
	
	y_snr = y / background_mean
	y_snr_err = result.intensity_stddev / background_mean

	
	ax1.errorbar(x, y_snr, yerr=y_snr_err, marker='x', color='black', linewidth=0)
	
	ax1.set_xlabel('spot')
	ax1.set_ylabel('signal / background')
	

	
	if background_std > 0:
		# don't plot lod, and loq if std_dev of background is not known.
		
		# limit of detection
		lod = result.limit_of_detection / background_mean
		ax1.axhline(y=lod, linewidth=1, color='g', label='LoD', linestyle='--')
		
		# limit of quantification
		loq = result.limit_of_quantification / background_mean
		ax1.axhline(y=loq, linewidth=1, color='b', label='LoQ', linestyle='-.')
	
	ax1.legend(loc=4)
           
	#fig.tight_layout()
	
	
	return fig
