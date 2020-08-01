import asyncio
import json
import logging
from modules.endpoint import Microservice, structureCheck
from server.modules.client import Client
import time
import _thread as thread

microservices = {}
clients = {}



def new_client(client, server):
    logging.info("New Client got connected")


def new_message(client, server, message):
    logging.info("Got new message")
    logging.debug("Handling request...")
    logging.debug("Request content: " + message)
    if structureCheck(message, microservices):
        logging.info("Request passed structure check")
        request_object = json.loads(message)
        if request_object["type"] == "response" and microservices[request_object["name"]].showQueuePosition(
                request_object["uuid"]) is not False:
            logging.info(message)
            microservices[request_object["name"]].enter_queue_response(
                response=request_object["data"]["response"],
                position=microservices[request_object["name"]].showQueuePosition(
                    uuid=request_object["uuid"]))
        elif request_object["type"] == "request":
            if request_object["endpoint"] == "register":
                microservices[request_object["data"]["name"]] = Microservice(name=request_object["data"]["name"],
                                                                             description=request_object["data"][
                                                                                 "description"],
                                                                             endpoints=request_object["data"][
                                                                                 "endpoints"],
                                                                             clientID=client["id"]
                server.send_message(client, json.dumps({"code": 200, "connected": True}))
                logging.info("Registered new microservice " + request_object["data"]["name"])
                def run():
                    while microservices[request_object["data"]["name"]].lock is False:
                        if microservices[request_object["data"]["name"]].check_queue():
                            queueLen = 0
                            server.send_message(client, json.dumps(
                                microservices[request_object["data"]["name"]].execute_queue()))
                            while microservices[request_object["data"]["name"]].check_queue() and microservices[
                                request_object["data"]["name"]].lock is False:
                                if queueLen != len(microservices[request_object["data"]["name"]].queue):
                                    for i in range(len(microservices[request_object["data"]["name"]].queue)):
                                        if microservices[request_object["data"]["name"]].check_queue_response(
                                                i) is False:
                                            server.send_message(client, json.dumps(
                                                microservices[request_object["data"]["name"]].execute_queue(
                                                    position=i)))
                                            logging.info("Added client")
                                    queueLen = len(microservices[request_object["data"]["name"]].queue)
                                for i in range(len(microservices[request_object["data"]["name"]].queue)):
                                    if microservices[request_object["data"]["name"]].queue[i].lock:
                                        server.send_message(client, json.dumps({
                                            "name": request_object["data"]["name"],
                                            "endpoint": microservices[request_object["data"]["name"]].queue[i].endpoint,
                                            "type": "deletion",
                                            "uuid": microservices[request_object["data"]["name"]].queue[i].uuid
                                        }))
                                        microservices[request_object["data"]["name"]].delete_queue_entry(position=i)
                                time.sleep(0.5)
                                for i in client_Connections.items():
                                    if i[1]["connected"] is False:
                                        logging.info("Sending deletion")
                                        server.send_message(client, json.dumps({
                                            "code": 200,
                                            "name": request_object["data"]["name"],
                                            "endpoint": microservices[request_object["data"]["name"]].queue[microservices[request_object["data"]["name"]].showQueuePosition(i[1]["uuid"])]["request"]["endpoint"],
                                            "type": "deletion",
                                            "uuid": i[1]["uuid"]
                                        }))
                                        del microservices[request_object["data"]["name"]].queue[microservices[request_object["data"]["name"]].showQueuePosition(i[1]["uuid"])]
                        time.sleep(0.5)

                thread.start_new_thread(run, ())
            elif request_object["name"] == microservices[request_object["name"]].name and \
                    microservices[request_object["name"]].endpoints[request_object["endpoint"]].name == request_object[
                "endpoint"]:
                logging.debug("New client got registered")
                if microservices[request_object["name"]].endpoints[request_object["endpoint"]].check(
                        request_object["data"]):
                    if not client["id"] in client:
                        clients[client["id"]] = Client(id=client["id"])
                    clients[client["id"]].newRequest(request_object["uuid"], request_object["name"],
                                                     request_object["endpoint"], request_object["data"])
                    microservices[request_object["name"]].append_queue(
                        clients[client["id"]].requests[request_object["uuid"]])
                    while not microservices[request_object["name"]].check_queue_response(
                            microservices[request_object["name"]].showQueuePosition(request_object["uuid"])) and clients[client["id"]].alive:
                        time.sleep(0.5)
                    logging.debug("Sending client response")
                    resp = microservices[request_object["name"]].show_queue_response(
                        position=microservices[request_object["name"]].showQueuePosition(request_object["uuid"]))
                    server.send_message(client, resp)
                    while microservices[request_object["name"]].lock is False and clients[client["id"]].alive:
                        if microservices[request_object["name"]].show_queue_response(
                                position=microservices[request_object["name"]].showQueuePosition(
                                    request_object["uuid"])) != resp:
                            resp = microservices[request_object["name"]].show_queue_response(
                                position=microservices[request_object["name"]].showQueuePosition(
                                    request_object["uuid"]))
                            try:
                                server.send_message(client, resp)
                            except BrokenPipeError:
                                clients[client["id"]].alive = False
                                clients[client["id"]].die()
                                print("DISCONNECT")
                                time.sleep(2)
                                del clients[client["id"]]
                                break
                        time.sleep(0.5)
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
    for i in microservices.items():
        if i[1].clientID == client["id"]:
            microservices[i[0]].lock = True
            time.sleep(1)
            del microservices[i[0]]
            break
    for i in clients.items():
        if i[1].id == client["id"]:
            clients[i[0]].alive = False
