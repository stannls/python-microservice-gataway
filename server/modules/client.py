class Client:
    def __init__(self, id):
        self.id = id
        self.alive = True
        self.requests = {}

    def newRequest(self, uuid, microservice, endpoint, data):
        self.requests[uuid] = Request(uuid, microservice, endpoint, data)

    def die(self):
        for i in self.requests.items():
            i[1].lock = True


class Request:
    def __init__(self, uuid, microservice, endpoint, data):
        self.data = data
        self.endpoint = endpoint
        self.microservice = microservice
        self.uuid = uuid
        self.lock = False
        self.response = ""
