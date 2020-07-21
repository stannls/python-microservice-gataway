import websockets
import asyncio
import json
import logging
from modules.endpoint import microservice

microservices = {}
logging.basicConfig(level=logging.INFO)


async def hello(websocket, path):
    request = await websocket.recv()
    logging.debug("Handling request...")
    logging.debug("Request content: " + request)
    requestObject = json.loads(request)
    if requestObject["endpoint"] == "register":
        microservices[requestObject["data"]["name"]] = microservice(name=requestObject["data"]["name"],
                                                                    description=requestObject["data"]["description"],
                                                                    endpoints=requestObject["data"]["endpoints"])
        await websocket.send(json.dumps({"code": 200}))
        logging.info("Registered new microservice " + requestObject["data"]["name"])
        while True:
            if microservices[requestObject["data"]["name"]].checkQueue():
                await websocket.send(json.dumps(microservices[requestObject["data"]["name"]].executeQueue()))
                response = json.loads(await websocket.recv())
                print(response["data"]["greeting"])
                microservices[requestObject["data"]["name"]].enterQueueResponse(response["data"]["greeting"])
            else:
                pass
            await asyncio.sleep(0.5)
    elif requestObject["name"] == microservices[requestObject["name"]].name and \
            microservices[requestObject["name"]].endpoints[requestObject["endpoint"]].name == requestObject["endpoint"]:
        logging.debug("New client got registered")
        microservices[requestObject["name"]].appendQueue(endpoint=requestObject["endpoint"],
                                                         parameters=requestObject["data"])
        while not microservices[requestObject["name"]].checkQueueResponse():
            await asyncio.sleep(0.5)
        logging.debug("Sending client response")
        await websocket.send(microservices[requestObject["name"]].showQueueResponse())
        microservices[requestObject["name"]].deleteQueueEntry()
    else:
        await websocket.send(json.dumps({"code": 400}))
        logging.debug("Got bad request")


start_server = websockets.serve(hello, "0.0.0.0", 8000)
logging.info('Starting server...')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
