import asyncio
import websockets
import json

async def hello():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        request = json.dumps({
            "name": "test",
            "endpoint": "hello",
            "data": {
                "user": "imatest"
            }
        })

        await websocket.send(request)
        print(request)

        while True:
            greeting = await websocket.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
asyncio.get_event_loop().run_forever()