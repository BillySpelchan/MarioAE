
LITE_TUX_SPRITE_IDS = {
    "EMPTY" : 0,# spawn placenolder
    "CEIL_SPIKE" : 1,
    "CLOUD" : 2,# spawn placenolder
    "HOVER_ENEMY" : 3,
    "COIN" : 4,
    "ENEMY": 5,
    "BIG_COIN" : 6,
    "SHELL_ENEMY" : 7,
    "GROUND" : 8,
    "GROUND_SPIKE" : 9,
    "BREAKABLE_BRICK" : 10,
    "SLIPPERY_GROUND" : 11,
    "COINBOX" : 12,
    "COLLAPSING_WALL" : 13,
    "POWERUP" : 14,
    "CANNON" : 15,

    "ALWAYS_ACTIVE_START" : 16,
    "CANNON_BALL" : 16
}

class LiteTuxMap:
    def __init__(self, w=400, h=36):
        self.width = w
        self.height = h
        self.mapChanged = False
        self._mapData = [[0 for i in range(w)] for j in range(h)]
        self.tile_str = "-v.O$e!bX^S=?BPC:"


    def getTile(self, x, y) :
        tx = max(0, min(x, self.width))
        ty = max(0, min(y, self.height))
        return self._mapData[ty][tx]


    def setTile(self, x, y, value):
        tx = max(0, min(x, self.width))
        ty = max(0, min(y, self.height))
        self._mapData[ty][tx] = value

    def toVerticalString(self, start=0, end=-1):
        last = end if end > 0 else self.width
        print (last)
        s = ""
        for col in range(start, last):
            rs = ""
            for row in range(self.height):
                tid = self.getTile(col, row)
                if (tid < 0) or (tid > 15): tid = 16
                rs += self.tile_str[tid]
            s = s + rs[::-1] + "\n"
        return s


    def toJSONString(self):
        jstr = "{\n \"width\": " + str(self.width) + ",\n"
        jstr += " \"height\": " + str(self.height) +  ",\n"
        jstr += " \"_mapData\": [\n"
        for row in range(self.height):
            jstr += "  ["
            for col in range(self.width-1):
                jstr += str(self.getTile(col, row))
                jstr += ", "
            jstr += str(self.getTile(self.width-1, row))
            if row < (self.height-1):
                jstr += "],\n"
            else:
                jstr += "]\n ]\n"
        jstr += "}\n"
        return jstr

