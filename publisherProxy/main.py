import io
import json

from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

import drivermanager


class WebController(BaseHTTPRequestHandler):
    manager = None

    def __init__(self, driver_config, *args):
        self.manager = drivermanager.DriverManager(driver_config)
        BaseHTTPRequestHandler.__init__(self, *args)

    def _set_response(self, response_message):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        request = Request("GET", self.path, str(self.headers))

        response = self.manager.request_response(request)

        self._set_response(response)

        my_json = json.load(io.BytesIO(response))

        self.wfile.write(my_json.encode('utf8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))

        request = Request("POST", self.path, str(self.headers), post_data.decode("utf-8"))

        self._send_to_topic_and_return(request)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(WebController, self).end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_to_topic_and_return(self, request):
        response = self.manager.request_response(request)

        self._set_response(response)

        my_json = json.load(io.BytesIO(response))

        self.wfile.write(my_json.encode('utf8'))


class Request(object):
    def __init__(self, method, path, headers, payload=None) -> None:
        self.method = method
        self.path = path
        self.headers = headers
        self.payload = payload

    def get_request(self):
        return self


def run(port=9993, config="../driver-manager.yml"):
    logging.basicConfig(level=logging.INFO)

    controller_class = partial(WebController, config)
    server = HTTPServer(('', port), controller_class)
    logging.info('Starting httpd with port ' + str(port))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    elif len(argv) >= 2:
        run(port=int(argv[1]), config=argv[2])
    else:
        run()
