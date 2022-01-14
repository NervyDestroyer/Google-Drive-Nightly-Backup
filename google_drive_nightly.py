# Designed for use with Windows TaskScheduler or equivalent
#
# Will start Google Drive Desktop and copy files in ToSync to the specified Google Drive location
# to start the upload process
#
# Will move files that have had their sync started to a datestamped SyncStarted_<DATETIME> folder
#
# Extra sync folders can be specified via extra_sync_folders.csv. These are lightweight folders
# meant to be sync'd every night (such as a LiveSplit splits folder for example). These are
# designed to be overwritten with any new data every night. The format of the csv is:
#   FolderToSync,OutputLocation
#   ex: path/to/Splits,G:/Splits
#
# NOTE: File upload not guaranteed to be complete upon program exit, may take multiple nightly
# runs before the files are fully uploaded

import argparse
import os
import sys
from datetime import datetime
import traceback

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

    parser.add_argument("-gdrive_exec", type=str, default=None, help="Google drive executable to run")
    parser.add_argument("-copy_location", type=str, default="G:/My Drive/", help="Location in Google Drive to copy files to start syncing")

    return parser.parse_args()

# main
def main():
    cur_datetime = datetime.now().strftime("%m%d%Y_%H%M%S")
    errlog = "errlog_%s.txt" % cur_datetime

    # Will catch all exceptions and log to file and console
    try:
        args = parse_args()

        # Make sure we know where gdrive desktop is
        if(args.gdrive_exec is None):
            raise ValueError( \
                "Must specify Google Drive Desktop executable with -gdrive_exec argument")


    except Exception:
        formatted_exc = traceback.format_exc()
        log_err(formatted_exc, errlog)

if __name__ == "__main__":
    main()
