"""
Some constants which you could use in your code. You can add more constants
if you want to, but please refrain from deleting any as there might be some
sample code that could be using these variables.
"""
# exit status of the program
SUCCESS = 0
ERROR = 1

# some constant values that are being/can be used as dictionary keys to
# store information or be used as strings to represent an information
# and also communicate with other machines

# to indicate that the synchronization of criu dump between ACTIVE and STANDBY
# is complete
COMPLETED = "completed"
# the key used as an argument for communicating the dump status
DUMP = "dump"
# to indicate that the monitoring service is about to start to dump
DUMPING = "dumping"
# to indicate that the pair is ACTIVE
ACTIVE = "active"
# to indicate that the pair is in STANDBY
STANDBY = "standby"

# the Process ID of the current program
PID = "pid"
# the port at which the current program is running
PORT = "port"

# number of seconds the program should sleep
SLEEP_TIME = 1

# URLS supported by the webserver
REGISTER_PATH = "/register"
ACTIVE_PATH = "/active"
STANDBY_PATH = "/standby"
COMPUTE_PATH = "/compute"
DUMPING_PATH = "/dumping"

# the param sent with /compute path
NUM = "num"

# some of the status codes for HTTP
STATUS_OK = 200
BAD_GATEWAY = 502
NOT_FOUND = 404
