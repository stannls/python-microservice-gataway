import time
import json
import logging
import threading
import re

uuid4hex = re.compile("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}", re.I)


class internal:
    def __init__(self):
        self.microservices = {}

    def register(self, microservice, internal=False):
        self.microservices[microservice.name] = {"internal": internal, "microservice": microservice}

    def run(self, server, client, microservice, clients):
        thread = threading.Thread(target=self._runloop, args=(client, server, microservice, clients))
        thread.start()

    def _runloop(self, client, server, microservice, clients):
        while self.microservices[microservice]["microservice"].lock is False:
            if self.microservices[microservice]["microservice"].check_queue():
                queueLen = 0
                print(server, client)
                server.send_message(client, json.dumps(
                    self.microservices[microservice]["microservice"].execute_queue()))
                while self.microservices[microservice]["microservice"].check_queue() and self.microservices[microservice]["microservice"].lock is False:
                    if queueLen != len(self.microservices[microservice]["microservice"].queue):
                        for i in range(len(self.microservices[microservice]["microservice"].queue)):
                            if self.microservices[microservice]["microservice"].check_queue_response(
                                    i) is False:
                                server.send_message(client, json.dumps(
                                    self.microservices[microservice]["microservice"].execute_queue(
                                        position=i)))
                                logging.info("Added client")
                        queueLen = len(self.microservices[microservice]["microservice"].queue)
                    for i in range(len(self.microservices[microservice]["microservice"].queue)):
                        if self.microservices[microservice]["microservice"].queue[i].lock:
                            server.send_message(client, json.dumps({
                                "name": microservice,
                                "endpoint": self.microservices[microservice]["microservice"].queue[i].endpoint,
                                "type": "deletion",
                                "uuid": self.microservices[microservice]["microservice"].queue[i].uuid
                            }))
                            self.microservices[microservice]["microservice"].delete_queue_entry(position=i)
                    time.sleep(0.5)

    def structureCheck(self, request):
        try:
            request = json.loads(request)
        except json.decoder.JSONDecodeError:
            return False
        if "uuid" in request and uuid4hex.match(request["uuid"]) and "name" in request and (
                request["name"] in self.microservices or request["name"] == "internal") and "endpoint" in request and (
                request["endpoint"] == "register" or request["endpoint"] in self.microservices[
            request["name"]]["microservice"].endpoints) and "data" in request and "type" in request and (
                request["type"] == "request" or request["type"] == "response"):
            return True
        else:
            return False
