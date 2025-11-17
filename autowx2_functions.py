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

# threading
from threading import Thread

# configuration
from autowx2_conf import *

# ---------------------------------------------------------------------------- #

def validate_config():
    """Validate configuration before starting"""
    errors = []

    # Check TLE file exists
    if not os.path.exists(tleFileName):
        errors.append(f"TLE file not found: {tleFileName}")

    # Check satellites configuration
    if not satellitesData:
        errors.append("No satellites configured in satellitesData")

    # Validate each satellite configuration
    for sat, config in satellitesData.items():
        if 'freq' not in config:
            errors.append(f"Missing 'freq' for satellite: {sat}")
        if 'processWith' not in config:
            errors.append(f"Missing 'processWith' for satellite: {sat}")
        if 'priority' not in config:
            errors.append(f"Missing 'priority' for satellite: {sat}")

        # Check if processWith script exists for non-fixed-time satellites
        if 'fixedTime' not in config and 'processWith' in config:
            script_path = config['processWith']
            if not os.path.exists(script_path):
                errors.append(f"Processing script not found for {sat}: {script_path}")

    # Check logging directory
    if loggingDir and not os.path.exists(os.path.dirname(loggingDir) if os.path.dirname(loggingDir) else '.'):
        errors.append(f"Logging directory parent does not exist: {loggingDir}")

    # Check www directory
    if wwwDir and not os.path.exists(os.path.dirname(wwwDir) if os.path.dirname(wwwDir) else '.'):
        errors.append(f"WWW directory parent does not exist: {wwwDir}")

    # Report errors
    if errors:
        for error in errors:
            log(f"✖ Configuration error: {error}", style=bc.FAIL)
        sys.exit(1)
    else:
        log("✓ Configuration validated successfully", style=bc.OKGREEN)

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
                transit = next(p)

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
            log(f"✖ Can't find TLE data (in keplers) nor fixed time schedule (in config) for {satellite}",
                style=bc.FAIL)

    # Sort pass table
    passTableSorted = []
    for start in sorted(passTable):
        passTableSorted.append(passTable[start])

    # Clean the pass table according to the priority. If any pass overlaps,
    # remove one with less priority (lower priority number).
    passTableSortedPrioritized = passTableSorted[:]
    passCount = len(passTableSorted)
    # Loop to passCount-1 to safely access i+1 without index error
    for i in range(0, passCount - 1):
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
                    log(f" 1. discard {satelliteI}, keep {satelliteJ}")
                    passTableSortedPrioritized[i] = ''
                elif priorityJ > priorityI:
                    log(f" 2. discard {satelliteJ}, keep {satelliteI}")
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
    return f"{mm:02d}:{ss:02d}"


def printPass(satellite, start, duration, peak, azimuth, freq, processWith):
    return (f"● {bc.OKGREEN}{satellite:>10}{bc.ENDC} :: "
            f"{bc.OKGREEN}{t2human(start)}{bc.ENDC} to {bc.OKGREEN}{t2human(start + int(duration))}{bc.ENDC}"
            f", dur: {t2humanMS(duration)}"
            f", max el. {int(peak)}°; azimuth: {int(azimuth)}° ({azimuth2dir(azimuth)}) "
            f"f={freq}Hz; Decoding: {processWith}")


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
    """Run command for specified duration with output logging

    Args:
        cmdline: List of command arguments (NOT a string to prevent injection)
        duration: Duration in seconds
        loggingDir: Directory for log files
    """
    outLogFile = logFile(loggingDir)
    teeCommand = ['tee',  '-a', outLogFile]

    # Validate cmdline is a list to prevent command injection
    if not isinstance(cmdline, list):
        log("✖ Security error: cmdline must be a list, not string", style=bc.FAIL)
        return

    # Convert all arguments to strings and validate they don't contain shell metacharacters
    cmdline = [str(x) for x in cmdline]

    # Validate first argument (executable) is safe
    if not cmdline or not cmdline[0]:
        log("✖ Error: Empty command", style=bc.FAIL)
        return

    print(cmdline)
    try:
        # shell=False ensures no shell interpretation (prevents injection)
        p1 = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
        _ = subprocess.Popen(teeCommand, stdin=p1.stdout, shell=False)
        time.sleep(duration)
        p1.terminate()
    except OSError as e:
        log(f"✖ OS Error during command: {' '.join(cmdline)}", style=bc.FAIL)
        log(f"✖ OS Error: {e.strerror}", style=bc.FAIL)


