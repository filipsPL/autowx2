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


def serverLoop():
    # Debug print
    print("[DEBUG] Server started")
    time.sleep(2)
    app.run(debug=True, port=webInterfacePort)


if __name__ == "__main__":
    log("⚡ Program start")
    # saves program start date to file
    saveToFile("%s/start.tmp" % (wwwDir), str(time.time()))

    # Debug print
    print("[DEBUG] Main program started")
#     t1 = Thread(target = serverLoop)
#     t1.setDaemon(True)
#     t1.start

    if cleanupRtl:
        killRtl()

    while True:
        # Debug print
        print("[DEBUG] Main loop started")
        try:
            mainLoop()
        finally:
            print("[MAIN] Main loop exited for some reason. Check the logs.")
        #app.run(debug=True, port=webInterfacePort)

        #socketio.run(app, port=webInterfacePort, debug=False)
