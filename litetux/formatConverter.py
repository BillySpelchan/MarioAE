import json
import LTMap

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
    ltm = LTMap.LiteTuxMap(len(raw_level[0]), len(raw_level))
    for r in range(len(raw_level)):
        s = raw_level[r]
        for c in range(len(s)):
            tid = MARIO_LT_MAPPING.get(s[c])
            if tid is None:
                tid = 16
            ltm.setTile(c,r, tid)
        print(s)
    print(ltm.toVerticalString())

convertVGLCMario("../levels/mario-1-1.txt")