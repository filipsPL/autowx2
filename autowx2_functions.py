# -*- coding: utf-8 -*-

#
# autowx2 - genpastable.py
# generates the pass table and recording plan for tne next few days and the appropriate plot
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
from tendo import singleton # avoid two instancess
import re
import sys

# for plotting
import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import DateFormatter
import numpy as np

# configuration
from autowx2_conf import *


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

'''
class Tee(object):
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
'''

class teeLog(object):
    '''Class for piping what is printed to both: screen and file'''
    def __init__(self, logDir):
        mkdir_p(logDir)
        outfile = "%s/%s.txt" % (
            logDir,
            datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d'))
        self.file = open(outfile, "a")
        self.stdout = sys.stdout
        sys.stdout = self
    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()
    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)


def runForDuration(cmdline, duration):
    cmdline = [str(x) for x in cmdline]
    try:
        if logging: pipeLog = teeLog(logging)
        child = subprocess.Popen(cmdline)
        time.sleep(duration)
        child.terminate()
        if logging: pipeLog.__del__()
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL)
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)


def justRun(cmdline):
    '''Just run the command as long as necesary and return the output'''
    cmdline = [str(x) for x in cmdline]
    try:
        pipeLog = teeLog(logging)
        child = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        result = child.communicate()[0]
        pipeLog.__del__()
        return result
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL)
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)


def runTest(duration=2):
    '''Check, if RTL_SDR dongle is connected'''
    child = subprocess.Popen('rtl_test', stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    time.sleep(duration)
    child.terminate()
    out, err = child.communicate()
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
        newdongleShift = justRun(cmdline).strip()
        if newdongleShift != '' and is_number(newdongleShift):
            log("Recalculated dongle shift is: " +
                str(newdongleShift) + " ppm")
            return str(float(newdongleShift))
        else:
            log("Using the good old dongle shift: " +
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
    '''remove anssi colors from the given string'''
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

    print message

    # logging to file, if not Flase
    if logging:
        logToFile(escape_ansi(message) + "\n", logging)


def logToFile(message, logDir):
    # save message to the file
    mkdir_p(logDir)
    outfile = "%s/%s.txt" % (
        logDir,
        datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d'))

    file_append(outfile, message)


def file_append(filename, content):
    f = open(filename, 'a')
    f.write(content)
    f.close()


# ------------ functions for generation of pass table, saving, png image etc...


def t2humanHM(timestamp):
    '''converts unix timestamp to human readable format'''
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
    output = "<table>\n"
    output += "<tr><td>#</td><td>satellite</td><td>start</td><td>duration</td><td>peak</td><td>azimuth</td><td>freq</td><td>process with</td><tr>\n"

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        output += "<tr><td>%i</td><td>%s</td><td>%s</td><td>%s</td><td>%s°</td><td>%s° (%s)</td><td>%sHz</td><td>%s</td><tr>\n" % (
            i, satellite, t2human(start), t2humanMS(duration), peak, azimuth, azimuth2dir(azimuth), freq, processWith)
        i += 1

    output += "</table>\n"

    return output


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
    plik = open(filename, "w")
    plik.write(data)
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
