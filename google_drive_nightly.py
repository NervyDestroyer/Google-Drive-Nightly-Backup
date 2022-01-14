# Designed for use with Windows TaskScheduler or equivalent
#
# Will wait for G:/ drive to be mounted by the Google Drive Desktop application that is started
# via TaskScheduler or equivalent before starting.
#
# Will move files that have had their sync started to a datestamped SyncStarted_<DATETIME> folder
#
# Extra sync folders can be specified via extra_sync_folders.csv. These are lightweight folders
# meant to be sync'd every night (such as a LiveSplit splits folder for example) IF ONE OF THE FILES
# CHANGED. These are designed to have multple days worth of backups (up to the max num backups).
# If the max num days worth of backups is met, the oldest backup is deleted. The format of the csv is:
#   FolderToSync,OutputLocation,MaxBackups
#   ex: path/to/Splits,G:/Splits,10
#
# NOTE: File upload not guaranteed to be complete upon program exit, may take multiple nightly
# runs before the files are fully uploaded

import argparse
import os
import sys
from datetime import datetime
import traceback
import filecmp
import shutil
import time

EXTRA_SYNC_CONFIG = "./extra_sync_folders.csv"

# log_error
# logs error to both console and errlog
def log_err(msg, errlog):
    print(msg)
    with open(errlog, "a") as o_stream:
        print(msg, file=o_stream)

# parse_args
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-copy_location", type=str, default="G:/My Drive/", help="Location in Google Drive to copy files to start syncing")

    return parser.parse_args()

# main
def main():
    cur_datetime = datetime.now().strftime("%m%d%Y_%H%M%S")
    errlog = "errlog_%s.txt" % cur_datetime

    # Will catch all exceptions and log to file and console
    try:
        args = parse_args()

        # Wait for gdrive directory to exist (wait an additional 5 seconds afterwards just in case)
        print("Sleeping until Gdrive directory exists...")
        while(not os.path.exists(args.copy_location)):
            time.sleep(1)

        print("Gdrive directory found, sleeping an additional 10 seconds (for sanity)")
        time.sleep(10)

    except Exception:
        formatted_exc = traceback.format_exc()
        log_err(formatted_exc, errlog)

if __name__ == "__main__":
    main()
