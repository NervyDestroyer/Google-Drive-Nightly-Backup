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
import traceback
import time
import shutil
import multiprocessing
from datetime import datetime

from utilities.log import setup_logging, log_msg
from utilities.sync import sync_folders
from utilities.gdrive_desktop import start_and_manage_gdrive

# Get directory of this file
THIS_DIR = os.path.split(__file__)[0]

SYNC_DIR = os.path.join(THIS_DIR, "ToSync")
EXTRA_SYNC_CONFIG = os.path.join(THIS_DIR, "extra_sync_folders.csv")
MOVE_DIR = os.path.join(THIS_DIR, "sync_started_%s" % datetime.now().strftime("%m%d%Y_%H%M%S"))

# parse_args
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-copy_location", type=str, default="G:/My Drive/", \
        help="Location in Google Drive to copy files to start syncing")
    parser.add_argument("--debug", action="store_true", \
        help="Runs the gdrive manager in debug mode. Must be used if running from a console such " \
            "such as Powershell. Do not set if running with TaskScheduler.")

    return parser.parse_args()

# main
def main():
    # setup logging
    setup_logging("main")

    # Will catch all exceptions and log to file and console
    try:
        args = parse_args()

        # If not in debug mode, run manager as a pythonw process so it is detached from our terminal
        if(not args.debug):
            multiprocessing.set_executable(os.path.join(sys.exec_prefix, "pythonw.exe"))

        # Get pipe for communicating heartbeats between parent and child so child knows when parent dies
        gdrive_conn, _ = multiprocessing.Pipe()

        # This process will properly clean itself up after this process dies.
        # NOTE: If debug is enabled, this process is tied to our terminal window which will not work
        #   with TaskScheduler
        gdrive_manager_proc = multiprocessing.Process(target=start_and_manage_gdrive, args=(gdrive_conn, "C:/Program Files/Google/Drive File Stream/54.0.3.0/GoogleDriveFS.exe"))
        gdrive_manager_proc.start()

        # Wait for gdrive directory to exist (wait an additional 5 seconds afterwards just in case)
        log_msg("Sleeping until Gdrive directory exists...")
        while(not os.path.exists(args.copy_location)):
            time.sleep(1)

        log_msg("Gdrive directory found, sleeping an additional 10 seconds (for sanity)")
        time.sleep(10)

        # First copy all files in ToSync and move them to a separate dir (one time copies)
        sync_folders(SYNC_DIR, args.copy_location)

        files_to_move = [f for f in os.listdir(SYNC_DIR) if f != ".gitignore"]
        if(len(files_to_move) > 0):
            os.makedirs(MOVE_DIR)
            [shutil.move(os.path.join(SYNC_DIR, f), MOVE_DIR) for f in files_to_move]

        # Sleep until the gdrive manager dies or we are killed
        log_msg("Sleeping until killed or gdrive manager process dies")
        gdrive_manager_proc.join()

    except Exception:
        formatted_exc = traceback.format_exc()
        log_msg(formatted_exc)

    print("Exiting...")

if __name__ == "__main__":
    main()
