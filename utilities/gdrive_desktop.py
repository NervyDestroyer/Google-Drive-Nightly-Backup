import subprocess

from .log import setup_logging, log_msg

# Timeout for 12 hours in seconds
TIMEOUT_12HOURS = 12 * 60 * 60

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
# issues, this process will initialize cleanup and shutdown after 12 hours regardless if the parent
# has died or not.
#
# When the parent process dies, the garbage
# collector will close the pipe connection which will signal to the child process to kill the
# Google Drive Desktop proc
def start_and_manage_gdrive(pipe_conn, gdrive_desktop_path):
    setup_logging("gdrive_manager")

    gdrive_desktop = subprocess.Popen(gdrive_desktop_path)
    try:
        log_msg("Started Google Drive desktop")

        # Poll (blocking) the parent with the pipe. We assume that any message actually received
        # indicates shutdown. If an exception occurs the parent process closed the connection
        # due to shutdown or other. Either way, we initiate shutdown.
        #
        # If 12 hours have passed (timeout), we initialize shutdown to avoid potential security
        # issues with zombie processes.
        pipe_conn.poll(TIMEOUT_12HOURS)
    except:
        log_msg("Caught exception")

    # Initialize shutdown and cleanup
    log_msg("Killing Google Drive Desktop")
    gdrive_desktop.kill()

    return
