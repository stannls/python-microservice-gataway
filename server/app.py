import asyncio
import logging
import websockets
from modules.server import server
import yaml

configFile = open('config.yml')
config = yaml.load(configFile, Loader=yaml.FullLoader)
logging.basicConfig(level=config["loglevel"])

start_server = websockets.serve(server, "0.0.0.0", 8000)
logging.info('Starting server...')
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
