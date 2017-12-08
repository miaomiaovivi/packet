import getopt
import requests
import sys
import constant as const

from server import Server, RequestHandler


def parse_args():
    options, remainder = getopt.getopt(sys.argv[1:],
            "a:s:", ["active=", "standby="])
    active = None
    standby = None
    for opt, arg in options:
	if opt in ('-a', '--active'):
            active = arg
	elif opt in ('-s', '--standby'):
            standby = arg

    if not active or not standby:
        print ("Usage: %s [OPTIONS]\n"
               "Where options are:\n"
               "    -a|--active\t\t- the IP of the active machine\n"
               "    -s|--standby\t- the IP of the standby machine\n"
               % sys.argv[0])
        sys.exit(const.ERROR)

    return (active, standby)


class Scheduler(object):
    """
    The scheduler class forwards the query from client to the backend

    | client | ----> | Scheduler | ----> | Backend |

    The scheduler is the decision maker for reassigning the roles of the
    Backend midway (from STANDBY to ACTIVE and ACTIVE to STANDBY)
    """
    _ACTIVE = None
    _STANDBY = None

    def compute(self, payload):
        """
        handler method for "/compute", this function should first contact the
        _ACTIVE host. If the _ACTIVE host responds with a failure message,
        the scheduler updates the monitoring service in both the nodes with the
        updated swapped roles (ie, _ACTIVE host becomes _STANDBY, _STANDBY
        becomes _ACTIVE)

        arguments:
            payload - the parameters passed in the GET URL from client
        """
        #TODO COMPLETE ME

        return const.STATUS_OK, self.compute.__name__

class SchedulerRequestHandler(RequestHandler):
    """
    An HTTP request handler that inherits RequestHandler and adds custom
    functionality to it.
    """

    _scheduler = Scheduler()

    def process_args(self):
        """
        process the path and parameters passed in the GET request.
        The response of this class should be the class you want to display.
        """
        path, query_args = self.parse_get_args()
        print path, query_args
        if path == const.COMPUTE_PATH:
            return self._scheduler.compute(query_args)

        return const.NOT_FOUND, "Invalid path %s" % (path)

    def do_GET(self):
        """
        GET requests land in this method, we let process_args handle to
        request and parse it into strings
        """

        status_code, msg = self.process_args()
        self._set_headers(status_code)
        self.wfile.write(self.process_args())


if __name__ == "__main__":
    active, standby = parse_args()
    Scheduler._ACTIVE = active
    Scheduler._STANDBY = standby
    Server(SchedulerRequestHandler, '0.0.0.0', 80)
