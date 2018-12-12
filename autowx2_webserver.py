# -*- coding: utf-8 -*-

#
# autowx2 - webserver definitions

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import codecs

# satellites = list(satellitesData)
# qth = (stationLat, stationLon, stationAlt)


app = Flask(__name__, template_folder="var/flask/templates/", static_folder='var/flask/static')
socketio = SocketIO(app)

body="This is the body."


#
# homepage
#
