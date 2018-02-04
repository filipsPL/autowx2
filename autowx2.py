#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
### autowx2
###


import predict
import time
from datetime import datetime
from time import gmtime, strftime
import subprocess
import os
import sys
from _crontab import *

from autowx2_conf import *  # configuration

#import pprint   # to remove after debugging
#pp = pprint.PrettyPrinter(indent=4)

satellites = list(satellitesData)
qth = (stationLat, stationLon, stationAlt)

def mkdir_p(outdir):
    ''' bash "mkdir -p" analog'''
    if not os.path.exists(outdir):
        os.makedirs(outdir)


class bc:
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
    tlefile=open(tleFileName, 'r')
    tledata=tlefile.readlines()
    tlefile.close()
    
    tleData=[]

    for i, line in enumerate(tledata):
        if satellite in line: 
            for n in tledata[i:i+3]: tleData.append(n.strip('\r\n').rstrip()),
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
        return {"fixedTime": parseCron(fixedTime), "fixedDuration": fixedDuration }
    except KeyError:
        return False

def genPassTable(howmany=20):
    '''generate a table with pass list, sorted'''
    
    passTable = {}
    for satellite in satellites:
        
        tleData = getTleData(satellite)
        priority =  satellitesData[satellite]['priority']
        
        if tleData != False:    # if tle data was there in the file :: SATELLITES
        
            czasStart=time.time()

            p = predict.transits(tleData, qth, czasStart)

            for i in range(1,howmany):
                transit = p.next()
                
                transitEnd = transit.start + transit.duration() - skipLast
                
                if not time.time() > transit.start + transit.duration() - skipLast - 1:  # esttimate the end of the transit, minus last 10 seconds
                    if int(transit.peak()['elevation'])>=minElev:
                        passTable[transit.start] = [satellite, int(transit.start + skipFirst), int(transit.duration() - skipFirst - skipLast), 
                                                    int(transit.peak()['elevation']), int(transit.peak()['azimuth']), priority]
                    # transit.start - unix timestamp
        
        else:                   # fixed time recording
            #cron = getFixedRecordingTime(satellite)["fixedTime"]
            cron = satellitesData[satellite]['fixedTime']
            duration = getFixedRecordingTime(satellite)["fixedDuration"]
            
            delta=0
            for i in range(0, howmany):
                entry = CronTab(cron).next(now=time.time() + delta, default_utc=False)
                delta+=entry
                start = delta + time.time()
                passTable[start] = [satellite, int(start), int(duration), '0', '0', priority]

    ## Sort pass table
    passTableSorted=[]
    for start in sorted(passTable):
        passTableSorted.append(passTable[start])
    
    ## Clean the pass table according to the priority. If any pass overlaps, remove one with less priority (lower priority number).
    passTableSortedPrioritized = passTableSorted[:]
    passCount = len(passTableSorted)
    for i in range(0, passCount - 1):   # -1 or -2 :BUG?
        satelliteI, startI, durationI, peakI, azimuthI, priorityI = passTableSorted[i]
        satelliteJ, startJ, durationJ, peakJ, azimuthJ, priorityJ = passTableSorted[i+1]
        endTimeI = startI + durationI

        if priorityI != priorityJ:
            if (startJ + priorityTimeMargin < endTimeI):
                #print "End pass:", satelliteI, t2human(endTimeI), "--- Start time:", satelliteJ, t2human(startJ)
                if priorityJ < priorityI:
                    #print " 1. discard %s, keep %s" % (satelliteI, satelliteJ)
                    passTableSortedPrioritized[i] = ''
                elif priorityJ > priorityI:
                    #print " 2. discard %s, keep %s" % (satelliteJ, satelliteI)
                    passTableSortedPrioritized[i+1] = ''
    
    
    # let's clean the table and remove empty (removed) records 
    # and remove the priority record, it will not be useful later -- x[:5]
    passTableSortedPrioritized = [ x[:5] for x in passTableSortedPrioritized if x != '']
    
    #pp.pprint(passTableSortedPrioritized)

    return passTableSortedPrioritized

def t2human(timestamp):
    '''converts unix timestamp to human readable format'''
    return strftime('%Y-%m-%d %H:%M', time.localtime(timestamp))

def t2humanMS(seconds):
    '''converts unix timestamp to human readable format MM:SS'''
    mm = int(seconds/60)
    ss = seconds % 60
    return "%02i:%02i" % (mm, ss)


