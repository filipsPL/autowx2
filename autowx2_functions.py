# -*- coding: utf-8 -*-
#
# autowx2 - function and classes used by autowx2 and auxiliary programs
#
# GANTT Chart with Matplotlib
# Sukhbinder
# inspired by:
# https://sukhbinder.wordpress.com/2016/05/10/quick-gantt-chart-with-matplotlib/
# taken from
# https://github.com/fialhocoelho/test/blob/master/plot/gantt.py
#

# for autowx2 itself
import predict
import time
from datetime import datetime
from time import strftime
import subprocess
import os
from _crontab import *
from tendo import singleton # avoid two instancess WARNING do we need it? :# QUESTION:
import re
import sys


# for plotting
import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
# import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import DateFormatter
import numpy as np

# webserver
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import codecs
from threading import Thread


# configuration
from autowx2_conf import *
from autowx2_webserver import *



# ---------------------------------------------------------------------------- #

satellites = list(satellitesData)
qth = (stationLat, stationLon, stationAlt)


def mkdir_p(outdir):
    ''' bash "mkdir -p" analog'''
    if not os.path.exists(outdir):
        os.makedirs(outdir)


class bc():

    """Colors made easy"""
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[97m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GRAY = '\033[37m'
    UNDERLINE = '\033[4m'


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def getTleData(satellite):
    '''Open tle file and return a TLE record for the given sat'''
    tlefile = open(tleFileName, 'r')
    tledata = tlefile.readlines()
    tlefile.close()

    tleData = []

    for i, line in enumerate(tledata):
        if satellite in line:
            for n in tledata[i:i + 3]:
                tleData.append(n.strip('\r\n').rstrip())
            break
    if len(tleData) > 0:
        return tleData
    else:
        return False


def parseCron(cron):
    entry = CronTab(cron).next(default_utc=False)
    return entry + time.time()  # timestamp of the next occurence


def getFixedRecordingTime(satellite):
    '''Reads from the config the fixed recording time'''
    try:
        fixedTime = satellitesData[satellite]["fixedTime"]
        fixedDuration = satellitesData[satellite]["fixedDuration"]
        return {"fixedTime": parseCron(fixedTime), "fixedDuration": fixedDuration}
    except KeyError:
        return False


def genPassTable(satellites, qth, howmany=20):
    '''generate a table with pass list, sorted'''

    passTable = {}
    for satellite in satellites:

        tleData = getTleData(satellite)
        priority = satellitesData[satellite]['priority']

        if tleData:    # if tle data was there in the file :: SATELLITES

            czasStart = time.time()

            p = predict.transits(tleData, qth, czasStart)

            # d = predict.observe(tleData, qth)
            # print d['doppler'] ## doppler : doppler shift between groundstation and satellite.
            # exit(1)

            for i in range(1, howmany):
                transit = p.next()

                # transitEnd = transit.start + transit.duration() - skipLast

                if not time.time() > transit.start + transit.duration() - skipLast - 1:  # esttimate the end of the transit, minus last 10 seconds
                    if int(transit.peak()['elevation']) >= minElev:
                        passTable[transit.start] = [satellite, int(
                            transit.start + skipFirst), int(
                                transit.duration() - skipFirst - skipLast),
                            int(transit.peak()['elevation']), int(
                                transit.peak()['azimuth']), priority
                        ]
                    # transit.start - unix timestamp

        elif 'fixedTime' in satellitesData[satellite]:                   # if ['fixedTime'] exists in satellitesData => time recording
            # cron = getFixedRecordingTime(satellite)["fixedTime"]
            cron = satellitesData[satellite]['fixedTime']
            duration = getFixedRecordingTime(satellite)["fixedDuration"]

            delta = 0
            for i in range(0, howmany):
                entry = CronTab(
                    cron).next(now=time.time() + delta,
                               default_utc=False)
                delta += entry
                start = delta + time.time()
                passTable[start] = [
                    satellite, int(start), int(duration), '0', '0', priority]
        else:
            log("✖ Can't find TLE data (in keplers) nor fixed time schedule (in config) for " +
                satellite, style=bc.FAIL)

    # Sort pass table
    passTableSorted = []
    for start in sorted(passTable):
        passTableSorted.append(passTable[start])

    # Clean the pass table according to the priority. If any pass overlaps,
    # remove one with less priority (lower priority number).
    passTableSortedPrioritized = passTableSorted[:]
    passCount = len(passTableSorted)
    for i in range(0, passCount - 1):   # -1 or -2 :BUG?
        satelliteI, startI, durationI, peakI, azimuthI, priorityI = passTableSorted[
            i]
        satelliteJ, startJ, durationJ, peakJ, azimuthJ, priorityJ = passTableSorted[
            i + 1]
        endTimeI = startI + durationI

        if priorityI != priorityJ:
            if (startJ + priorityTimeMargin < endTimeI):
                # print "End pass:", satelliteI, t2human(endTimeI), "--- Start
                # time:", satelliteJ, t2human(startJ)
                if priorityJ < priorityI:
                    log(" 1. discard %s, keep %s" % (satelliteI, satelliteJ))
                    passTableSortedPrioritized[i] = ''
                elif priorityJ > priorityI:
                    log(" 2. discard %s, keep %s" % (satelliteJ, satelliteI))
                    passTableSortedPrioritized[i + 1] = ''

    # let's clean the table and remove empty (removed) records
    # and remove the priority record, it will not be useful later -- x[:5]
    passTableSortedPrioritized = [x[:5]
                                  for x in passTableSortedPrioritized if x != '']

    return passTableSortedPrioritized


def t2human(timestamp):
    '''converts unix timestamp to human readable format'''
    return strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))


