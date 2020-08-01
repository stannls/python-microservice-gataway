import time
import logging
import threading


class Client:
    def __init__(self, id):
        self.id = id
        self.alive = True
        self.requests = {}

    def newRequest(self, uuid, microservice, endpoint, data, client, server, request, microservice_object):
        self.requests[uuid] = Request(uuid, microservice, endpoint, data)
        thread = threading.Thread(target=self._run_new_Request, args=(client, server, request, microservice_object))
        thread.start()

    def die(self):
        for i in self.requests.items():
            i[1].lock = True

    def _run_new_Request(self, client, server, request, microservice):
        microservice.microservices[request["name"]]["microservice"].append_queue(self.requests[request["uuid"]])
        while not microservice.microservices[request["name"]]["microservice"].check_queue_response(
                microservice.microservices[request["name"]]["microservice"].showQueuePosition(
                    request["uuid"])) and \
                self.alive:
            time.sleep(0.5)
        logging.debug("Sending client response")
        resp = microservice.microservices[request["name"]]["microservice"].show_queue_response(
            position=microservice.microservices[request["name"]]["microservice"].showQueuePosition(
                request["uuid"]))
        server.send_message(client, resp)
        while microservice.microservices[request["name"]]["microservice"].lock is False and self.alive:
            if microservice.microservices[request["name"]]["microservice"].show_queue_response(
                    position=microservice.microservices[request["name"]]["microservice"].showQueuePosition(
                        request["uuid"])) != resp:
                resp = microservice.microservices[request["name"]]["microservice"].show_queue_response(
                    position=microservice.microservices[request["name"]]["microservice"].showQueuePosition(
                        request["uuid"]))
                try:
                    server.send_message(client, resp)
                except BrokenPipeError:
                    # TODO Reimplement killing
                    self.alive = False
                    self.die()
                    print("DISCONNECT")
                    time.sleep(2)
                    del self
                    break
            time.sleep(0.5)


class Request:
    def __init__(self, uuid, microservice, endpoint, data):
        self.data = data
        self.endpoint = endpoint
        self.microservice = microservice
        self.uuid = uuid
        self.lock = False
        self.response = ""
