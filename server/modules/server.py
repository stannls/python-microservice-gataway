import asyncio
import json
import logging
from modules.endpoint import Microservice

microservices = {}


async def server(websocket, path):
    request = await websocket.recv()
    logging.debug("Handling request...")
    logging.debug("Request content: " + request)
    request_object = json.loads(request)
    if request_object["endpoint"] == "register":
        microservices[request_object["data"]["name"]] = Microservice(name=request_object["data"]["name"],
                                                                     description=request_object["data"]["description"],
                                                                     endpoints=request_object["data"]["endpoints"])
        await websocket.send(json.dumps({"code": 200, "connected": True}))
        logging.info("Registered new microservice " + request_object["data"]["name"])
        while True:
            if microservices[request_object["data"]["name"]].check_queue():
                queueLen = 0
                await websocket.send(json.dumps(microservices[request_object["data"]["name"]].execute_queue()))
                while microservices[request_object["data"]["name"]].check_queue():
                    if queueLen != len(microservices[request_object["data"]["name"]].queue):
                        for i in range(len(microservices[request_object["data"]["name"]].queue)):
                            if not microservices[request_object["data"]["name"]].queue[i]["send"]:
                                await websocket.send(json.dumps(microservices[request_object["data"]["name"]].execute_queue(position=i)))
                                logging.info("Added client")
                        queueLen = len(microservices[request_object["data"]["name"]].queue)
                    response = json.loads(await websocket.recv())
                    logging.info(response)
                    microservices[request_object["data"]["name"]].enter_queue_response(response=response["data"]["greeting"], position=microservices[request_object["data"]["name"]].showQueuePosition(uuid=response["uuid"]))
                    await asyncio.sleep(0.5)
            await asyncio.sleep(0.5)
    elif request_object["name"] == microservices[request_object["name"]].name and \
            microservices[request_object["name"]].endpoints[request_object["endpoint"]].name == request_object[
        "endpoint"]:
        logging.debug("New client got registered")
        queueID = microservices[request_object["name"]].append_queue(endpoint=request_object["endpoint"],
                                                           parameters=request_object["data"], queueID=request_object["uuid"])
        while not microservices[request_object["name"]].check_queue_response(position=microservices[request_object["name"]].showQueuePosition(queueID)):
            await asyncio.sleep(0.5)
        logging.debug("Sending client response")
        resp = microservices[request_object["name"]].show_queue_response(position=microservices[request_object["name"]].showQueuePosition(queueID))
        await websocket.send(resp)
        while True:
            if microservices[request_object["name"]].show_queue_response(position=microservices[request_object["name"]].showQueuePosition(queueID)) != resp:
                resp = microservices[request_object["name"]].show_queue_response(position=microservices[request_object["name"]].showQueuePosition(queueID))
                await websocket.send(resp)
            await asyncio.sleep(0.5)
        # microservices[request_object["name"]].delete_queue_entry(position=microservices[request_object[
        # "name"]].showQueuePosition(queueID))
    else:
        await websocket.send(json.dumps({"code": 400}))
        logging.debug("Got bad request")
