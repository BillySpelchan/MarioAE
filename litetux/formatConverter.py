import json
from litetux import LTMap

MARIO_LT_MAPPING = {
    "-": 0,
    "o": 4,
    "E": 5,
    "S": 10,
    "?": 12,
    "Q": 8,
    "<": 8,
    ">": 8,
    "[": 8,
    "]": 8,
    "X": 8
}

def convertVGLCMario(level_name):
    f = open(level_name, "r")
    raw_level = f.readlines()
    f.close()
    ltm = LTMap.LiteTuxMap(len(raw_level[0])-1, len(raw_level))
    for r in range(len(raw_level)):
        s = raw_level[r]
        for c in range(len(s)-1):
            tid = MARIO_LT_MAPPING.get(s[c])
            if tid is None:
                tid = 16
            ltm.set_tile(c,r, tid)
        #print(s)
    return ltm


ltm = convertVGLCMario("../levels/mario-1-1.txt")
print(ltm.to_vertical_string())
ltm.save("levels/mario1-1.json")
