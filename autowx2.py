#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# autowx2 - The program for scheduling recordings and processing of the
# satellite and ground radio transmissions (like capturing of the weather
# APT images from NOAA satellites, voice messages from ISS, fixed time
# recordings of WeatherFaxes etc.)
# https://github.com/filipsPL/autowx2/
#


from autowx2_conf import *  # configuration
from autowx2_functions import *


me = singleton.SingleInstance()
                              # will sys.exit(-1) if other instance is running


satellites = list(satellitesData)
qth = (stationLat, stationLon, stationAlt)



# ------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":
    log("⚡ Program start")
    dongleShift = getDefaultDongleShift()

    while True:

        # recalculate table of next passes
        passTable = genPassTable(satellites, qth)

        # save table to disk
        generatePassTableAndSaveFiles(satellites, qth, verbose=False)

        # show next five passes
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
                    runForDuration(
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