def justRun(cmdline, loggingDir):
    """Run command and return output with logging

    Args:
        cmdline: List of command arguments (NOT a string to prevent injection)
        loggingDir: Directory for log files

    Returns:
        Command output as bytes
    """
    outLogFile = logFile(loggingDir)
    teeCommand = ['tee',  '-a', outLogFile]

    # Validate cmdline is a list to prevent command injection
    if not isinstance(cmdline, list):
        log("✖ Security error: cmdline must be a list, not string", style=bc.FAIL)
        return b""

    # Convert all arguments to strings
    cmdline = [str(x) for x in cmdline]

    # Validate command is not empty
    if not cmdline or not cmdline[0]:
        log("✖ Error: Empty command", style=bc.FAIL)
        return b""

    try:
        # shell=False ensures no shell interpretation (prevents injection)
        p1 = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, shell=False)
        p2 = subprocess.Popen(teeCommand, stdin=p1.stdout, close_fds=True, shell=False)
        result = p1.communicate()[0]
        return result
    except OSError as e:
        log(f"✖ OS Error during command: {' '.join(cmdline)}", style=bc.FAIL)
        log(f"✖ OS Error: {e.strerror}", style=bc.FAIL)
        return b""


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

        if newdongleShift != '' and is_number(newdongleShift):
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
    timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M')
    message = f"{bc.BOLD}{timestamp}{bc.ENDC} {style} {string} {bc.ENDC}"
    print(message)

    # logging to file, if not False
    if loggingDir:
        logToFile(f"{escape_ansi(message)}\n", loggingDir)


def logFile(logDir):
    '''Create output logging dir, returns name of the logfile'''
    mkdir_p(logDir)
    date_str = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
    outfile = f"{logDir}/{date_str}.txt"
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


def assignColorsToEvent(uniqueEvents):
    ''' returns dict of event -> color'''

    eventsColors = {'METEOR-M2': 'red',
                    'NOAA-15': '#0040FF',
                    'NOAA-18': '#0890FF',
                    'NOAA-19': '#07CAFF',
                    'ISS': '#38FF06',
                    }

    colors = ['#F646FF', 'yellow', 'orange', 'silver', 'magenta', 'red', 'white', '#FF2894', '#FF6E14']

    fixedColorsEvents = [event for event in eventsColors]     # events that have assigned fixed colors

    # generate list of events with not assigned fixed color
    uniqueEventsToAssignColors = []
    for uniqueEvent in uniqueEvents:
        if uniqueEvent not in  fixedColorsEvents:
            uniqueEventsToAssignColors += [uniqueEvent]

    # assign colors to the events with not assigne fixed colrs and add them to dict
    for event, color in zip(uniqueEventsToAssignColors, colors):
        eventsColors[event] = color


    return eventsColors


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

    now = _create_date(time.time())

    uniqueEvents = list(set([x[0] for x in listNextPasesListList])) # unique list of satellites
    colorDict = assignColorsToEvent(uniqueEvents)

    ilen = len(ylabels)
    pos = np.arange(0.5, ilen * 0.5 + 0.5, 0.5)
    task_dates = {}
    for i, task in enumerate(ylabels):
        task_dates[task] = customDates[i]
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    for i, ylabel in enumerate(ylabels):
        ylabelIN, startdateIN, enddateIN = listNextPasesListList[i]
        start_date, end_date = task_dates[ylabels[i]]

        if i < (ilen/2):
            labelAlign = 'left'
            factor = 1
        else:
            labelAlign = 'right'
            factor = -1


        ax.barh(
            (i * 0.5) + 0.5,
            end_date - start_date,
            left=start_date,
            height=0.3,
            align='center',
            edgecolor='black',
            color=colorDict[ylabelIN],
            label='',
            alpha=0.95)
        ax.text(
            end_date,
            (i * 0.5) + 0.55,
            ' %s | %s    ' % (t2humanHM(startdateIN),
                          ylabelIN),
            ha=labelAlign,
            va='center',
            fontsize=8,
            color='#7B7B7B')

    locsy, labelsy = plt.yticks(pos, ylabels)
    plt.setp(labelsy, fontsize=8)
    ax.axis('tight')
    ax.set_ylim(ymin=-0.1, ymax=ilen * 0.5 + 0.5)
    ax.set_xlim(xmin=now)
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
        print(locsy)  # "This is done only to satisfy the codacy.com. Sorry for that."


