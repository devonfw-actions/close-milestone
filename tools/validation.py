import os
import subprocess
import sys

from tools.logger import log_error


def check_running_in_bash():
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.call("ls", stdout=FNULL)
    except:
        log_error("Please run the script in a linux like environment (e.g. git bash)")
        sys.exit(1)
