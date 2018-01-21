#!/usr/bin/env python
# -*- coding: utf-8 -*-

###
### autowx2
###


import predict
import time
import datetime
from time import gmtime, strftime
import subprocess
import os
import sys

from autowx2_conf import *

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
    return tleData  


def genPassTable():
    '''generate a table with pass list, sorted'''
    
    passTable = {}
    for satellite in satellites:
        
        tleData = getTleData(satellite)
        czasStart=time.time()

        p = predict.transits(tleData, qth, czasStart)

        for i in range(1,20):
            transit = p.next()

            if int(transit.peak()['elevation'])>=minElev:
                passTable[transit.start] = [satellite, transit.start, transit.duration(), transit.peak()['elevation'], transit.peak()['azimuth'] ]
    
    passTableSorted=[]
    for start in sorted(passTable):
        satellite, start, duration, peak, azimuth = passTable[start]
        passTableSorted.append([satellite, int(start), int(duration), int(peak), int(azimuth)])
    
    return passTableSorted


def printPass(satellite, start, duration, peak, azimuth, freq,  processWith):
    return "** " + satellite + " " +strftime('%d-%m-%Y %H:%M:%S', time.localtime(start))+" ("+str(int(start))+") to "+strftime('%d-%m-%Y %H:%M:%S', time.localtime(start+int(duration)))+" ("+str(int(start+int(duration)))+")"+", dur: "+str(int(duration))+" sec ("+str(time.strftime("%M:%S", time.gmtime(duration)))+"), max el. "+str(int(peak))+"°" + " Azimuth: "+ str(int(azimuth))+"° (" + azimuth2dir(azimuth) + ") f=" + str(freq) + "Hz, Decoding: " + str(processWith)

def listNextPases(passTable, howmany):
    i=1
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak, azimuth = satelitePass
        freq   = satellitesData[satellite]['freq']
        processWith = satellitesData[satellite]['processWith']
        log(str(i) + ") " + printPass(satellite, start, duration, peak, azimuth, freq, processWith))
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
    cmdline = [systemDir + 'bin/kalibruj.sh']
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
    print bc.BOLD + datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M'), bc.ENDC, style, str(string), bc.ENDC


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
        
        fileNameCore = datetime.datetime.fromtimestamp(start).strftime('%Y%m%d-%H%M') + "_" + satellite
        
        log("Next pass:")
        log(printPass(satellite, start, duration, peak, azimuth, freq, processWith))

        towait = int(start-time.time())

        if towait < 1:
            ## here the recording happens
            log("!! Recording " + printPass(satellite, start, duration+towait, peak, azimuth, freq, processWith), style=bc.WARNING)
                    
            processCmdline = [ processWith, fileNameCore, satellite, start, duration+towait, peak, azimuth, freq ]
            justRun(processCmdline)
            
        else:
            # recalculating waiting time

            if towait > 120:
                    log("Recalibrating the dongle...")
                    dongleShift = calibrate() # replace the global value
            
            towait = int(start-time.time())
            
            if scriptToRunInFreeTime != False:
                if towait >= 300: # if we have more than five minutes spare time, let's do something useful
                    log("We have still %ss free time to the next pass. Let's do something useful!" % (towait-1) )
                    log("Running: %s for %ss" % (scriptToRunInFreeTime, towait-1) )
                    runForDuration([scriptToRunInFreeTime, towait-1, dongleShift], towait-1)    # scrript with runt ime and dongle shift as arguments

            towait = int(start-time.time())

            log("Sleeping for: " + str(towait) + "s")
            time.sleep(towait)


