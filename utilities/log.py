import os

# Get directory of this file
LOG_DIR = "%s/.." % os.path.split(__file__)[0]

LOGFILE = None

# setup_logging
# sets up logging, should only be called once
def setup_logging(log_prefix):
    global LOGFILE

    LOGFILE = "%s/log_%s.txt" % (LOG_DIR, log_prefix)

    # Open and clear out any existing log file
    o_stream = open(LOGFILE, "w")
    o_stream.close()

# log_msg
# logs msg to both console and log
def log_msg(msg):
    global LOGFILE

    print(msg)
    with open(LOGFILE, "a") as o_stream:
        print(msg, file=o_stream)
