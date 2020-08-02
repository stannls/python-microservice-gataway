import json
import logging


class request_error:
    @staticmethod
    def bad_request(client, server, error_msg):
        server.send_message(client, json.dumps({"code": 400, "message": error_msg}))
        logging.info(error_msg)
