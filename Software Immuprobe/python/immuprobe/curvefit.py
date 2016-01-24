#!/bin/env python2

'''
Calculate concentrations of the samples given the raw measurements
and some calibration data.
'''

import numpy as np
from scipy.optimize import curve_fit
from scipy.misc import derivative	# derivative using finite differences


_defaultCurve = lambda x, a, b: a*x + b


'''
Set parameters according to calibration data.

Returns: Fitted function of x as a lambda fuction.
Throws: OptimizeWarning, ValueError
'''
def fittedCurve(xdata, ydata, curve=_defaultCurve):
	popt, pcov = curve_fit(curve, xdata, ydata) # TODO: handle exceptions: OptimizeWarning, ValueError
	
	return lambda x : curve(x, *popt)
		
	
'''
Evaluate a measurement (or a list of them).

If standard deviations are given (stdDevs=...) then the standard deviations
of the new values get calculated: returns (list of values, list of standard deviations)

@param calibX	X values of calibration points.
@param calibY	Y values of calibration points.
@param xdata	The data to apply the fitted curve to.
@param stdDevs	Standard deviations of xdata.

Returns: The evaluated list.
'''
def evaluate_stddev(calibX, calibY, xdata, stdDevs):
	
	curve = fittedCurve(calibX, calibY, curve=_defaultCurve)
	
	assert(len(xdata) == len(stdDevs))
	
	mean_std = [evaluate_stddev_(curve, x, std) for x, std in zip(xdata, stdDevs)]
	
	values = [m[0] for m in mean_std]
	stdDevs = [m[1] for m in mean_std]
	
	
	return (values, stdDevs)

'''
Given x and the std. dev. of x calculates f(x) and std. dev. of f(x)

Returns: f(value), std. dev. of f(value)
'''
def evaluate_stddev_(f, value, stddev):

	y = f(value)
	df = derivative(f, value)
	
	_stddev = stddev * df
	
	return (y, _stddev)

# run as standalone script
if __name__ == '__main__':
	print('testing '+__file__)
	x = [0,1,2,3]
	y = [10,12,14,14]
	test = [0,1,2,3]
	print(evaluate(x,y,test,[0.1]*4))
	
