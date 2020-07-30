import websocket
import json
import uuid


def on_open(ws):
    request = json.dumps({
        "uuid": uuid.uuid4().hex,
        "name": "test",
        "endpoint": "hello",
        "type": "request",
        "data": {
            "user": "test"
        }
    })
    ws.send(request)


def on_message(ws, message):
    print(message)


ws = websocket.WebSocketApp("ws://localhost:8000", on_message=on_message)
ws.on_open = on_open
ws.run_forever()