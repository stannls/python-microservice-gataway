import re
import json

uuid4hex = re.compile("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}", re.I)


def structureCheck(request, microservices):
    try:
        request = json.loads(request)
    except json.decoder.JSONDecodeError:
        return False
    if "uuid" in request and uuid4hex.match(request["uuid"]) and "name" in request and (request["name"] in microservices or request["name"] == "internal") and "endpoint" in request and (request["endpoint"] == "register" or request["endpoint"] in microservices[request["name"]].endpoints) and "data" in request:
        return True
    else:
        return False


class Microservice:
    def __init__(self, name, description, endpoints):
        self.description = description
        self.name = name
        self.queue = []
        self.endpoints = {}
        for i in range(len(endpoints)):
            self.endpoints[endpoints[i]["name"]] = Endpoint(name=endpoints[i]["name"],
                                                            description=endpoints[i]["description"],
                                                            parameters=endpoints[i]["parameters"])

    def append_queue(self, endpoint, parameters, queueID):
        self.queue.append({
            "send": False,
            "uuid": queueID,
            "request": {
                "endpoint": endpoint,
                "parameters": parameters
            }
        })
        return queueID

    def check_queue(self):
        if self.queue:
            return True
        else:
            return False

    def execute_queue(self, position=0):
        self.queue[position]["send"] = True
        return {
            "endpoint": self.queue[position]["request"]["endpoint"],
            "uuid": self.queue[position]["uuid"],
            "data": self.queue[position]["request"]["parameters"]
        }

    def enter_queue_response(self, response, position=0):
        self.queue[position]["response"] = response

    def check_queue_response(self, position):
        try:
            self.queue[position]["response"]
        except KeyError:
            return False
        return True

    def show_queue_response(self, position):
        return self.queue[position]["response"]

    def delete_queue_entry(self, position):
        self.queue.pop(position)

    def showQueuePosition(self, uuid):
        for i in range(len(self.queue)):
            if self.queue[i]["uuid"] == uuid:
                return i


class Endpoint:
    def __init__(self, name, description, parameters):
        self.description = description
        self.name = name
        self.parameters = {}
        for i in range(len(parameters)):
            self.parameters[parameters[i]["name"]] = Parameter(name=parameters[i]["name"],
                                                               description=parameters[i]["description"],
                                                               optional=parameters[i]["optional"],
                                                               type=parameters[i]["type"])


class Parameter:
    def __init__(self, name, description, optional, type):
        self.type = type
        self.optional = optional
        self.description = description
        self.name = name
