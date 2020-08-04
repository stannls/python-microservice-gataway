from ..client.microservice import Microservice
from ..server.microservice_server import new_message
import threading
import json
import logging


class internal_Template(Microservice):
    def __init__(self, name, description, endpoints, endpointFuncs, server, client):
        Microservice.__init__(name, description, endpoints, clientID=0)
        self.client = client
        self.server = server
        self.endpointFuncs = endpointFuncs

    def receiveRequest(self, request):
        self.endpointFuncs[request["endpoint"]](data=request["data"])

    def returnDummyResponse(self, response):
        new_message(self.client, self.server, response)

    def run(self):
        thread = threading.Thread(target=self._runloop(), args=())

    def _runloop(self):
        while True:
            if self.check_queue():
                queueLen = 0
                self.receiveRequest(json.dumps(
                    self.execute_queue()))
                self.queue[0].isSend = True
                while self.check_queue():
                    if queueLen != len(self.queue):
                        for i in range(len(self.queue)):
                            if self.check_queue_response(i) is False and self.queue[i].isSend is False:
                                self.receiveRequest(json.dumps(
                                    self.execute_queue(
                                        position=i)))
                                self.queue[i].isSend = True
                                logging.info("Added client")
                        queueLen = len(self.queue)
