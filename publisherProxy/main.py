import io
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

from drivermanager import drivermanager


class WebController(BaseHTTPRequestHandler):
    def _set_response(self, response_message):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        request = Request("GET", self.path, str(self.headers))
        manager = drivermanager.DriverManager('C:/Users/deenfer2/PycharmProjects/applicationProxy/driver-manager.yml')
        # manager.publish("temp-livingroom",100)
        response = manager.request_response(request)

        self._set_response(response)

        my_json = json.load(io.BytesIO(response))

        self.wfile.write(my_json.encode('utf8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


class Request(object):
    def __init__(self, method, path, headers, payload=None) -> None:
        self.method = method
        self.path = path
        self.headers = headers
        self.payload = payload

    def get_request(self):
        return self


def run(server_class=HTTPServer, handler_class=WebController, port=8081):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
