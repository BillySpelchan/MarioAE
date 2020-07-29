import json
import numpy as np

LITE_TUX_SPRITE_IDS = {
    "EMPTY": 0,  # spawn placenolder
    "CEIL_SPIKE": 1,
    "CLOUD": 2,  # spawn placenolder
    "HOVER_ENEMY": 3,
    "COIN": 4,
    "ENEMY": 5,
    "BIG_COIN": 6,
    "SHELL_ENEMY": 7,
    "GROUND": 8,
    "GROUND_SPIKE": 9,
    "BREAKABLE_BRICK": 10,
    "SLIPPERY_GROUND": 11,
    "COINBOX": 12,
    "COLLAPSING_WALL": 13,
    "POWERUP": 14,
    "CANNON": 15,

    "ALWAYS_ACTIVE_START": 16,
    "CANNON_BALL": 16
}


class LiteTuxMap:
    def __init__(self, w=400, h=36):
        self.width = w
        self.height = h
        self.mapChanged = False
        self._mapData = [[0 for _ in range(w)] for _ in range(h)]
        self.tile_str = "-v.O$e!bX^S=?BPC:"

    def get_tile(self, x, y):
        tx = max(0, min(x, self.width-1))
        ty = max(0, min(y, self.height-1))
        return self._mapData[ty][tx]

    def set_tile(self, x, y, value):
        tx = max(0, min(x, self.width))
        ty = max(0, min(y, self.height))
        self._mapData[ty][tx] = value

    def to_vertical_string(self, start=0, end=-1):
        last = end if end > 0 else self.width
        s = ""
        for col in range(start, last):
            rs = ""
            for row in range(self.height):
                tid = self.get_tile(col, row)
                if (tid < 0) or (tid > 15):
                    tid = 16
                rs += self.tile_str[tid]
            s = s + rs[::-1] + "\n"
        return s

    def to_json_string(self):
        jstr = "{\n \"width\": " + str(self.width) + ",\n"
        jstr += " \"height\": " + str(self.height) + ",\n"
        jstr += " \"_mapData\": [\n"
        for row in range(self.height):
            jstr += "  ["
            for col in range(self.width - 1):
                jstr += str(self.get_tile(col, row))
                jstr += ", "
            jstr += str(self.get_tile(self.width - 1, row))
            if row < (self.height - 1):
                jstr += "],\n"
            else:
                jstr += "]\n ]\n"
        jstr += "}\n"
        return jstr

    def from_json_string(self, s):
        js = json.loads(s)
        self.width = js["width"]
        self.height = js["height"]
        self._mapData = js["_mapData"]

    def load(self, filename):
        load_file = open(filename, 'r')
        self.from_json_string(load_file.read())
        load_file.close()

    def save(self, filename):
        save_file = open(filename, 'w')
        save_file.write(self.to_json_string())
        save_file.close()


class LTAgentNode:
    def __init__(self, parent):
        self.parent = parent
        if parent is not None:
            self.x = parent.x
            self.y = parent.y
            self.score = parent.score
            self.state = parent.state
        else:
            self.x = 0
            self.y = 0
            self.score = 1000
            self.state = 0
        self.joiners = None

    def __str__(self):
        s = "(" + str(self.x) + "," + str(self.y) +\
            " state " + str(self.state) +\
            " score " + str(self.score)
        if self.joiners is not None:
            s = s + " with " + str(len(self.joiners)) + " joiners"
        return s
    
    def add_joiner(self, node):
        if self.joiners is None:
            self.joiners = []
        self.joiners.append(node)

    def set_location(self, x, y):
        self.x = x
        self.y = y

    def set_state(self, state, score=None):
        self.state = state
        if score is not None:
            self.score = score


