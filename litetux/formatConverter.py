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

def batchConvert(list):
    sm = LTMap.LTSpeedrunStateManager(4, True)
    for filename in list:
        newname = filename[3:]
        newname = newname.replace(".txt", ".json")
        print("Processing ", filename)
        ltm = convertVGLCMario(filename)
        print(ltm.to_vertical_string())
        board = LTMap.LTPathBoard(ltm, sm)
        board.process_all_paths(0, 8)
        if len(board.get_nodes_in_column(ltm.width-1)) > 0:
            print("Saving map ", newname)
            ltm.save(newname)

"""
ltm = convertVGLCMario("../levels/mario-1-1.txt")
print(ltm.to_vertical_string())
ltm.save("levels/mario1-1.json")
LTMap.LTSpeedrunStateManager
"""
batchConvert(["../levels/mario-1-1.txt", "../levels/mario-1-2.txt", "../levels/mario-1-3.txt",
              "../levels/mario-2-1.txt","../levels/mario-3-1.txt","../levels/mario-3-3.txt",
              "../levels/mario-4-1.txt","../levels/mario-4-2.txt","../levels/mario-5-1.txt",
              "../levels/mario-5-3.txt","../levels/mario-6-1.txt","../levels/mario-6-2.txt",
              "../levels/mario-6-3.txt","../levels/mario-7-1.txt","../levels/mario-8-1.txt",])