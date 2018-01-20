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
#import shutil
#import re
import sys

from noaa_conf import *

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
                passTable[transit.start] = [satellite, transit.start, transit.duration(), transit.peak()['elevation'] ]
    
    passTableSorted=[]
    for start in sorted(passTable):
        satellite, start, duration, peak = passTable[start]
        passTableSorted.append([satellite, int(start), int(duration), int(peak)])
    
    return passTableSorted


def printPass(satellite, start, duration, peak, freq, decodeWith):
    return "** " + satellite + " " +strftime('%d-%m-%Y %H:%M:%S', time.localtime(start))+" ("+str(int(start))+") to "+strftime('%d-%m-%Y %H:%M:%S', time.localtime(start+int(duration)))+" ("+str(int(start+int(duration)))+")"+", dur: "+str(int(duration))+" sec ("+str(time.strftime("%M:%S", time.gmtime(duration)))+"), max el. "+str(int(peak))+" deg." + " f=" + str(freq) + "Hz, Decoding: " + str(decodeWith)

def listNextPases(passTable, howmany):
    i=1
    for satelitePass in passTable[0:howmany]:
        satellite, start, duration, peak = satelitePass
        freq   = satellitesData[satellite]['freq']
        decodeWith = satellitesData[satellite]['decodeWith']
        log(str(i) + ") " + printPass(satellite, start, duration, peak, freq, decodeWith))
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

def getDefaultDongleShift():
    log("Reading the default dongle shift")
    if os.path.exists(dongleShiftFile):
        f = open(dongleShiftFile, "r")
        newdongleShift = f.read()
        f.close()
        if newdongleShift != '': # WARNING and newdongleShift is numeric:
            newdongleShift = str(float(newdongleShift))

        if newdongleShift != False:
            dongleShift = newdongleShift
            log("Recently used dongle shift is: " + str(dongleShift) + " ppm")
        else:
            log("Using the default dongle shift: " + str(dongleShift) + " ppm")
        return newdongleShift

def calibrate():
    '''calculate the ppm for the device'''
    cmdline = [systemDir + 'bin/kalibruj.sh']
    dongleShift = justRun(cmdline)
    if dongleShift != '':
        return str(float(dongleShift))
    else:
        return False

def recordFM(freq, fname, duration):
    '''Record audio via rtl_fm to fname'''
    log("Recording f=%s to file %s for %ss" % (freq, fname, duration) )
    cmdline = [rtl_fm_path,\
		'-f',str(freq),\
		'-s',sample,\
		'-g',dongleGain,\
		'-F','9',\
		'-l','0',\
		'-t','900',\
		'-A','fast',\
		'-E','offset',\
#		'-E','pad',\
		'-p',dongleShift,\
		fname]
    runForDuration(cmdline, duration)

def transcode(fname, fnameWav):
    '''Transcode raw to wav'''
    log("Transcoding %s" % (fname) )
    cmdlinesox = ['sox','-t','raw','-r',sample,'-es','-b','16','-c','1','-V1',fname,fnameWav,'rate',wavrate]
    subprocess.call(cmdlinesox)
    cmdlinetouch = ['touch','-r', fname, fnameWav]
    subprocess.call(cmdlinetouch)
    os.remove(fname)


def log(string, style=bc.HEADER):
    print bc.BOLD + datetime.datetime.fromtimestamp(time.time()).strftime('%Y/%m/%d %H:%M'), bc.ENDC, style, str(string), bc.ENDC


### DECODING

dongleShift = getDefaultDongleShift()

while True:
    
    # recalculate table of next passes
    passTable = genPassTable()
    
    log("Next five passes:")
    listNextPases(passTable, 5)
    
    
    # get the very next pass
    satelitePass = passTable[0]
    
    satellite, start, duration, peak = satelitePass
    
    freq   = satellitesData[satellite]['freq']
    decodeWith = satellitesData[satellite]['decodeWith']
    
    fileNameCore = datetime.datetime.fromtimestamp(start).strftime('%Y%m%d-%H%M') + "_" + satellite
    
    log("Next pass:")
    log(printPass(satellite, start, duration, peak, freq, decodeWith))

    towait = int(start-time.time())

    if towait < 1:
        ## here the recording happens
        log("!! Recording " + printPass(satellite, start, duration+towait, peak, freq, decodeWith), style=bc.WARNING)
        
        fullimgdir = "%s/%s/" % (imgdir, time.strftime("%Y/%m/%d"))
        mkdir_p(fullimgdir)
        
        recordFM(freq, recdir + fileNameCore + ".raw", duration+towait)
        transcode(recdir + fileNameCore + ".raw", recdir + fileNameCore + ".wav")
        
        if decodeWith != False:
            # decode here
            decodeCmdline = [ decodeWith, recdir + fileNameCore + ".wav", fullimgdir + fileNameCore, satellite, start, duration+towait, peak, freq ]
            justRun(decodeCmdline)
        
    else:
        # recalculating waiting time

        if towait > 120:
                log("Recalibrating the dongle...")
                newdongleShift = calibrate() # replace the global value
                if newdongleShift != False:
                    dongleShift = newdongleShift
                    log("Recalculated dongle shift is: " + str(dongleShift) + " ppm")
                else:
                    log("Using the good old dongle shift: " + str(dongleShift) + " ppm")
        
        towait = int(start-time.time())
        
        if scriptToRunInFreeTime != False:
            if towait >= 300: # if we have more than five minutes spare time, let's do something useful
                log("We have still %ss free time to the next pass. Let's do something useful!" % (towait) )
                runForDuration([scriptToRunInFreeTime, towait-1, dongleShift], towait-1)

        towait = int(start-time.time())

        log("Sleeping for: " + str(towait) + "s")
        time.sleep(towait)


