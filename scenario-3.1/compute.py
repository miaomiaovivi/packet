"""
YOU DON'T HAVE TO EDIT THIS FILE

You will be using the monitoring service and scheduler to ensure that this
process is always snapshotted and sync'd with the other node
"""
import getopt
import json
import os
import requests
import sys
import constant as const

from server import Server, RequestHandler


def parse_cmd_args():
    port = 8080

    options, remainder = getopt.getopt(sys.argv[1:],
            "p:h", ["port=", "help"])

    for opt, arg in options:
        if opt in ('-p', '--port'):
            try:
                port = int(arg)
            except ValueError:
                print ("Argument for port - %s - is not an integer" % arg)
                sys.exit(const.ERROR)
        elif opt in ("-h", "--help"):
            print ("Usage: %s [OPTIONS]\n"
                   "Where options are:\n"
                   "    -p|--port\t- the port number of the server\n"
                   % sys.argv[0])
            sys.exit(const.SUCCESS)

    return (port)


class Compute(object):
    """
    For each Get request it received, the compute object keeps track of all
    the total number of requests it has processed until now.

    While using CRIU dump, you will see that the in memory content of
    _requests_processed is sequentially growing even after the process has
    been restarted (via CRIU).
    """
    _requests_processed = 0

    def Get(self, query_components):
        # increment the requests processed count
        self._requests_processed += 1
        print("Requests processed: %d" % self._requests_processed)

        # generate a response for the server
        response = {
            const.PID: os.getpid(),
            const.NUM: query_components.get(const.NUM),
        }

        status_code = const.STATUS_OK
        if not response[const.NUM]:
            print "\nWARNING: Please pass 'num' param in the URL\n"
            status_code = const.BAD_GATEWAY
            response[const.NUM] = -1


        # return the contents
        return status_code, json.dumps(response)


class ComputeRequestHandler(RequestHandler):
    """
    An HTTP request handler that inherits RequestHandler and adds custom
    functionality to it.
    """

    _compute = Compute()

    def process_args(self):
        """
        process the path and parameters passed in the GET request.
        The response of this class should be the class you want to display.
        """
        _, query_args = self.parse_get_args()
        return self._compute.Get(query_args)

    def do_GET(self):
        """
        GET requests land in this method, we let process_args handle to
        request and parse it into strings
        """
        status_code, msg = self.process_args()
        self._set_headers(status_code)
        self.wfile.write(msg)


def register(port):
    """
    when this program starts it will register itself with the monitoring server
    it does by sending out the port it is listening at and the process ID of
    the current port.
    """
    path = "http://127.0.0.1%s" % const.REGISTER_PATH
    try:
        requests.get(path, params={
            const.PID: os.getpid(),
            const.PORT: port,
            })
    except requests.ConnectionError:
        print "Please start the monitoring service first"
        sys.exit(const.ERROR)

if __name__ == "__main__":
    # get the port number passed in the command line argument
    port = parse_cmd_args()
    # register the port and the process ID of this server with Monitor
    register(port)
    # start the web server
    Server(ComputeRequestHandler, '127.0.0.1', port)