class LTSpeedrunStateManager:
    def __init__(self, jump_height=4, can_backtrack=False):
        self.jump_height = jump_height
        self.backtracking = can_backtrack
        self.jump_start = 2 if can_backtrack else 1
        self.jump_angle_start = self.jump_start + jump_height
        self.jump_back_start = self.jump_angle_start + jump_height
        self.jump_end = self.jump_back_start
        if can_backtrack:
            self.jump_end += jump_height
        self.falling = self.jump_end
        self.falling_forward = self.falling + 1
        self.falling_back = self.falling_forward + 1

    def is_node_jumping(self, node, level_map):
        tile_above = level_map.get_tile(node.x, node.y-1)
        if tile_above >= 8:
            return False
        if (node.state >= self.jump_start) and (node.state < self.jump_end):
            jump_step = (node.state-self.jump_start) % self.jump_height
            if jump_step == (self.jump_height-1):
                return False
            return True
        return False

    def is_node_falling(self, node, level_map):
        tile_on = level_map.get_tile(node.x, node.y+1)
        if (tile_on < 8) or (tile_on == 9):
            if self.is_node_jumping(node, level_map):
                return False
            return True
        return False

    def can_enter(self, node, level_map):
        if (node.x < 0) or (node.x >= level_map.width) or (node.y < 0) or (node.y >= level_map.height):
            return False
        tile_in = level_map.get_tile(node.x, node.y)
        return False if ((tile_in > 9) or (tile_in == 8)) else True

    def is_alive(self, node, level_map):
        tile_in = level_map.get_tile(node.x, node.y)
        if (tile_in % 2) == 1:
            above = False if node.parent is None else \
                (True if node.y > node.parent.y else False)
            return True if (tile_in < 8 and above) else False
        return True if node.y < (level_map.height - 1) else False

    def force_jump(self, node, level_map):
        tile_on = level_map.get_tile(node.x, node.y+1)
        return True if (tile_on % 2) == 1 else False

    def generate_node(self, board, node, level_map, target_x, target_y, target_state):
        child = LTAgentNode(node)
        child.set_location(target_x, target_y)
        child.set_state(target_state, node.score-1)
        if self.can_enter(child, level_map):
            if self.is_alive(node, level_map):
                if self.force_jump(node, level_map):
                    child.set_location(target_x, target_y-1)
                    child.set_state(self.jump_start)
                board.add_node(child)

    def generate_children(self, board, node, level_map):
        if self.is_node_falling(node, level_map):
            if self.backtracking:
                self.generate_node(board, node, level_map, node.x-1, node.y+1, self.falling_back)
            self.generate_node(board, node, level_map, node.x, node.y+1, self.falling)
            self.generate_node(board, node, level_map, node.x+1, node.y+1, self.falling_forward)
        elif self.is_node_jumping(node, level_map):
            jump_step = ((node.state-self.jump_start) % self.jump_height) + 1
            if self.backtracking:
                self.generate_node(board, node, level_map, node.x-1, node.y-1, self.jump_back_start + jump_step)
            self.generate_node(board, node, level_map, node.x, node.y-1, self.jump_start + jump_step)
            self.generate_node(board, node, level_map, node.x+1, node.y-1, self.jump_angle_start + jump_step)
        else:
            self.generate_node(board, node, level_map, node.x+1, node.y, 0)
            if self.backtracking:
                self.generate_node(board, node, level_map, node.x-1, node.y, 1)
                self.generate_node(board, node, level_map, node.x-1, node.y-1, self.jump_back_start)
            self.generate_node(board, node, level_map, node.x, node.y-1, self.jump_start)
            self.generate_node(board, node, level_map, node.x+1, node.y-1, self.jump_angle_start)
            pass

        pass

    def get_num_states(self):
        return (self.falling_back+1) if self.backtracking else (self.falling_forward+1)

    def calculate_node_weight(self, node, map):
        return node.score + node.x - map.width