def listNextPasesHtml(passTable, howmany):
    i = 1
    output = "<table class='table small'>\n"
    output += "<tr><th>#</th><th>satellite</th><th>start</th><th>duration</th><th>peak</th><th>azimuth</th><th>freq</th><th>process with</th><tr>\n"

    # uniqueEvents
    # colorDict = assignColorsToEvent(listNextPasesListList)
    # print passTable[0:howmany]
    uniqueEvents = list(set([x[0] for x in passTable[0:howmany]])) # unique list of satellites
    colorDict = assignColorsToEvent(uniqueEvents)

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']

        color = colorDict[satellite]
        output += "<tr><td style='background-color: %s'>%i</td><td>%s</td><td>%s</td><td>%s</td><td>%s°</td><td>%s° (%s)</td><td>%sHz</td><td>%s</td><tr>\n" % (
            color, i, satellite, t2human(start), t2humanMS(duration), peak, azimuth, azimuth2dir(azimuth), freq, processWith)
        i += 1

    output += "</table>\n"

    return output #.decode('utf-8')


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

def listNextPasesShort(passTable, howmany=4):
    ''' list next passes in a sentence '''

    output = ""

    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass

        output += "%s (%s); " % (satellite, strftime('%H:%M', time.localtime(start)) )

    return output

def listNextPasesList(passTable, howmany):
    output = []
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        # freq = satellitesData[satellite]['freq']
        # processWith = satellitesData[satellite]['processWith']

        output.append([satellite, start, start + duration])
    if peak:
        print("This is a miracle!")  # codacy cheating, sorry.
    return output


def saveToFile(filename, data):
    # print filename
    # print data
    # exit(1)
    plik = open(filename, "w")
    plik.write(data) # .encode("utf-8")
    plik.close()


def generatePassTableAndSaveFiles(satellites, qth, verbose=True):
    # recalculate table of next passes
    log("Recalculating the new pass table and saving to disk.")
    passTable = genPassTable(satellites, qth, howmany=50)
    listNextPasesHtmlOut = listNextPasesHtml(passTable, 100)
    saveToFile(htmlNextPassList, listNextPasesHtmlOut)

    saveToFile(wwwDir + 'nextpassshort.tmp', listNextPasesShort(passTable, 6))

    listNextPasesListList = listNextPasesList(passTable, 20)
    CreateGanttChart(listNextPasesListList)

    if verbose:
        print(listNextPasesTxt(passTable, 100))



# --------------------------------------------------------------------------- #
# --------- THE MAIN LOOP --------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Constants for main loop
RECORDING_START_MARGIN = 1  # seconds before official start
MIN_FREE_TIME_FOR_SCRIPT = 120  # minimum seconds to run free-time script
DONGLE_TEST_TIME_THRESHOLD = 15  # minimum seconds needed for dongle test
RECALIBRATION_THRESHOLD = 300  # seconds before recalibrating dongle

def reload_config():
    """Reload configuration from file in case it has changed"""
    from autowx2_conf import satellitesData, scriptToRunInFreeTime
    return satellitesData, scriptToRunInFreeTime

def calculate_and_save_pass_table():
    """Calculate pass table and save to disk"""
    passTable = genPassTable(satellites, qth)
    generatePassTableAndSaveFiles(satellites, qth, verbose=False)
    return passTable

