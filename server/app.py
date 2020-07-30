import asyncio
import logging
import websockets
from modules.server import new_client, new_message
import yaml
from websocket_server import WebsocketServer

configFile = open('config.yml')
config = yaml.load(configFile, Loader=yaml.FullLoader)
logging.basicConfig(level=config["loglevel"])


# start_server = websockets.serve(server, "0.0.0.0", 8000)
# logging.info('Starting server...')
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()




server = WebsocketServer(8000, host='0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_message_received(new_message)
server.run_forever()
