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

    def append_queue(self, endpoint, parameters):
        self.queue.append({
            "request": {
                "endpoint": endpoint,
                "parameters": parameters
            }
        })

    def check_queue(self):
        if self.queue:
            return True
        else:
            return False

    def execute_queue(self, position=0):
        return {
            "endpoint": self.queue[position]["request"]["endpoint"],
            "data": self.queue[position]["request"]["parameters"]
        }

    def enter_queue_response(self, response, position=0):
        self.queue[position]["response"] = response

    def check_queue_response(self, position=0):
        try:
            self.queue[position]["response"]
        except KeyError:
            return False
        return True

    def show_queue_response(self, position=0):
        return self.queue[position]["response"]

    def delete_queue_entry(self, position=0):
        self.queue.pop(position)


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