class LTPathBoard:
    def __init__(self, ltmap, ltstate_manager):
        self.level_map = ltmap
        self.state_manager = ltstate_manager
        self.best_nodes = [[[None for _ in range(ltmap.width)]
                            for _ in range(ltmap.height)]
                           for _ in range(ltstate_manager.get_num_states())]
        self.queue = []

    def dump_queue(self):
        for node in self.queue:
            print(node)

    def process_all_paths(self, start_x, start_y):
        root_node = LTAgentNode(None)
        root_node.set_location(start_x, start_y)
        self.add_node_to_queue(root_node)
        while(len(self.queue) > 0):
            node = self.queue.pop(0)
            #print("debug processing node: ", node)
            self.state_manager.generate_children(self, node, self.level_map)

    def remove_from_queue(self, node):
        if node in self.queue:
            self.queue.remove(node)

    def add_node_to_queue(self, node):
        node_weight = self.state_manager.calculate_node_weight(node, self.level_map)
        index = len(self.queue)
        for i in range (len(self.queue)):
            cur_weight = self.state_manager.calculate_node_weight(self.queue[i], self.level_map)
            if node_weight > cur_weight:
                index = i
                break
        self.queue.insert(index, node)

    def add_node(self, node):
        state = node.state
        x = node.x
        y = node.y
        best_node = self.best_nodes[state][y][x]
        if best_node is None:
            best_node = node
            self.add_node_to_queue(node)
        elif best_node.score < node.score:
            node.add_joiner(best_node)
            self.remove_from_queue(best_node)
            best_node = node
            self.add_node_to_queue(node)
        else:
            best_node.add_joiner(node)
        self.best_nodes[state][y][x] = best_node

    def get_nodes_in_column(self, column):
        column_nodes = []
        for row in range(self.level_map.height):
            for state in range(self.state_manager.get_num_states()):
                if self.best_nodes[state][row][column] is not None:
                    column_nodes.append(self.best_nodes[state][row][column])
        return column_nodes


class BasicExtractor:
    def __init__(self, ltmap, ltstate_manager, start_x, start_y):
        self.level_map = ltmap
        self.manager = ltstate_manager
        self.board = LTPathBoard(ltmap, ltstate_manager)
        self.board.process_all_paths(start_x, start_y)
        self.enter_map = np.zeros((ltmap.height, ltmap.width))

    def perform_extraction(self):
        for c in range(self.level_map.width):
            nodes = self.board.get_nodes_in_column(c)
            for node in nodes:
                self.enter_map[node.y,node.x] = 1
        return self.enter_map

    def find_longest_path(self):
        longest = self.level_map.width - 1
        while (longest > 0) and (len(self.board.get_nodes_in_column(longest)) == 0):
            longest -= 1
        return longest

    def enter_map_to_string(self):
        s = ""
        for col in range(self.level_map.width):
            cs = ""
            for row in range(self.level_map.height):
                cs += "." if self.enter_map[row,col] == 0 else "*"
            s = s + cs[::-1]
            s += "\n"
        return s

class PathEextractor(BasicExtractor):
    def __init__(self,  ltmap, ltstate_manager, start_x, start_y):
        super().__init__(ltmap, ltstate_manager, start_x, start_y)

    def find_best_path_node(self):
        last_col = self.find_longest_path()
        nodes = self.board.get_nodes_in_column(last_col)
        best_node = nodes.pop(0)
        for node in nodes:
            if node.score > best_node.score:
                best_node = node
        return best_node

    def perform_extraction(self):
        node = self.find_best_path_node()
        while node is not None:
            self.enter_map[node.y, node.x] = 1
            node = node.parent
        return self.enter_map

class LastInColumnPathExtractor(PathEextractor):
    def __init__(self,  ltmap, ltstate_manager, start_x, start_y):
        super().__init__(ltmap, ltstate_manager, start_x, start_y)

    def perform_extraction(self):
        node = self.find_best_path_node()
        current_column = node.x + 1
        while node is not None:
            if current_column != node.x:
                self.enter_map[node.y, node.x] = 1
                current_column = node.x
            node = node.parent
        return self.enter_map

class BestReachableAsFloatExtractor(PathEextractor):
    def __init__(self,  ltmap, ltstate_manager, start_x, start_y):
        super().__init__(ltmap, ltstate_manager, start_x, start_y)

    def perform_extraction(self):
        for c in range(self.level_map.width):
            nodes = self.board.get_nodes_in_column(c)
            for node in nodes:
                self.enter_map[node.y,node.x] = .5
        return super().perform_extraction()

    def enter_map_to_string(self):
        s = ""
        for col in range(self.level_map.width):
            cs = ""
            for row in range(self.level_map.height):
                weight = self.enter_map[row,col]
                cs += "." if weight < .25 else ("*" if weight > .75 else "!")
            s = s + cs[::-1]
            s += "\n"
        return s


class MockPathBoard:
    def __init__(self):
        pass

    def add_node(self, node):
        print(node)


def map_test():
    ltm = LiteTuxMap()
    ltm.from_json_string('{"width":5, "height":3, "_mapData":[[0,0,0,0,0],[0,0,0,0,0],[8,8,8,8,8]]}')
    print(ltm.to_vertical_string())


