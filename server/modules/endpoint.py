import re

uuid4hex = re.compile("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}", re.I)


class Microservice:
    def __init__(self, name, description, endpoints, clientID):
        self.lock = False
        self.clientID = clientID
        self.description = description
        self.name = name
        self.queue = []
        self.endpoints = {}
        for i in range(len(endpoints)):
            self.endpoints[endpoints[i]["name"]] = Endpoint(name=endpoints[i]["name"],
                                                            description=endpoints[i]["description"],
                                                            parameters=endpoints[i]["parameters"])

    def append_queue(self, request):
        self.queue.append(request)

    def check_queue(self):
        if self.queue:
            return True
        else:
            return False

    def execute_queue(self, position=0):
        self.queue[position].send = True
        return {
            "type": "request",
            "endpoint": self.queue[position].endpoint,
            "uuid": self.queue[position].uuid,
            "data": self.queue[position].data
        }

    def enter_queue_response(self, response, position=0):
        self.queue[position].response = response

    def check_queue_response(self, position):
        if self.queue[position].response == "":
            return False
        else:
            return True

    def show_queue_response(self, position):
        return self.queue[position].response

    def delete_queue_entry(self, position):
        self.queue.pop(position)

    def showQueuePosition(self, uuid):
        for i in range(len(self.queue)):
            if self.queue[i].uuid == uuid:
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

    def check(self, data):
        for parameter in self.parameters.items():
            if not ((parameter[1].name in data or parameter[1].optional) and self.validateType(parameter[1].type, data[
                parameter[1].name])):
                return False
        return True

    def validateType(self, type, var):
        if type == "string" and isinstance(var, str):
            return True
        elif type == "int" and isinstance(var, int):
            return True
        elif type == "float" and isinstance(var, float):
            return True
        elif type == "bool" and isinstance(var, bool):
            return True
        elif type == "dict" and isinstance(var, dict):
            return True
        else:
            return False


class Parameter:
    def __init__(self, name, description, optional, type):
        self.type = type
        self.optional = optional
        self.description = description
        self.name = name
