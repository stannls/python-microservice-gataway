from .internal_template import internal_Template
import json


class test(internal_Template):
    def __init__(self):
        endpointFuncs = {"testFunc": {"function": self.testFunc, "args": ()}}
        endpoints = []
        endpoints.append({"name": "testFunc", "description": "a test", "parameters": []})
        super().__init__(name="test", description="test-service", endpoints=endpoints, endpointFuncs=endpointFuncs)

    def testFunc(self, data):
        print(data)
        data = json.loads(data)
        position = self.showQueuePosition(data["uuid"])
        response = json.dumps({
                        "code": 200,
                        "name": self.name,
                        "endpoint": "testFunc",
                        "type": "response",
                        "uuid": data["uuid"],
                        "data": {
                            "response": "test"
                        }
                    })
        self.execute_queue(position)
        self.enter_queue_response(response, position)
        print("Queue:", self.queue)