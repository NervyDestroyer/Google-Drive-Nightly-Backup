from datetime import datetime

ERRLOG = None

# setup_logging
# sets up error logging, should only be called once
def setup_logging():
    global ERRLOG

    cur_datetime = datetime.now().strftime("%m%d%Y_%H%M%S")
    ERRLOG = "errlog_%s.txt" % cur_datetime

# log_error
# logs error to both console and errlog
def log_err(msg):
    global ERRLOG

    print(msg)
    with open(ERRLOG, "a") as o_stream:
        print(msg, file=o_stream)
