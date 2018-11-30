# -*- coding: utf-8 -*-

#
# autowx2 - webserver definitions

from flask import Flask, render_template
from flask_socketio import SocketIO, emit


# configuration
from autowx2_conf import *
from autowx2_functions import * # all functions and magic hidden here

import codecs

# satellites = list(satellitesData)
# qth = (stationLat, stationLon, stationAlt)

def file_read(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        lines = f.read()
    return lines


# -------------------------------------------------------------------------- #


app = Flask(__name__, template_folder="var/flask/templates/", static_folder='var/flask/static')
socketio = SocketIO(app)

body="body2"


#
# homepage
#

@app.route('/')
def homepage():
    print "aaaaaaaaaaaaaaaa!@"
    return render_template('index.html', title="Home page", body=body)

@socketio.on('my event')
def handle_my_custom_event(text):
    socketio.emit('my response', { 'tekst': text } )

#
# display last log
#

@app.route('/lastlog')
def lastlog():
    logfile = logFile(loggingDir)
    logs = file_read(logfile)
    body = "<p><strong>File</strong>: %s</p><pre class='small'>%s</pre>" % (logfile, logs)
    return render_template('index.html', title="Recent logs", body=body)

#
# show pass table
#

@app.route('/table')
def passTable():
    body=file_read(htmlNextPassList)
    return render_template('index.html', title="Pass table", body=body)
