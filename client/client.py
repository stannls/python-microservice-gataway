import asyncio
import websockets
import json
import uuid


async def hello():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        request = json.dumps({
            "uuid": uuid.uuid4().hex,
            "name": "test",
            "endpoint": "hello",
            "data": {
                "user": "test"
            }
        })

        await websocket.send(request)
        print(request)

        while True:
            greeting = await websocket.recv()
            print(f"< {greeting}")


asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()
