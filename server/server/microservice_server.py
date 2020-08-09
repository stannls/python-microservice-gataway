import json
import logging
from client.microservice import Microservice
from client.client import Client
from microservices.internal import internal
from request_error.request_error import request_error
import time

clients = {}
Internal = internal()


def new_client(client, server):
    logging.info("New Client got connected")


def new_message(client, server, message):
    logging.info("Got new message")
    logging.debug("Handling request...")
    logging.debug("Request content: " + message)
    if Internal.structureCheck(message):
        logging.info("Request passed structure check")
        request_object = json.loads(message)
        if request_object["type"] == "response" and Internal.microservices[request_object["name"]][
            "microservice"].showQueuePosition(
            request_object["uuid"]) is not False:
            logging.info("The message is a response")
            logging.debug(message)
            Internal.microservices[request_object["name"]]["microservice"].enter_queue_response(
                response=request_object["data"]["response"],
                position=Internal.microservices[request_object["name"]]["microservice"].showQueuePosition(
                    uuid=request_object["uuid"]))
        elif request_object["type"] == "request":
            if request_object["name"] == "internal" and request_object[
                "endpoint"] == "register" and Internal.registerCheck(request_object):
                microservice = Microservice(name=request_object["data"]["name"],
                                            description=request_object["data"]["description"],
                                            endpoints=request_object["data"]["endpoints"],
                                            clientID=client["id"])
                Internal.register(microservice=microservice, is_internal=False)
                server.send_message(client, json.dumps({"code": 200, "connected": True}))
                logging.info("Registered new microservice " + request_object["data"]["name"])
                Internal.run(microservice, clients, server, client)
            elif request_object["name"] in Internal.microservices and \
                    Internal.microservices[request_object["name"]]["microservice"].endpoints[
                        request_object["endpoint"]].name == request_object[
                "endpoint"] and Internal.microservices[request_object["name"]]["microservice"].internal is False:
                logging.debug("New client got registered")
                if not client["id"] in client:
                    clients[client["id"]] = Client(id=client["id"])
                clients[client["id"]].newRequest(request_object["uuid"], request_object["name"],
                                                 request_object["endpoint"], request_object["data"], client, server,
                                                 request_object, Internal)
            else:
                request_error.bad_request(client, server, "No valid microservice were given")
        elif request_object["type"] == "deletion":
            clients[client["id"]].requests[request_object["uuid"]].lock = True
            time.sleep(1)
            del clients[client["id"]].requests[request_object["uuid"]]
        else:
            request_error.bad_request(client, server, "Request has no valid type")
    else:
        request_error.bad_request(client, server, "Request failed at structure check")


def on_disconnect(client, server):
    for i in Internal.microservices.items():
        if i[1]["microservice"].clientID == client["id"]:
            Internal.microservices[i[0]]["microservice"].lock = True
            time.sleep(1)
            del Internal.microservices[i[0]]
            break
    for i in clients.items():
        if i[0] == client["id"]:
            clients[i[0]].alive = False
            clients[i[0]].die()
            time.sleep(2)
            del clients[i[0]]
            break
