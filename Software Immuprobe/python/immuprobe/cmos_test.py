#!/bin/env python2

'''
Measure dependence of pixel values to exposure time. This is expected to be linear,
but for the RaspberryPi camera it's not.
'''

import capture
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import pickle
_light_color = 'blue'
_resolution = (2592,1944)
max_exposure = 20 # milliseconds
_exposure_times = np.linspace(0, max_exposure, 100) # time in ms
#_exposure_times = np.logspace(0, 200, 20) # time in ms


saturation_value = np.iinfo(np.uint16).max*0.8

_avg_values = list()
_min_values = list()
_max_values = list()

for expTime in _exposure_times:
	print('exposure time: %f ms'%expTime)
	img = capture.capture(shutter_speed=expTime*1000, light_color=_light_color, resolution=_resolution)
	min = np.min(img)
	avg = np.mean(img)
	max = np.max(img)

	_avg_values.append(avg)
	_min_values.append(min)
	_max_values.append(max)

_avg_values = np.array(_avg_values)
_min_values = np.array(_min_values)
_max_values = np.array(_max_values)


# save values
save = {'exposure_times': _exposure_times, 'mean': _avg_values, 'min': _min_values, 'max': _max_values}
file = open('cmos_test.dat', 'wb')
file.write(pickle.dumps(save))

# get saturation point
saturation_exptime = np.max(_exposure_times[_max_values<saturation_value]) or None

# get linear aproximation before saturation
lin_function = lambda x,a,b: a*x + b
popt, pcov = curve_fit(lin_function, _exposure_times[_max_values<saturation_value], _avg_values[_max_values<saturation_value])
lin_approx = lambda x : lin_function(x, *popt)
lin_approx = np.vectorize(lin_approx)

approx_x = _exposure_times[_max_values<saturation_value]
approx_y = lin_approx(approx_x)

print('first pixels saturated at %d ms'%saturation_exptime)

# plot that stuff

fig, (ax1) = plt.subplots(1, 1)
fig.set_facecolor('white')

ax1.set_title('CMOS sensitivity')
ax1.grid(True)

ax1.plot(_exposure_times, _avg_values, linewidth=1, label='average intensity')

ax1.plot(approx_x, approx_y, linewidth=1, label='linear approximation')
#ax1.plot(_exposure_times, _max_values, color='black', linewidth=1, label='max. intensity')

#ax1.errorbar(x, y, yerr=y_err, marker='x', color='black', linewidth=0)

# plot saturation point
if saturation_exptime is not None:
	plt.axvline(x=saturation_exptime, linewidth=1, color='red', label='saturation', linestyle='--')

plt.legend(loc=4)

plt.xlabel('exposure time [ms]')
plt.ylabel('pixel intensity')

plt.show()
