import json

class LiteTuxMap:
    def __init__(self):
        self.width = 400
        self.height = 36
        self.mapChanged = False
        self._mapData = [[0 for i in range(400)] for j in range(36)]

    def toJSON(self):
        raw = {"width":self.width, "height":self.height, "_mapData":self._mapData}
        return json.dumps(raw, indent=2);

test = LiteTuxMap()
jtest = test.toJSON()
print(jtest)