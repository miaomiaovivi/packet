import getopt
import json
import os
import requests
import sys
import constant as const

from server import Server, RequestHandler
from criu import CRIU


class Monitor(object):
    _COMPUTE_PORT = None
    _COMPUTE_HOST = "http://127.0.0.1"
    _CRIU_DIR = "criu_dump"
    _PREV_CRIU_DIR = "criu_prev_dump"
    _PAIR = ""
    _ROLE = ""

    def __init__(self):
        """
        initialize this method with a CRIU object which will be used for
        checkpointing and restoring.
        """
        #TODO COMPLETE ME

    def _dump_and_sync(self, pid):
        """
        you should run a dump on the currently running process and sync the
        contents of this folder with that of the pair machine. You could choose
        to delegate the synchronization task to an external command "rsync",
        or write your own python helper methods to sync the dir contents.
        """
        #TODO COMPLETE ME

    def compute(self, payload):
        """
        the expected behavior of this method is, it should not accept any
        request if the role is not ACTIVE, or if the compute server is not
        running.

        It should hold the request if it is currently syncing the criu dump.

        Then, it should attempt to contact with the compute server in the local
        machine. Return the response as is from the local machine if it
        received a response. Otherwise, tell the scheduler that it should
        switch roles of the machines from ACTIVE to STANDBY and STANDBY to
        ACTIVE.

        should return a tuple with status code as first argument and message
        as the second
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.compute.__name__

    def register(self, payload):
        """
        the server that computes will register itself with the monitoring
        service in this method. Please make sure that this compute service can
        only run when the monitoring service has an ACTIVE role.

        if this is an ACTIVE monitoring service, and this is the first time you
        have got a call to register the compute server, you could choose to
        store the CRIU pre dump contents in this path.

        should return a tuple with status code as first argument and message
        as the second
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.register.__name__

    def active(self):
        """
        if this function is called, the scheduler has assigned the role to the
        current node to be ACTIVE. Since this service didn't start as ACTIVE,
        and has been constantly syncing the criu dump content locally, this
        service is made ACTIVE by the scheduler, hence it should restore the
        service from the current dump content.

        should return a tuple with status code as first argument and message
        as the second
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.active.__name__

    def standby(self):
        """
        if this function is called, the scheduler has assigned the role to the
        current node to be STANDBY

        should return a tuple with status code as first argument and message
        as the second
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.standby.__name__

    def dumping(self, payload):
        """
        sets the dump status sent from the the peer monitor service.

        should return a tuple with status code as first argument and message
        as the second
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.dumping.__name__


class MonRequestHandler(RequestHandler):
    """
    An HTTP request handler that inherits RequestHandler and adds custom
    functionality to it that is useful for monitoring service
    """

    _monitor = Monitor()

    def process_args(self):
        """
        process the path and parameters passed in the GET request.
        The response of this class should be the class you want to display.

        should return a tuple with status code as first argument and message
        as the second
        """
        path, query_args = self.parse_get_args()
        if path == const.REGISTER_PATH:
            return self._monitor.register(query_args)
        elif path == const.ACTIVE_PATH:
            return self._monitor.active()
        elif path == const.STANDBY:
            return self._monitor.standby()
        elif path == const.COMPUTE_PATH:
            return self._monitor.compute(query_args)
        elif path == const.DUMPING_PATH:
            return self._monitor.dumping(query_args)
        else:
            return self.NOT_FOUND, "Error 404: Unknown path - %s" % path

    def do_GET(self):
        """
        GET requests land in this method, we let process_args handle to
        request and parse it into strings
        """
        status_code, response = self.process_args()
        self._set_headers(status_code)
        self.wfile.write(self.process_args())


def parse_args():
    options, remainder = getopt.getopt(sys.argv[1:],
            "p:r:", ["pair=", "role="])

    pair = None
    role = None

    for opt, arg in options:
	if opt in ('-p', '--pair'):
            pair = arg
	elif opt in ('-r', '--role'):
            role = arg

    if not pair or not role:
        print ("Usage: %s [OPTIONS]\n"
               "Where options are:\n"
               "    -p|--pair\t- the IP of the pair machine\n"
               "    -r|--role\t- the role of the current service\n"
               % sys.argv[0])
        sys.exit(const.ERROR)

    return (pair, role)


if __name__ == "__main__":
    pair, role = parse_args()
    Monitor._PAIR = pair
    Monitor._ROLE = role
    Server(MonRequestHandler, '0.0.0.0', 80)
