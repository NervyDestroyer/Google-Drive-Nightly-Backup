import subprocess
import traceback
import os
import re

from .log import setup_logging, log_msg

# Timeout for 8 hours in seconds
TIMEOUT_8HOURS = 8 * 60 * 60

# start_and_manage_gdrive
#
# Starts and manages the gdrive process, killing upon nightly program termination
#
# Should be run as a separate multiprocessing.Process with
# multiprocessing.set_executable(os.path.join(sys.exec_prefix, "pythonw.exe")) set and passed the
# recv connection portion of a multiprocessing.Pipe.
#
# We need pythonw.exe because TaskScheduler will kill the terminal window which also includes
# this process. In order to properly clean up and kill Google Drive Desktop, we use pythonw.exe
# which detaches the python process from the terminal. In order to mitigate potential security
# issues, this process will initialize cleanup and shutdown after 8 hours regardless if the parent
# has died or not.
#
# When the parent process dies, the garbage collector will close the pipe connection which will
# signal to the child process to kill the Google Drive Desktop proc
def start_and_manage_gdrive(pipe_conn, gdrive_desktop_root):
    setup_logging("gdrive_manager")
    try:
        gdrive_desktop_path = find_google_dfs_from_root(gdrive_desktop_root)

        log_msg("Google Drive Binary: %s" % gdrive_desktop_path)

        gdrive_desktop = subprocess.Popen(gdrive_desktop_path)

        log_msg("Started Google Drive desktop")

        # Poll (blocking) the parent with the pipe. We assume that any message actually received
        # indicates shutdown. If an exception occurs the parent process closed the connection
        # due to shutdown or other. Either way, we initiate shutdown.
        #
        # If 8 hours have passed (timeout), we initialize shutdown to avoid potential security
        # issues with zombie processes.
        pipe_conn.poll(TIMEOUT_8HOURS)
    except:
        tb = traceback.format_exc()
        log_msg("Caught exception. Failed pipe exception is normal and means the parent process " \
            "initiated shutdown.")
        log_msg(str(tb))

    # Initialize shutdown and cleanup
    log_msg("Killing Google Drive Desktop")
    gdrive_desktop.kill()

    return

# find_google_dfs_from_root
# Finds the most up to date google dfs executable and returns the path to it
def find_google_dfs_from_root(gdrive_root):
    all_folders = \
        [f for f in os.listdir(gdrive_root) if os.path.isdir(os.path.join(gdrive_root, f))]

    # Get all folders of the form %d.%d.%d.%d (what Google names their versions under the root dir)
    regex = "[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+$"
    versions = sorted([f for f in all_folders if bool(re.match(regex, f))])

    versions = [os.path.join(gdrive_root, f) for f in versions]

    if(len(versions) == 0):
        raise ValueError("No GoogleFS versions detected...")

    # Since we sorted, most up to date version will be the last entry
    return os.path.join(versions[-1], "GoogleDriveFS.exe")
