import asyncio
import json
import logging
from modules.endpoint import Microservice, structureCheck
import time
import _thread as thread

microservices = {}


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
                                                                                 "endpoints"])
                server.send_message(client, json.dumps({"code": 200, "connected": True}))
                logging.info("Registered new microservice " + request_object["data"]["name"])

                def run():
                    while True:
                        if microservices[request_object["data"]["name"]].check_queue():
                            queueLen = 0
                            server.send_message(client, json.dumps(
                                microservices[request_object["data"]["name"]].execute_queue()))
                            while microservices[request_object["data"]["name"]].check_queue():
                                if queueLen != len(microservices[request_object["data"]["name"]].queue):
                                    for i in range(len(microservices[request_object["data"]["name"]].queue)):
                                        if not microservices[request_object["data"]["name"]].queue[i]["send"]:
                                            server.send_message(client, json.dumps(
                                                microservices[request_object["data"]["name"]].execute_queue(
                                                    position=i)))
                                            logging.info("Added client")
                                    queueLen = len(microservices[request_object["data"]["name"]].queue)

                                time.sleep(0.5)
                        time.sleep(0.5)

                thread.start_new_thread(run, ())
            elif request_object["name"] == microservices[request_object["name"]].name and \
                    microservices[request_object["name"]].endpoints[request_object["endpoint"]].name == request_object[
                "endpoint"]:
                logging.debug("New client got registered")
                if microservices[request_object["name"]].endpoints[request_object["endpoint"]].check(
                        request_object["data"]):
                    queueID = microservices[request_object["name"]].append_queue(endpoint=request_object["endpoint"],
                                                                                 parameters=request_object["data"],
                                                                                 queueID=request_object["uuid"])
                    while not microservices[request_object["name"]].check_queue_response(
                            position=microservices[request_object["name"]].showQueuePosition(queueID)):
                        time.sleep(0.5)
                    logging.debug("Sending client response")
                    resp = microservices[request_object["name"]].show_queue_response(
                        position=microservices[request_object["name"]].showQueuePosition(queueID))
                    server.send_message(client, resp)
                    while True:
                        if microservices[request_object["name"]].show_queue_response(
                                position=microservices[request_object["name"]].showQueuePosition(queueID)) != resp:
                            resp = microservices[request_object["name"]].show_queue_response(
                                position=microservices[request_object["name"]].showQueuePosition(queueID))
                            server.send_message(client, resp)
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
