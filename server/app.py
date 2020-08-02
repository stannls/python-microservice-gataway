import logging
from server.modules.server import new_client, new_message, on_disconnect
import yaml
from websocket_server import WebsocketServer

configFile = open('config.yml')
config = yaml.load(configFile, Loader=yaml.FullLoader)
logging.basicConfig(level=config["loglevel"])

server = WebsocketServer(config["server"]["port"], host=config["server"]["host"])
server.set_fn_new_client(new_client)
server.set_fn_message_received(new_message)
server.set_fn_client_left(on_disconnect)
server.run_forever()