def printPass(satellite, start, duration, peak, azimuth, freq,  processWith):
    return "● " + bc.OKGREEN + "%10s" % (satellite) + bc.ENDC + " :: " \
    + bc.OKGREEN + t2human(start) + bc.ENDC + " to " + bc.OKGREEN  + t2human(start+int(duration)) + bc.ENDC \
    + ", dur: " + t2humanMS(duration) \
    + ", max el. " +str(int(peak)) + "°" + "; azimuth: "+ str(int(azimuth))+"° (" + azimuth2dir(azimuth) + ") f=" + str(freq) + "Hz; Decoding: " + str(processWith)

def listNextPases(passTable, howmany):
    i=1
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq   = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']
        log(printPass(satellite, start, duration, peak, azimuth, freq, processWith))
        i+=1

def runForDuration(cmdline, duration):
    cmdline = [str(x) for x in cmdline]
    try:
        child = subprocess.Popen(cmdline)
        time.sleep(duration)
        child.terminate()
    except OSError as e:
        print "OS Error during command: "+" ".join(cmdline)
        print "OS Error: "+e.strerror

def justRun(cmdline):
    '''Just run the command as long as necesary and return the output'''
    cmdline = [str(x) for x in cmdline]
    try:
        child = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
        result = child.communicate()[0]
        return result
    except OSError as e:
        print "OS Error during command: "+" ".join(cmdline)
        print "OS Error: "+e.strerror

def getDefaultDongleShift(dongleShift=dongleShift):
    log("Reading the default dongle shift")
    if os.path.exists(dongleShiftFile):
        f = open(dongleShiftFile, "r")
        newdongleShift = f.read().strip()
        f.close()
        
        if newdongleShift != '' and is_number(newdongleShift): # WARNING and newdongleShift is numeric:
            dongleShift = str(float(newdongleShift))
            log("Recently used dongle shift is: " + str(dongleShift) + " ppm")
        else:  
            print "else"
            log("Using the default dongle shift: " + str(dongleShift) + " ppm")

        return dongleShift

def calibrate(dongleShift=dongleShift):
    '''calculate the ppm for the device'''
    cmdline = [baseDir + 'bin/kalibruj.sh']
    newdongleShift = justRun(cmdline).strip()
    if newdongleShift != '' and is_number(newdongleShift):
        log("Recalculated dongle shift is: " + str(newdongleShift) + " ppm")
        return str(float(newdongleShift))
    else:
        log("Using the good old dongle shift: " + str(dongleShift) + " ppm")
        return dongleShift


def azimuth2dir(azimuth):
    ''' convert azimuth in degrees to wind rose directions (16 wings)'''
    dirs = ["N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE", 
            "S", "SSW", "SW", "WSW", 
            "W", "WNW", "NW", "NNW", ]

    part = int( float(azimuth)/360*16 )
    return dirs[part]
    

def log(string, style=bc.CYAN):
    print bc.BOLD + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M'), bc.ENDC, style, str(string), bc.ENDC


# ------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":

    dongleShift = getDefaultDongleShift()

    while True:
        
        # recalculate table of next passes
        passTable = genPassTable()
        
        log("Next five passes:")
        listNextPases(passTable, 5)

        # get the very next pass
        satelitePass = passTable[0]
        
        satellite, start, duration, peak, azimuth = satelitePass
        
        freq   = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']
        
        fileNameCore = datetime.fromtimestamp(start).strftime('%Y%m%d-%H%M') + "_" + satellite
        
        log("Next pass:")
        log(printPass(satellite, start, duration, peak, azimuth, freq, processWith))

        towait = int(start-time.time())

        if towait <= 1 and duration > 0:
            ## here the recording happens
            log("!! Recording " + printPass(satellite, start, duration, peak, azimuth, freq, processWith), style=bc.WARNING)
                    
            processCmdline = [ processWith, fileNameCore, satellite, start, duration+towait, peak, azimuth, freq ]
            justRun(processCmdline)
            time.sleep(10.0)
            
        else:
            # recalculating waiting time

            if towait > 120:
                    log("Recalibrating the dongle...")
                    dongleShift = calibrate() # replace the global value
            
            towait = int(start-time.time())
            
            if scriptToRunInFreeTime != False:
                if towait >= 60: # if we have more than five minutes spare time, let's do something useful
                    log("We have still %ss free time to the next pass. Let's do something useful!" % ( t2humanMS(towait-1) ) )
                    log("Running: %s for %ss" % (scriptToRunInFreeTime, t2humanMS(towait-1)) )
                    runForDuration([scriptToRunInFreeTime, towait-1, dongleShift], towait-1)    # scrript with runt ime and dongle shift as arguments
                else:
                    log("Sleeping for: " + t2humanMS(towait-1) + "s")
                    time.sleep(towait-1)
            else:
                towait = int(start-time.time())
                log("Sleeping for: " + t2humanMS(towait-1) + "s")
                time.sleep(towait-1)



