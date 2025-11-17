#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# autowx2 - The program for scheduling recordings and processing of the
# satellite and ground radio transmissions (like capturing of the weather
# APT images from NOAA satellites, voice messages from ISS, fixed time
# recordings of WeatherFaxes etc.)
# https://github.com/filipsPL/autowx2/
#

# Import specific functions to improve code clarity
# Note: Some wildcard imports remain for backward compatibility
from autowx2_functions import (
    log, saveToFile, justRun, mainLoop, validate_config,
    wwwDir, loggingDir, cleanupRtl, bc
)
import sys
import time
import traceback

# ------------------------------------------------------------------------------------------------------ #

if __name__ == "__main__":
    try:
        log("⚡ Program start")

        # Validate configuration before proceeding
        validate_config()

        saveToFile(f"{wwwDir}/start.tmp", str(time.time())) # saves program start date to file

        if cleanupRtl:
            log("Killing all remaining rtl_* processes...")
            justRun(["bin/kill_rtl.sh"], loggingDir)

        # Run main loop directly (Flask webserver removed)
        mainLoop()
    except KeyboardInterrupt:
        log("Program interrupted by user", style=bc.WARNING)
        sys.exit(0)
    except Exception as e:
        log(f"✖ Fatal error: {str(e)}", style=bc.FAIL)
        traceback.print_exc()
        sys.exit(1)
