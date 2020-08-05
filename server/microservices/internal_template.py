from client.microservice import Microservice
import threading
import json
import logging


class internal_Template(Microservice):
    def __init__(self, name, description, endpoints, endpointFuncs):
        super().__init__(name=name, description=description, endpoints=endpoints, clientID=0)
        self.endpointFuncs = endpointFuncs

    def receiveRequest(self, request):
        request = json.loads(request)
        args = json.dumps(request)
        print(args)
        print(self.endpointFuncs[request["endpoint"]])
        thread = threading.Thread(target=self.endpointFuncs[request["endpoint"]]["function"], args=(args,))
        thread.start()

    def run(self):
        print("test")
        thread = threading.Thread(target=self._runloop, args=())
        thread.start()

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
