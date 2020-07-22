import asyncio
import websockets
import json
import datetime


async def hello():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        request = json.dumps({
            "endpoint": "register",
            "data": {
                "name": "test",
                "description": "A test microservice",
                "endpoints": [
                    {
                        "name": "hello",
                        "description": "says hello",
                        "parameters": [
                            {
                                "name": "user",
                                "description": "The user to say hello",
                                "optional": False,
                                "type": "string"
                            }
                        ]
                    }
                ]
            }})

        await websocket.send(request)
        print(request)

        greeting = await websocket.recv()
        print(f"< {greeting}")

        while True:
            request = json.loads(await websocket.recv())
            print(request)
            if request["endpoint"] == "hello":
                while True:
                    response = json.dumps({
                        "code": 200,
                        "uuid": request["uuid"],
                        "data": {
                            "greeting": "Hello " + request["data"]["user"] + "!" + str(datetime.datetime.now())
                        }
                    })
                    print(response)
                    await websocket.send(response)
                    await asyncio.sleep(1)


asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()
