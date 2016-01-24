#!/bin/env python2

import sys
sys.path.append('../python/')	# add path to immuprobe module

from flask import Flask, render_template, send_from_directory, jsonify, request, Response, json
from immuprobe.immuprobe import *
import tempfile
import csv
import io
from immuprobe import plot
import subprocess
from time import gmtime, strftime
from dateutil.parser import parse

import os

# global variables
_livestream_on = False
experiment = Immuprobe()
data = None

# initialize Flask application 
app = Flask(__name__, static_url_path = "")

# ---- rendering the main html file and setting a static path route for static files on the server ----

#first html to be rendered, home
@app.route('/')
def index():
  return render_template('gui.html')

#general routing for static files. Used to get html, csv, images and js from folder static
@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)



# ---- API code section -----

# Getter function for JS API. 
@app.route('/ipGet', methods=['POST'])
def ipGet():
	tempdata = json.loads(request.data)
	
	name = tempdata['name']
	
	global data
	
	# This maps names to functions.
	functionMap = {
		'camera.iso': lambda: experiment.iso,	# lambda is required because .iso is a @property
		'camera.shutter_speed': lambda: experiment.shutter_speed,
		'experiment.categoryMap': lambda: list(experiment.categoryMap.values()),
		'experiment.calibration': lambda: experiment.caldata,
		'experiment.iscalibrated': lambda: data is not None and data.isCalibrated,
		'data.isnone': lambda: data == None,
		'data.results': lambda: data.concentration_values,
		'measure.please': lambda: measurement(),
		'reset': lambda: reset()
	}
	
	if name in functionMap:
		resp = json.dumps(functionMap[name]())
	else:
		resp = "invalid function %s"%name
	
	print(resp)
	return resp
		
# Setter function for JS API.
@app.route('/ipSet', methods=['POST'])
def ipSet():
	data = json.loads(request.data)
	
	name = data['name']
	value = data['value']
	
	if name == 'camera.iso':
		experiment.iso = int(value)
		resp = 'OK'
		
	elif name == 'camera.shutter_speed':
		experiment.shutter_speed = int(value)
		resp = 'OK'
		
	elif name == 'camera.livestream':
		# toggle the livestream
		global _livestream_on
		_livestream_on = not _livestream_on
		
		light_color = 'white'
		
		# kill the livestream
		setLight(light_color, 0)
		os.system('bash livestream.sh stop')
		
		if _livestream_on:
			setLight(light_color, 1)
			os.system('bash livestream.sh start')
		
		resp = 'OK'
		
	elif name == 'calibrate':
		resp = calibrate(value)
		
		
	elif name == 'categories':
		resp = categories(value)
		
	elif name == 'time':
		if len(value) > 0:
			#TODO actuall test this one on the rpi
			print("Set time:", value)
			date = parse(value)
			datestr = date.strftime('%Y-%m-%d %H:%M:%S')
			os.system("sudo date --set='%s'"%datestr)	
		resp="OK"

	else:
		resp = "invalid function %s"%name
	
	return json.dumps(resp)


# ---- helping functions for formating and triggering of measurement ----

# prepares value to call actual calibration function of immuprobe object	
def calibrate(value):
	try:
		if (not data==None):
			dct=dict()
			i = 0	
			for i in range(25):
				c = value[i]["value"]
				if len(c)>0:
					dct[i] = float(c)
			print("set calibration in data: ", dct)
			data.calibrationMap=dct
	
		dct=dict()
		i = 0	
		for i in range(25):
			c = value[i]["value"]
			if len(c)>0:
				dct[i] = float(c)
		print("set calibration: ", dct)
		experiment.calibrate(dct)
	except Exception, e:
		return e.args[0]		
	
	return "OK"

# prepares value to call actual category setter function of immuprobe object	
def categories(value):
	try:
		if(not data==None):
			dct=dict()
			i = 0
			for d in value:
				if d["name"][0:3] == 'cat':
					dct[i] = d["value"]
					i = i+1
			print("set categories in data: ", dct)		
			data.categoryMap = dct
	
		dct=dict()
		i = 0
		for d in value:
			if d["name"][0:3] == 'cat':
				dct[i] = d["value"]
				i = i+1
		print("set categories: ", dct)	
		experiment.categoryMap = dct
	except Exception, e:
		return e.args[0]
	
	return "OK"
	
# triggers measurement and stores result in a global variable called data
def measurement():	
	try:
		global data
		data=experiment.measure()
	except Exception, e:
		return e.args[0]
	return "success"
	
	
def reset():
	global _livestream_on
	global experiment
	global data
	_livestream_on = False
	experiment = Immuprobe()
	data = None
	return "OK"
	



# ---- Other routes for tasks that don't use the API ----

# get a preview image
@app.route('/camera/preview')
def preview():
	
	print('generate preview')
	
	resolution =	request.args.get('resolution')
	width, height = map(int, resolution.split('x'))
	
	shutter_speed = int(request.args.get('shutter_speed'))
	light_color = request.args.get('light_color')
	
	auto_exposure = request.args.get('auto_exposure') in ['1', 'true', 'True']
	
	img = plot.img_compress(experiment.image_preview(shutter_speed=shutter_speed, resolution=(width, height), light_color=light_color, auto_exposure=auto_exposure), encoding='png')
	resp = Response(response=img,
						status=200,
						mimetype="image/png")
	return resp

	'''resp = Response(response='Failed to get a preview image!',
						status=500,
						mimetype="image/png")
	return resp'''
		
# execute module measure with uploaded image
@app.route('/upload', methods=['POST'])
def experiment_upload():
	try:
		file = request.files['file']
		serialized = file.stream.read()
		
		global data
		data = deserialize_result(serialized)
		
		# load settings
		experiment.calibrate(data.calibrationMap)
		experiment.categoryMap = data.categoryMap
		
	except Exception, e:
		return json.dumps(e.args[0])
	
	return json.dumps("success")

	
# provide plots as svg
@app.route('/results/plot')
def plotplotplot():
	
	plotType = request.args.get('type')
	download = request.args.get('download') is not None
	svgPlot = None
	
	mimetype = "application/svg+xml" if download else "image/svg+xml"
	
	try :
		svgPlot = plot.plot_svg(data, plotType);
		resp = Response(response=svgPlot,
							status=200,
							mimetype=mimetype)
		if download:
			filename= "immuprobe_plot_%s_%s.svg"%(plotType, data.timestamp.strftime('%Y%m%d_%H%M'))
			resp.headers["Content-Disposition"] = 'inline; filename="%s"'%filename
	except Exception, e:
		print(str(e))
		resp = Response(response="Plot type not found: %s"%str(e),
							status=404)
	
	return resp


# returns a csv file to gui
@app.route('/results/csv')
def write():
	if data is not None:
		csv = data.asCSV
		resp = Response(response=csv,
							status=200,
							mimetype="text/csv")
		filename= "immuprobe_result_%s.csv"%strftime('%Y%m%d_%H%M')
		resp.headers["Content-Disposition"] = 'inline; filename="%s"'%filename
	else:
		resp = Response(response="CSV not available!",
						status=404)
	return resp
	
	
# returns a serialized form of the immuprobe data to gui	
@app.route('/results/serialize')
def serializedresult():
	global data
	resp = Response(response=data.serialize, status=200, mimetype="application/ipr")
	filename= "experiment_result_%s.ipr"%strftime('%Y%m%d_%H%M')
	resp.headers["Content-Disposition"] = 'inline; filename="%s"'%filename
	return resp


	
if __name__ == '__main__':
	#app.run(host="0.0.0.0", debug=True)
	app.run(debug=True)
