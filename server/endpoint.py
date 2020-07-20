class microservice:
    def __init__(self, name, description, endpoints):
        self.description = description
        self.name = name
        self.queue = []
        self.endpoints = {}
        for i in range(len(endpoints)):
            self.endpoints[endpoints[i]["name"]] = endpoint(name=endpoints[i]["name"],
                                                            description=endpoints[i]["description"],
                                                            parameters=endpoints[i]["parameters"])

    def appendQueue(self, endpoint, parameters):
        self.queue.append({
            "request": {
                "endpoint": endpoint,
                "parameters": parameters
            }
        })

    def checkQueue(self):
        if self.queue:
            return True
        else:
            return False

    def executeQueue(self, position=0):
        return {
            "endpoint": self.queue[position]["request"]["endpoint"],
            "data": self.queue[position]["request"]["parameters"]
        }

    def enterQueueResponse(self, response, position=0):
        self.queue[position]["response"] = response

    def checkQueueResponse(self, position=0):
        try:
            self.queue[position]["response"]
        except KeyError:
            return False
        return True

    def showQueueResponse(self, position=0):
        return self.queue[position]["response"]

    def deleteQueueEntry(self, position=0):
        self.queue.pop(position)


class endpoint:
    def __init__(self, name, description, parameters):
        self.description = description
        self.name = name
        self.parameters = {}
        for i in range(len(parameters)):
            self.parameters[parameters[i]["name"]] = parameter(name=parameters[i]["name"],
                                                               description=parameters[i]["description"],
                                                               optional=parameters[i]["optional"],
                                                               type=parameters[i]["type"])


class parameter:
    def __init__(self, name, description, optional, type):
        self.type = type
        self.optional = optional
        self.description = description
        self.name = name
