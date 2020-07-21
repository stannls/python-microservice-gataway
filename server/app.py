import websockets
import asyncio
import json
from endpoint import microservice

microservices = {}


async def hello(websocket, path):
    request = await websocket.recv()
    print(request)
    requestObject = json.loads(request)
    if requestObject["endpoint"] == "register":
        microservices[requestObject["data"]["name"]] = microservice(name=requestObject["data"]["name"],
                                                                    description=requestObject["data"]["description"],
                                                                    endpoints=requestObject["data"]["endpoints"])
        print(microservices)
        await websocket.send(json.dumps({"code": 200}))
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
        microservices[requestObject["name"]].appendQueue(endpoint=requestObject["endpoint"],
                                                         parameters=requestObject["data"])
        while not microservices[requestObject["name"]].checkQueueResponse():
            await asyncio.sleep(0.5)
        await websocket.send(microservices[requestObject["name"]].showQueueResponse())
        microservices[requestObject["name"]].deleteQueueEntry()
    else:
        await websocket.send(json.dumps({"code": 400}))


start_server = websockets.serve(hello, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
