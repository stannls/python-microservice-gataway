import time
import json
import logging
import threading
import re

uuid4hex = re.compile("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}", re.I)


class internal:
    def __init__(self):
        self.microservices = {}

    def register(self, microservice, is_internal=False):
        self.microservices[microservice.name] = {"internal": is_internal, "microservice": microservice}

    def registerCheck(self, request):
        if request["data"]["name"] not in self.microservices:
            return True
        else:
            return False

    def run(self, microservice, clients, server=None, client=None):
        if self.microservices[microservice.name]["internal"] is False:
            thread = threading.Thread(target=self._runloop, args=(client, server, microservice, clients))
            thread.daemon = True
            thread.start()
        else:
            self.microservices[microservice.name]["microservice"].run()

    def _runloop(self, client, server, microservice, clients):
        while self.microservices[microservice.name]["microservice"].lock is False:
            if self.microservices[microservice.name]["microservice"].check_queue():
                queueLen = 0
                server.send_message(client, json.dumps(
                    self.microservices[microservice.name]["microservice"].execute_queue()))
                self.microservices[microservice.name]["microservice"].queue[0].isSend = True
                while self.microservices[microservice.name]["microservice"].check_queue() and \
                        self.microservices[microservice.name]["microservice"].lock is False:
                    if queueLen != len(self.microservices[microservice.name]["microservice"].queue):
                        for i in range(len(self.microservices[microservice.name]["microservice"].queue)):
                            if self.microservices[microservice.name]["microservice"].check_queue_response(
                                    i) is False and self.microservices[microservice.name]["microservice"].queue[
                                i].isSend is False:
                                server.send_message(client, json.dumps(
                                    self.microservices[microservice.name]["microservice"].execute_queue(
                                        position=i)))
                                self.microservices[microservice.name]["microservice"].queue[i].isSend = True
                                logging.info("Added client")
                        queueLen = len(self.microservices[microservice.name]["microservice"].queue)
                    for i in range(len(self.microservices[microservice.name]["microservice"].queue)):
                        if self.microservices[microservice.name]["microservice"].queue[i].lock:
                            server.send_message(client, json.dumps({
                                "name": microservice,
                                "endpoint": self.microservices[microservice.name]["microservice"].queue[i].endpoint,
                                "type": "deletion",
                                "uuid": self.microservices[microservice.name]["microservice"].queue[i].uuid
                            }))
                            self.microservices[microservice.name]["microservice"].delete_queue_entry(position=i)

    def structureCheck(self, request):
        try:
            request = json.loads(request)
        except json.decoder.JSONDecodeError:
            return False
        if "uuid" in request and uuid4hex.match(request["uuid"]) and "name" in request and (
                request["name"] in self.microservices or request["name"] == "internal") and "endpoint" in request and (
                request["endpoint"] == "register" or request["endpoint"] in self.microservices[
            request["name"]]["microservice"].endpoints) and "data" in request and "type" in request and (
                request["type"] == "request" or request["type"] == "response" or type == "deletion"):
            return True
        else:
            return False
