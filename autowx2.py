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
from autowx2_functions import * # all functions and magic hidden here

from autowx2_webserver import *
from threading import Thread


# ------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":
    log("⚡ Program start")
    dongleShift = getDefaultDongleShift()
    # mainLoop()
    while True:
        t1 = Thread(target = mainLoop)
        t1.setDaemon(True)
        t1.start()
        app.run(debug=True)
