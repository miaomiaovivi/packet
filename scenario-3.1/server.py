from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse

import constant as const


class Server(object):
    """
    A simple web server class
    """
    def __init__(self, request_handler, host='', port=80):
        """
        Starts the web server and delegate the calls to the request_handler
        object
        """
        server_addr = (host, port)
        httpd = HTTPServer(server_addr, request_handler)
        print ("Waiting for requests on port: %d" % server_addr[1])
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print ("\nGood bye!")


class RequestHandler(BaseHTTPRequestHandler):
    """
    An HTTP Request Handler with generic properties for all the webservers
    that will be running using this class.
    """
    STATUS_OK = const.STATUS_OK
    BAD_GATEWAY = const.BAD_GATEWAY
    NOT_FOUND = const.NOT_FOUND

    def _set_headers(self, status_code):
        """
        inform the client with the status of the request
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def parse_get_args(self):
        """
        parses the URL and returns the caller with the path used and the
        arguments passed in the URL in the form of a tuple
        """
        query = urlparse(self.path).query
        path = urlparse(self.path).path
        params = [qc.split("=") for qc in query.split("&")]
        if params == [['']]:
            param_dict = {}
        else:
            param_dict = dict(params)
        return (path, param_dict)