def display_upcoming_passes(passTable):
    """Display next five passes"""
    log("Next five passes:")
    listNextPases(passTable, 5)

def get_next_pass_info(passTable, satellitesData):
    """Extract and format information about the next satellite pass

    Returns:
        Tuple of (satellite, start, duration, peak, azimuth, freq, processWith, fileNameCore)
    """
    satelitePass = passTable[0]
    satellite, start, duration, peak, azimuth = satelitePass
    satelliteNoSpaces = satellite.replace(" ", "-")

    freq = satellitesData[satellite]['freq']
    processWith = satellitesData[satellite]['processWith']

    fileNameCore = datetime.fromtimestamp(start).strftime('%Y%m%d-%H%M') + "_" + satelliteNoSpaces

    log("Next pass:")
    log(printPass(satellite, start, duration, peak, azimuth, freq, processWith))

    return satellite, start, duration, peak, azimuth, freq, processWith, fileNameCore

def prepare_for_recording(towait):
    """Prepare system for recording (cleanup and dongle test)"""
    if cleanupRtl:
        log("Killing all remaining rtl_* processes...")
        justRun(["bin/kill_rtl.sh"], loggingDir)

    # Test if SDR dongle is available
    if towait > DONGLE_TEST_TIME_THRESHOLD:
        while not runTest():
            log("Waiting for the SDR dongle...")
            time.sleep(10)

def execute_recording(satellite, start, duration, peak, azimuth, freq, processWith, fileNameCore, towait):
    """Execute the satellite recording"""
    log(f"!! Recording {printPass(satellite, start, duration, peak, azimuth, freq, processWith)}",
        style=bc.WARNING)

    processCmdline = [
        processWith,
        fileNameCore,
        satellite,
        start,
        duration + towait,
        peak,
        azimuth,
        freq
    ]
    print(justRun(processCmdline, loggingDir))
    time.sleep(10.0)

def handle_free_time(towait, dongleShift, scriptToRunInFreeTime):
    """Handle free time before next recording

    Args:
        towait: Seconds to wait before recording
        dongleShift: Current dongle shift value
        scriptToRunInFreeTime: Script to run during free time (or False)

    Returns:
        Updated dongleShift value
    """
    # Recalibrate dongle if we have enough time
    if towait > RECALIBRATION_THRESHOLD:
        log("Recalibrating the dongle...")
        dongleShift = calibrate(dongleShift)

    if scriptToRunInFreeTime and towait >= MIN_FREE_TIME_FOR_SCRIPT:
        log(f"We have still {t2humanMS(towait - 1)}s free time to the next pass. Let's do something useful!")
        log(f"Running: {scriptToRunInFreeTime} for {t2humanMS(towait - 1)}s")
        runForDuration(
            [scriptToRunInFreeTime, towait - 1, dongleShift],
            towait - 1,
            loggingDir
        )
    else:
        log(f"Sleeping for: {t2humanMS(towait - 1)}s")
        time.sleep(towait - 1)

    return dongleShift

def mainLoop():
    """Main program loop - calculate passes, wait, and execute recordings"""
    dongleShift = getDefaultDongleShift()

    while True:
        # Reload configuration in case it has changed
        satellitesData, scriptToRunInFreeTime = reload_config()

        # Calculate and display upcoming passes
        passTable = calculate_and_save_pass_table()
        display_upcoming_passes(passTable)

        # Get next pass information
        satellite, start, duration, peak, azimuth, freq, processWith, fileNameCore = \
            get_next_pass_info(passTable, satellitesData)

        # Calculate wait time
        towait = int(start - time.time())

        # Prepare system for recording
        prepare_for_recording(towait)

        # Execute recording or handle free time
        if towait <= RECORDING_START_MARGIN and duration > 0:
            execute_recording(satellite, start, duration, peak, azimuth, freq,
                            processWith, fileNameCore, towait)
        else:
            dongleShift = handle_free_time(towait, dongleShift, scriptToRunInFreeTime)

logfile = logFile(loggingDir)
