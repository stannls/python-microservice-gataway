import asyncio
import json
import logging
from server.modules.endpoint import Microservice
from server.modules.client import Client
from server.modules.microservices.internal import internal
import time
import _thread as thread

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
        if request_object["type"] == "response" and Internal.microservices[request_object["name"]]["microservice"].showQueuePosition(
                request_object["uuid"]) is not False:
            logging.info(message)
            Internal.microservices[request_object["name"]]["microservice"].enter_queue_response(
                response=request_object["data"]["response"],
                position=Internal.microservices[request_object["name"]]["microservice"].showQueuePosition(
                    uuid=request_object["uuid"]))
        elif request_object["type"] == "request":
            if request_object["name"] == "internal" and request_object["endpoint"] == "register":
                microservice = Microservice(name=request_object["data"]["name"],
                                            description=request_object["data"]["description"],
                                            endpoints=request_object["data"]["endpoints"],
                                            clientID=client["id"])
                Internal.register(microservice=microservice, internal=False)
                server.send_message(client, json.dumps({"code": 200, "connected": True}))
                logging.info("Registered new microservice " + request_object["data"]["name"])
                Internal.run(server, client, request_object["data"]["name"], clients)
            elif request_object["name"] in Internal.microservices and \
                    Internal.microservices[request_object["name"]]["microservice"].endpoints[request_object["endpoint"]].name == request_object[
                "endpoint"]:
                logging.debug("New client got registered")
                if Internal.microservices[request_object["name"]]["microservice"].endpoints[request_object["endpoint"]].check(
                        request_object["data"]):
                    if not client["id"] in client:
                        clients[client["id"]] = Client(id=client["id"])
                    clients[client["id"]].newRequest(request_object["uuid"], request_object["name"],
                                                     request_object["endpoint"], request_object["data"], client, server, request_object, Internal)
                else:
                    server.send_message(client, json.dumps({"code": 400}))
                    logging.debug("Got bad request")
            else:
                server.send_message(client, json.dumps({"code": 400}))
                logging.debug("Got bad request")
        else:
            server.send_message(client, json.dumps({"code": 400}))
            logging.debug("Got bad request")
    else:
        logging.info("Request failed at structure check")
        server.send_message(client, json.dumps({"code": 400}))
        logging.debug("Got bad request")


def on_disconnect(client, server):
    for i in Internal.microservices.items():
        if i[1]["microservice"].clientID == client["id"]:
            Internal.microservices[i[0]]["microservice"].lock = True
            time.sleep(1)
            del Internal.microservices[i[0]]
            break
    for i in clients.items():
        print(i[0])
        print(client["id"])
        if i[0] == client["id"]:
            print("Passed client disconnect check")
            clients[i[0]].alive = False
            clients[i[0]].die()
            time.sleep(2)
            del clients[i[0]]
            break
