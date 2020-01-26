#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# autowx2 - The program for scheduling recordings and processing of the
# satellite and ground radio transmissions (like capturing of the weather
# APT images from NOAA satellites, voice messages from ISS, fixed time
# recordings of WeatherFaxes etc.)
# https://github.com/filipsPL/autowx2/
#

# from autowx2_conf import *  # configuration
from autowx2_functions import *  # all functions and magic hidden here

# ------------------------------------------------------------------------------------------------------ #


if __name__ == "__main__":
    log("⚡ Program start")
    # saves program start date to file
    saveToFile("%s/start.tmp" % (wwwDir), str(time.time()))

    debugPrint("Main program started")

    if cleanupRtl:
        killRtl()

    while True:
        debugPrint("Main loop started")
        try:
            mainLoop()
        finally:
            print("[MAIN] Main loop exited for some reason. Check the logs.")