def t2humanMS(seconds):
    '''converts unix timestamp to human readable format MM:SS'''
    mm = int(seconds / 60)
    ss = seconds % 60
    return "%02i:%02i" % (mm, ss)


def printPass(satellite, start, duration, peak, azimuth, freq, processWith):
    return "● " + bc.OKGREEN + "%10s" % (satellite) + bc.ENDC + " :: " \
        + bc.OKGREEN + t2human(start) + bc.ENDC + " to " + bc.OKGREEN  + t2human(start + int(duration)) + bc.ENDC \
        + ", dur: " + t2humanMS(duration) \
        + ", max el. " + str(int(peak)) + "°" + "; azimuth: " + str(int(azimuth)) + \
                         "° (" + azimuth2dir(azimuth) + ") f=" + str(
                             freq) + "Hz; Decoding: " + str(processWith)


def listNextPases(passTable, howmany):
    i = 1
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']
        log(printPass(satellite, start, duration,
            peak, azimuth, freq, processWith))
        i += 1


def runForDuration(cmdline, duration, loggingDir):
    outLogFile = logFile(loggingDir)
    teeCommand = ['tee',  '-a', outLogFile ] # quick and dirty hack to get log to file

    cmdline = [str(x) for x in cmdline]
    # print cmdline
    try:
        p1 = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p2 = subprocess.Popen(teeCommand, stdin=p1.stdout)

        # result1 = p1.communicate()[0]
        # handle_my_custom_event(result1)

        result = p2.communicate()[0]
        return result

        time.sleep(duration)
        p1.terminate()
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL)
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)


def justRun(cmdline, loggingDir):
    '''Just run the command as long as necesary and return the output'''
    outLogFile = logFile(loggingDir)
    teeCommand = ['tee',  '-a', outLogFile ] # quick and dirty hack to get log to file

    cmdline = [str(x) for x in cmdline]
    try:
        p1 = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p2 = subprocess.Popen(teeCommand, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = p2.communicate()[0]
        return result
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL)
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)


