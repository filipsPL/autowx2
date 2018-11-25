# -*- coding: utf-8 -*-

#
# autowx2 - webserver definitions


# configuration
from autowx2_conf import *

from flask import Flask, render_template

# satellites = list(satellitesData)
# qth = (stationLat, stationLon, stationAlt)

app = Flask(__name__, template_folder="var/flask/templates/", static_folder='var/flask/static') # " template_folder="var/flask/templates/"

body="hello!"

@app.route('/')
def homepage():
    return render_template('index.html', body=body)
