from flask import Flask, render_template, send_from_directory, jsonify, request, Response, json
from flask.ext.restful import Api, Resource
from immuprobe.immuprobe import *
import tempfile
import csv
import io
from immuprobe import plot
import subprocess
from time import gmtime, strftime


app = Flask(__name__, static_url_path = "")
api = Api(app)

experiment = Immuprobe()
data = None

#first html to be rendered, home
@app.route('/')
def index():
  return render_template('gui.html')

#general routing for static files. Used to get html, csv, images and js from folder static
@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)
	
	
class ImmuprobeAPI(Resource):
    def get(self, dat):
		tempdata = json.loads(request.dat)
	
		name = tempdata['name']
	
		global data
	
		# This maps names to functions.
		functionMap = {
			'camera.iso': lambda: experiment.iso,	# lambda is required because .iso is a @property
			'camera.shutter_speed': lambda: experiment.shutter_speed,
			'experiment.categoryMap': lambda: list(experiment.categoryMap.values()),
			'experiment.calibration': lambda: experiment.caldata,
			'data.results': lambda: data.concentration_values,
			'measure.please': lambda: measure()
		}
	
		if dat in functionMap:
			resp = json.dumps(functionMap[name]())
		else:
			resp = "invalid function %s"%name
	
		print(resp)
		return resp
        


api.add_resource(ImmuprobeAPI, '/ImmuproneAPI', endpoint = 'immuprobeEnd')


if __name__ == '__main__':
	#app.run(host="0.0.0.0", debug=True)
	app.run(debug=True)



