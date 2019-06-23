import os
from datetime import datetime
import sys
from os.path import expanduser

home = expanduser("~")
log_dir = os.path.join(home, "Log")
date_time = datetime.now()
date_time_suffix = date_time.strftime('%Y%m%d%H%M%S')
log_file = os.path.join(log_dir, "bootLog_" + date_time_suffix + ".txt")
motion_log_file_path = os.path.join(log_dir, "motionLog.txt")

def measure_spec(spec):
    try:
        if not os.path.isdir(log_dir):
            print("Log directory - {0} doesn't exist, creating it".format(log_dir))
            os.makedirs(log_dir)

        motion_log_file = open(motion_log_file_path, "w")
        motion_log_file.write(spec)
        motion_log_file.close()
    except:
        print("Something went wrong")

def main(argv):
    try:
        if not os.path.isdir(log_dir):
            print("Log directory - {0} doesn't exist, creating it".format(log_dir))
            os.makedirs(log_dir)

        boot_log_file = open(log_file, "w")
        boot_log_file.write("Booted at " + date_time.strftime('%Y-%m-%d %H:%M:%S'))
        boot_log_file.close()
        print("Created log file - {0}".format(log_file))
    except:
        print("Something went wrong")

if __name__ == "__main__":
    main(sys.argv[1:])
