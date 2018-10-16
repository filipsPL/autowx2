#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# autowx2 - The program for scheduling recordings and processing of the
# satellite and ground radio transmissions (like capturing of the weather
# APT images from NOAA satellites, voice messages from ISS, fixed time
# recordings of WeatherFaxes etc.)
# https://github.com/filipsPL/autowx2/
#


import predict
import time
from datetime import datetime
from time import strftime
import subprocess
import os
from _crontab import *
from tendo import singleton  # avoid two instancess
import re

from autowx2_conf import *  # configuration

me = singleton.SingleInstance()
                              # will sys.exit(-1) if other instance is running


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


def genPassTable(howmany=20):
    '''generate a table with pass list, sorted'''

    passTable = {}
    for satellite in satellites:

        tleData = getTleData(satellite)
        priority = satellitesData[satellite]['priority']

        if tleData:    # if tle data was there in the file :: SATELLITES

            czasStart = time.time()

            p = predict.transits(tleData, qth, czasStart)

            #d = predict.observe(tleData, qth)
            #print d['doppler'] ## doppler : doppler shift between groundstation and satellite.
            #exit(1)

            for i in range(1, howmany):
                transit = p.next()

                # transitEnd = transit.start + transit.duration() - skipLast

                if not time.time() > transit.start + transit.duration() - skipLast - 1:  # esttimate the end of the transit, minus last 10 seconds
                    if int(transit.peak()['elevation']) >= minElev:
                        passTable[transit.start] = [satellite, int(
                            transit.start + skipFirst), int(
                                transit.duration() - skipFirst - skipLast),
                            int(transit.peak()['elevation']), int(transit.peak()['azimuth']), priority
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
            print bc.FAIL + "ERROR: " + bc.ENDC + "Can't find TLE data (in keplers) nor fixed time schedule (in config) for " + satellite

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
                    print " 1. discard %s, keep %s" % (satelliteI, satelliteJ)
                    passTableSortedPrioritized[i] = ''
                elif priorityJ > priorityI:
                    print " 2. discard %s, keep %s" % (satelliteJ, satelliteI)
                    passTableSortedPrioritized[i + 1] = ''

    # let's clean the table and remove empty (removed) records
    # and remove the priority record, it will not be useful later -- x[:5]
    passTableSortedPrioritized = [x[:5]
                                  for x in passTableSortedPrioritized if x != '']

    # pp.pprint(passTableSortedPrioritized)

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


def runForDuration(cmdline, duration):
    cmdline = [str(x) for x in cmdline]
    try:
        child = subprocess.Popen(cmdline)
        time.sleep(duration)
        child.terminate()
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL )
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)

def justRun(cmdline):
    '''Just run the command as long as necesary and return the output'''
    cmdline = [str(x) for x in cmdline]
    try:
        child = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        result = child.communicate()[0]
        return result
    except OSError as e:
        log("✖ OS Error during command: " + " ".join(cmdline), style=bc.FAIL )
        log("✖ OS Error: " + e.strerror, style=bc.FAIL)


def runTest(duration=2):
    '''Check, if RTL_SDR dongle is connected'''
    child = subprocess.Popen('rtl_test', stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    time.sleep(duration)
    child.terminate()
    out, err = child.communicate()
    # if no device: ['No', 'supported', 'devices', 'found.']
    # if OK: ['Found', '1', 'device(s):', '0:', 'Realtek,', 'RTL2838UHIDIR,',...
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
            print "else"
            log("Using the default dongle shift: " + str(dongleShift) + " ppm")

        return dongleShift


def calibrate(dongleShift=dongleShift):
    '''calculate the ppm for the device'''
    if (calibrationTool != False):
        cmdline = [ calibrationTool ]
        newdongleShift = justRun(cmdline).strip()
        if newdongleShift != '' and is_number(newdongleShift):
            log("Recalculated dongle shift is: " + str(newdongleShift) + " ppm")
            return str(float(newdongleShift))
        else:
            log("Using the good old dongle shift: " + str(dongleShift) + " ppm")
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
    message = "%s%s%s %s %s %s " % (bc.BOLD, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M'), bc.ENDC, style, str(string), bc.ENDC)
    print message

    # logging to file, if not Flase
    if logging:
        logToFile(escape_ansi(message) + "\n", logging)


def logToFile(message, logDir):
    # save message to the file
    mkdir_p(logDir)
    outfile = "%s/%s.txt" % ( logDir, datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d') )

    file_append(outfile, message)


def file_append(filename, content):
  f = open( filename, 'a' )
  f.write(content)
  f.close()


# ------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":

    log("Program start")
    dongleShift = getDefaultDongleShift()

    while True:
        while not runTest():
            log("Waiting for the SDR dongle...")
            time.sleep(10)

        # recalculate table of next passes
        passTable = genPassTable()

        log("Next five passes:")
        listNextPases(passTable, 5)

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
            justRun(processCmdline)
            time.sleep(10.0)

        else:
            # recalculating waiting time

            if towait > 300:
                    log("Recalibrating the dongle...")
                    dongleShift = calibrate(dongleShift)  # replace the global value

            towait = int(start - time.time())

            if scriptToRunInFreeTime:
                if towait >= 60:  # if we have more than five minutes spare time, let's do something useful
                    log("We have still %ss free time to the next pass. Let's do something useful!" %
                        (t2humanMS(towait - 1)))
                    log("Running: %s for %ss" %
                        (scriptToRunInFreeTime, t2humanMS(towait - 1)))
                    runForDuration(
                        [scriptToRunInFreeTime,
                         towait - 1,
                         dongleShift],
                        towait - 1)
                                   # scrript with runt ime and dongle shift as
                                   # arguments
                else:
                    log("Sleeping for: " + t2humanMS(towait - 1) + "s")
                    time.sleep(towait - 1)
            else:
                towait = int(start - time.time())
                log("Sleeping for: " + t2humanMS(towait - 1) + "s")
                time.sleep(towait - 1)