def agent_test():
    ltm = LiteTuxMap()
    ltm.from_json_string('{"width":3, "height":5, "_mapData":[[8,8,8],[0,0,0],[0,0,0],[0,0,0],[0,8,8]]}')
    test_node = LTAgentNode(None)
    test_node.set_location(1,1)
    sm = LTSpeedrunStateManager(4,True)
    for i in range(sm.get_num_states()):
        test_node.set_state(i)
        print(test_node, " is falling " +\
               str(sm.is_node_falling(test_node, ltm)) +\
            " is jumping " + str(sm.is_node_jumping(test_node, ltm)))

    ltm.from_json_string('{"width":16, "height":3, "_mapData":[[0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]]}')
    test_node.set_location(0,2)
    print("bottom test should be False: ", sm.is_alive(test_node, ltm))
    test_child_node = LTAgentNode(test_node)
    for i in range(16):
        test_node.set_location(i, 0)
        test_child_node.set_location(i,1)
        print("can enter {0} from above is {1}. Is alive from above is {2}".
              format(i, sm.can_enter(test_child_node, ltm), sm.is_alive(test_child_node, ltm)))
        test_node.set_location(i-1, 1)
        print("can enter {0} from side is {1}. Is alive from side is {2}".
              format(i, sm.can_enter(test_child_node, ltm), sm.is_alive(test_child_node, ltm)))

    ltm.from_json_string('{"width":3, "height":5, "_mapData":[[8,8,8],[0,0,0],[0,0,0],[0,0,0],[8,8,8]]}')
    board = MockPathBoard()
    print("near edge walking")
    test_node.set_location(0,3)
    sm.generate_children(board, test_node, ltm)
    print("near edge jumping")
    test_node.set_location(0,2)
    test_node.set_state(sm.jump_start)
    sm.generate_children(board, test_node, ltm)
    print("near edge falling")
    test_node.set_location(0,2)
    test_node.set_state(sm.falling)
    sm.generate_children(board, test_node, ltm)

    print("near middle walking")
    test_node.set_location(1,3)
    test_node.set_state(0)
    sm.generate_children(board, test_node, ltm)
    print("near middle jumping")
    test_node.set_location(1,2)
    test_node.set_state(sm.jump_start)
    sm.generate_children(board, test_node, ltm)
    print("near middle falling")
    test_node.set_location(1,2)
    test_node.set_state(sm.falling)
    sm.generate_children(board, test_node, ltm)


def queue_test():
    highest = LTAgentNode(None)
    highest.set_location(1, 1)
    highest.set_state(0, 1000)
    lost = LTAgentNode(None)
    lost.set_location(1, 1)
    lost.set_state(0, 1000)
    third = LTAgentNode(None)
    third.set_location(1, 2)
    third.set_state(0, 998)
    second = LTAgentNode(None)
    second.set_location(1, 3)
    second.set_state(0, 998)
    path = LTPathBoard(LiteTuxMap(10, 10), LTSpeedrunStateManager())
    path.add_node(highest)
    path.add_node(lost)
    path.add_node(third)
    path.add_node(second)
    path.dump_queue()

def board_test():
    ltm = LiteTuxMap()
    ltm.from_json_string('{"width":10, "height":10, "_mapData":[' +
        '[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],' +
        '[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,8,8,8,8,0,0,0],[0,0,0,0,0,0,0,0,0,0],' +
        '[0,0,0,0,0,0,0,0,0,0],[8,8,8,8,8,8,8,8,8,8]]}')
    sm = LTSpeedrunStateManager(4,True)
    board = LTPathBoard(ltm, sm)
    board.process_all_paths(0, 8)
    
#map_test()
#agent_test()
#queue_test()
#board_test()
ltm = LiteTuxMap(1,1)
ltm.load("levels/mario1-1.json")
sm = LTSpeedrunStateManager(4, True)
#extractor = BasicExtractor(ltm, sm, 0, 11)
#extractor = PathEextractor(ltm, sm, 0, 11)
#extractor = LastInColumnPathExtractor(ltm, sm, 0, 11)
extractor = BestReachableAsFloatExtractor(ltm, sm, 0, 11)
extractor.perform_extraction()
print(extractor.enter_map_to_string())