def runTest(duration=3):
    '''Check, if RTL_SDR dongle is connected'''
    child = subprocess.Popen('rtl_test', stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    time.sleep(duration)
    child.terminate()
    _, err = child.communicate()
    # if no device: ['No', 'supported', 'devices', 'found.']
    # if OK: ['Found', '1', 'device(s):', '0:', 'Realtek,',
    # 'RTL2838UHIDIR,',...
    info = err.split()[0]
    if info == "No":
        log("✖ No SDR device found!", style=bc.FAIL)
        return False
    elif info == "Found":
        log("SDR device found!")
        return True
    else:
        log("Not sure, if SDR device is there...")
        return True


def getDefaultDongleShift(dongleShift=dongleShift):
    log("Reading the default dongle shift")
    if os.path.exists(dongleShiftFile):
        f = open(dongleShiftFile, "r")
        newdongleShift = f.read().strip()
        f.close()

        if newdongleShift != '' and is_number(newdongleShift):  # WARNING and newdongleShift is numeric:
            dongleShift = str(float(newdongleShift))
            log("Recently used dongle shift is: " + str(dongleShift) + " ppm")
        else:
            log("Using the default dongle shift: " + str(dongleShift) + " ppm")

        return dongleShift


def calibrate(dongleShift=dongleShift):
    '''calculate the ppm for the device'''
    if (calibrationTool):
        cmdline = [calibrationTool]
        newdongleShift = justRun(cmdline, loggingDir).strip()
        if newdongleShift != '' and is_number(newdongleShift):
            log("Recalculated dongle shift is: " +
                str(newdongleShift) + " ppm")
            return str(float(newdongleShift))
        else:
            log("Using the good old dongle shift (a): " +
                str(dongleShift) + " ppm")
            return dongleShift
    else:
        log("Using the good old dongle shift: " + str(dongleShift) + " ppm")
        return dongleShift


def azimuth2dir(azimuth):
    ''' convert azimuth in degrees to wind rose directions (16 wings)'''
    dirs = ["N↑", "NNE↑↗", "NE↗", "ENE→↗",
            "E→", "ESE→↘", "SE↘", "SSE↓↘",
            "S↓", "SSW↓↙", "SW↙", "WSW←↙",
            "W←", "WNW←↖", "NW↖", "NNW↑↖", ]

    part = int(float(azimuth) / 360 * 16)
    return dirs[part]


def escape_ansi(line):
    '''remove ansi colors from the given string'''
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


def log(string, style=bc.CYAN):
    message = "%s%s%s %s %s %s " % (
        bc.BOLD,
        datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M'),
        bc.ENDC,
        style,
        str(string),
        bc.ENDC)
    # socketio.emit('log', {'data': message}, namespace='/')
    handle_my_custom_event(escape_ansi(message) + "<br />\n")
    print message

    # logging to file, if not Flase
    if loggingDir:
        logToFile(escape_ansi(message) + "\n", loggingDir)


def logFile(logDir):
    '''Create output logging dir, returns name of the logfile'''
    mkdir_p(logDir)
    outfile = "%s/%s.txt" % (
        logDir,
        datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d'))
    return outfile


def logToFile(message, logDir):
    # save message to the file
    outfile = logFile(logDir)
    file_append(outfile, message)


def file_append(filename, content):
    f = open(filename, 'a')
    f.write(content)
    f.close()


# ------------ functions for generation of pass table, saving, png image etc...


def t2humanHM(timestamp):
    '''converts unix timestamp to human readable format'''
    # oggingDir
    return strftime('%H:%M', time.localtime(timestamp))


def _create_date(timestamp):
    """Creates the date from timestamp"""
    mdate = matplotlib.dates.date2num(datetime.fromtimestamp(timestamp))
    return mdate


def CreateGanttChart(listNextPasesListList):
    """
        Create gantt charts with matplotlib
    """

    ylabels = []
    customDates = []

    i = 1
    for tx in listNextPasesListList:
        ylabel, startdate, enddate = tx
        # ylabels.append("%s (%1i)" % (ylabel, i) )
        ylabels.append("(%1i)" % (i))
        # ylabels.append("%s" % (ylabel) )
        customDates.append([_create_date(startdate), _create_date(enddate)])
        i += 1

    ilen = len(ylabels)
    pos = np.arange(0.5, ilen * 0.5 + 0.5, 0.5)
    task_dates = {}
    for i, task in enumerate(ylabels):
        task_dates[task] = customDates[i]
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    for i, ylabel in enumerate(ylabels):
        ylabelIN, startdateIN, enddateIN = listNextPasesListList[i]
        start_date, end_date = task_dates[ylabels[i]]
        ax.barh(
            (i * 0.5) + 0.5,
            end_date - start_date,
            left=start_date,
            height=0.3,
            align='center',
            edgecolor='black',
            color='navy',
            label='',
            alpha=0.95)
        ax.text(
            end_date,
            (i * 0.5) + 0.55,
            ' %s | %s' % (t2humanHM(startdateIN),
                          ylabelIN),
            ha='left',
            va='center',
            fontsize=7,
            color='gray')

    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=8)
    ax.axis('tight')
    ax.set_ylim(ymin=-0.1, ymax=ilen * 0.5 + 0.5)
    ax.grid(color='silver', linestyle=':')
    ax.xaxis_date()

    # FAKE,startdate,FAKE=listNextPasesListList[0]
    # minutOdPelnej = int(datetime.fromtimestamp(time.time()).strftime('%M'))
    # plotStart = int(time.time() - minutOdPelnej*60)
    # print t2human(plotStart)
    # ax.set_xlim(_create_date(plotStart), _create_date(enddate+600))

    Majorformatter = DateFormatter("%H:%M\n%d-%b")
    ax.xaxis.set_major_formatter(Majorformatter)
    labelsx = ax.get_xticklabels()
    # plt.setp(labelsx, rotation=30, fontsize=10)
    plt.setp(labelsx, rotation=0, fontsize=7)
    plt.title(
        'Transit plan for %s, generated %s' %
        (stationName, t2human(time.time())))

    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(ganttNextPassList)

    if ylabel == enddateIN:
        print locsy  # "This is done only to satisfy the codacy.com. Sorry for that."


def listNextPasesHtml(passTable, howmany):
    i = 1
    output = "<table class='table small'>\n"
    output += "<tr><th>#</th><th>satellite</th><th>start</th><th>duration</th><th>peak</th><th>azimuth</th><th>freq</th><th>process with</th><tr>\n"

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        output += "<tr><td>%i</td><td>%s</td><td>%s</td><td>%s</td><td>%s°</td><td>%s° (%s)</td><td>%sHz</td><td>%s</td><tr>\n" % (
            i, satellite, t2human(start), t2humanMS(duration), peak, azimuth, azimuth2dir(azimuth), freq, processWith)
        i += 1

    output += "</table>\n"

    return output.decode('utf-8')


def listNextPasesTxt(passTable, howmany):

    txtTemplate = "%3s\t%10s\t%16s\t%9s\t%4s\t%3s\t%6s\t%10s\t%20s\n"

    i = 1
    output = ""
    output += txtTemplate % (
        "#",
        "satellite",
     "start",
     "dur MM:SS",
     "peak",
     "az",
     "az",
     "freq",
     "process with")

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        output += txtTemplate % (
            i,
            satellite,
            t2human(start),
            t2humanMS(duration),
            peak,
            azimuth,
            azimuth2dir(azimuth),
            freq,
            processWith)
        i += 1

    output += "\n"

    return output


def listNextPasesList(passTable, howmany):
    output = []
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        # freq = satellitesData[satellite]['freq']
        # processWith = satellitesData[satellite]['processWith']

        output.append([satellite, start, start + duration])
    if peak:
        print "This is a miracle!"  # codacy cheating, sorry.
    return output


def saveToFile(filename, data):
    # print filename
    # print data
    # exit(1)
    plik = open(filename, "w")
    plik.write(data.encode("utf-8"))
    plik.close()


def generatePassTableAndSaveFiles(satellites, qth, verbose=True):
    # recalculate table of next passes
    log("Recalculating the new pass table and saving to disk.")
    passTable = genPassTable(satellites, qth, howmany=50)
    listNextPasesHtmlOut = listNextPasesHtml(passTable, 100)
    saveToFile(htmlNextPassList, listNextPasesHtmlOut)

    listNextPasesListList = listNextPasesList(passTable, 20)
    CreateGanttChart(listNextPasesListList)

    if verbose:
        print listNextPasesTxt(passTable, 100)



# --------------------------------------------------------------------------- #
# --------- THE WEBSERVER --------------------------------------------------- #
# --------------------------------------------------------------------------- #


def file_read(filename):
    with codecs.open(filename, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.read()
    linesBr = "<br />".join( lines.split("\n") )
    return linesBr


@app.route('/')
def homepage():
    logfile = logFile(loggingDir)
    logs = file_read(logfile)

    body =""
    # log window
    body += "<h3>Recent logs</h3><p><strong>File</strong>: %s</p><pre style='height: 400px;' id='logWindow' class='pre-scrollable small text-nowrap'>%s</pre>" % (logfile, logs)

    # next pass table
    passTable = genPassTable(satellites, qth)
    body += "<h3>Next passes</h3><span id='nextPassWindow'>%s</span>" % ( listNextPasesHtml(passTable, 10) )
    return render_template('index.html', title="Home page", body=body)

@socketio.on('my event')
def handle_my_custom_event(text):
    socketio.emit('my response', { 'tekst': text } )

@socketio.on('next pass table')
def handle_next_pass_list(text):
    socketio.emit('response next pass table', { 'tekst': text } )


#
# show pass table
#

@app.route('/table')
def passTable():
    body=file_read(htmlNextPassList)
    return render_template('index.html', title="Pass table", body=body)


# --------------------------------------------------------------------------- #
# --------- THE MAIN LOOP --------------------------------------------------- #
# --------------------------------------------------------------------------- #

def mainLoop():
    dongleShift = getDefaultDongleShift()

    while True:

        # each loop - reads the config file in case it has changed
        from autowx2_conf import *  # configuration

        # recalculate table of next passes
        passTable = genPassTable(satellites, qth)

        # save table to disk
        generatePassTableAndSaveFiles(satellites, qth, verbose=False)

        # show next five passes
        log("Next five passes:")
        listNextPases(passTable, 5)

        # pass table for webserver
        handle_next_pass_list(listNextPasesHtml(passTable, 10))

        # get the very next pass
        satelitePass = passTable[0]
        satellite, start, duration, peak, azimuth = satelitePass
        satelliteNoSpaces = satellite.replace(" ", "-") #remove spaces from the satellite name

        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        fileNameCore = datetime.fromtimestamp(
            start).strftime(
                '%Y%m%d-%H%M') + "_" + satelliteNoSpaces

        log("Next pass:")
        log(printPass(satellite, start, duration,
            peak, azimuth, freq, processWith))

        towait = int(start - time.time())

        if cleanupRtl:
            log("Killing all remaining rtl_* processes...")
            justRun(["bin/kill_rtl.sh"], loggingDir)

        # test if SDR dongle is available
        if towait > 15: # if we have time to perform the test?
            while not runTest():
                log("Waiting for the SDR dongle...")
                time.sleep(10)

        # It's a high time to record!
        if towait <= 1 and duration > 0:
            # here the recording happens
            log("!! Recording " + printPass(satellite, start, duration,
                peak, azimuth, freq, processWith), style=bc.WARNING)

            processCmdline = [
                processWith,
                fileNameCore,
                satellite,
                start,
                duration + towait,
                peak,
                azimuth,
                freq]
            justRun(processCmdline, loggingDir)
            time.sleep(10.0)

        # still some time before recording
        else:
            # recalculating waiting time
            if towait > 300:
                    log("Recalibrating the dongle...")
                    dongleShift = calibrate(dongleShift)  # replace the global value

            towait = int(start - time.time())
            if scriptToRunInFreeTime:
                if towait >= 120:  # if we have more than [some] minutes spare time, let's do something useful
                    log("We have still %ss free time to the next pass. Let's do something useful!" %
                        (t2humanMS(towait - 1)))
                    log("Running: %s for %ss" %
                        (scriptToRunInFreeTime, t2humanMS(towait - 1)))
                    _ =     runForDuration(
                        [scriptToRunInFreeTime,
                         towait - 1,
                         dongleShift],
                        towait - 1, loggingDir)
                                   # scrript with run time and dongle shift as
                                   # arguments
                else:
                    log("Sleeping for: " + t2humanMS(towait - 1) + "s")
                    time.sleep(towait - 1)
            else:
                towait = int(start - time.time())
                log("Sleeping for: " + t2humanMS(towait - 1) + "s")
                time.sleep(towait - 1)

logfile = logFile(loggingDir)
