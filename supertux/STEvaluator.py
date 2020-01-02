# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:36:47 2019

@author: Billy D. Spelchan
"""
import numpy as np

class STPriorityQueue:
    def __init__(self):
        self.head_node = None
    
    def enqueue(self, node):
        """
        Used to put node in linked list in order based on lowest time first.
        
        Parameters
        ----------
        node : STANode
            Node to be added to the priority queue

        Returns
        -------
        None
        """
        if self.head_node is None:
            self.head_node = node
        elif self.head_node.priority > node.priority:
            self.head_node.prev = node
            node.next =self.head_node
            self.head_node = node
        else:
            nextnode = self.head_node
            notdone = True
            while notdone:
                if nextnode.next is None:
                    notdone = False
                elif node.priority < nextnode.next.priority:
                    notdone = False
                else:
                    nextnode = nextnode.next
            node.next = nextnode.next
            node.prev = nextnode
            nextnode.next = node

    def dequeue(self):
        last_head = self.head_node
        if last_head is not None:
            self.head_node = last_head.next
            if self.head_node is not None:
                self.head_node.prev = None
            
        return last_head


class STANode:
    SPEED_STOPPED = 0
    SPEED_WALK = 1
    SPEED_JOG = 2
    SPEED_RUN = 3
    JUMP_NONE = 0
    JUMP_JUMPED = 1
    JUMP_RISING = 2
    JUMP_MID = 3
    JUMP_NEAR_PEAK = 4
    JUMP_PEEK = 5
    JUMP_FREEFALL = -1
    
    def __init__(self, parent=None):
        self.parent = parent
        if parent is not None:            
            self.x = parent.x
            self.y = parent.y
            self.move_speed = parent.move_speed
            self.jump_start = parent.jump_start
            self.jump_state = parent.jump_state
            self.time_taken = parent.time_taken
            self.priority = parent.priority
        else:
            self.x = 0
            self.y = 0
            self.move_speed = 0
            self.jump_start = 0
            self.jump_state = 0
            self.time_taken = 0
            self.priority = 0
            
        self.prev = None
        self.next = None

    def __str__(self):
        s = str(self.x) + "," + str(self.y)
        s += " moving at " + str(self.move_speed)
        if (self.jump_state < 0):
            s += " falling"
        elif (self.jump_state > 0):
            s += " jumping from " + str(self.jump_start)
            s += " phase " + str(self.jump_state)
        s += " time " + str(self.time_taken)
        s += " priority " + str(self.priority)
        return s

    def setLocation(self, x, y, isFalling):
        self.x = x
        self.y = y
        self.jump_state = STANode.JUMP_FREEFALL if isFalling else STANode.JUMP_NONE
        

    def adjust_time(self, controller, time_to_add):
        self.time_taken += time_to_add
        distance_delta = controller.get_num_columns() - self.x
        self.priority = self.time_taken + (distance_delta * 4)

        
    def generate_forward_node(self, controller):
        if self.jump_state != 0:
            return None
        hit_wall = not controller.can_enter(self.x+1, self.y)
        if (hit_wall) and (self.move_speed == 0):
            return None
        child = STANode(self)
        if hit_wall:
            child.move_speed = 0
        else:
            child.x = self.x+1
            if self.move_speed < STANode.SPEED_RUN:
                child.move_speed += 1
                
        if controller.can_enter(child.x, child.y-1):                
                    child.jump_state = -1        
        child.adjust_time(controller, 4-child.move_speed)
        return child

    def generate_freefall_node(self, controller):
        if self.jump_state != STANode.JUMP_FREEFALL:
            return None
        child = STANode(self)
        # sanity check for falling when should have landed
        if (controller.can_enter(child.x, child.y+1)):
            child.y += 1
        #landing check
        if not(controller.can_enter(child.x, child.y+1)):
            child.jump_state = 0
            child.move_speed = 0
        child.time_taken += 1
        child.adjust_time(controller, 1)
        return child
    
    def generate_freefall_angle_node(self, controller):
        child = self.generate_freefall_node(controller)
        if (child is None) or (child.jump_state >= 0):
            return None
        if controller.can_enter(child.x+1, child.y):
            child.x += 1
            child.jump_state = -1 if controller.can_enter(child.x, child.y+1) else 0
            child.adjust_time (controller, 4-child.move_speed)
            return child
        return None
    
    def generate_jump_node(self, controller):
        if self.jump_state < 0 or self.jump_state > STANode.JUMP_PEEK:
            return None
        if self.jump_state == 0 and self.jump_start == self.x:
            return None
        child = STANode(self)
        if child.jump_state == 0:
            child.jump_start = child.x
        child.adjust_time (controller, 1)
        child.jump_state += 1
        if (child.jump_state > STANode.JUMP_PEEK):
            child.jump_state = STANode.JUMP_FREEFALL
        elif controller.can_enter(child.x, child.y-1):
            child.y -= 1
        return child

    def generate_jump_angle_node(self, controller):
        child = self.generate_jump_node(controller)
        if child is None:
            return None
        if controller.can_enter(child.x+1, child.y):
            child.x += 1
            child.adjust_time (controller, 4-child.move_speed)
            return child
        return None
    
    
class STMapSliceController:
    """
    Remember that we are using c,r format for maps as we care about vertical
    slices of the column.
    """
    
    def __init__(self, slc = None):
        self.current_slice = slc
        
    def set_slice(self, slc):
        self.current_slice = slc
        
    def get_num_columns(self):
        return self.current_slice.shape[0]
    
    def can_enter(self, x, y):
        if x < 0: return False
        if x >= self.current_slice.shape[0]: return False
        if y < 0: return True
        if y >= self.current_slice.shape[1]: return True
        return self.current_slice[x, y] < .5

    def is_alive(self, x, y):
        if x < 0: return False
        if x >= self.current_slice.shape[0]: return False
        if y < 0: return True
        if y >= self.current_slice.shape[1]: return False
        return self.current_slice[x, y] < .5

    def has_won(self, x, y):
        if x >= self.current_slice.shape[0]-1: 
            return self.is_alive(x,y)
        return False
    
    def get_map_column_as_string(self, col, path_nodes=None):
        rows = self.current_slice.shape[1]
        result= ''
        for y in range(rows):
            row = rows-y-1
            ch = '.' if self.current_slice[col,row] < .5 else 'X'
            if path_nodes is not None:
                for p in path_nodes:
                    if (p.x == col) and (p.y == row):
                        ch = '@'
                        break
            result += ch
        return result


    def print_map(self, path_nodes=None):
        cols = self.current_slice.shape[0]
        
        for col in range (cols):
            print(self.get_map_column_as_string(col, path_nodes))


class STAStarPath:
    def __init__(self, controller, start_x, start_y):
        self.controller = controller
        self.start_x = start_x
        self.start_y = start_y
        self.best = None
        self.pq = STPriorityQueue()

    def validate_node(self, node):
        if node is None: return
        if self.controller.is_alive(node.x, node.y):
            t = self.best[node.jump_state+1, node.x, node.y]
            if t < 1 or t > node.priority:
                print(node.x,",",node.y, " now ", node.priority)
                self.best[node.jump_state+1, node.x, node.y] = node.priority
                self.pq.enqueue(node)

    def get_path_from_node(self, node):
        if node is None:
            return []
        path = [node]
        while node.parent is not None:
            path.append(node.parent)
            node = node.parent
        path.reverse()
        return path
    
    def find_path(self):
        start = STANode()
        end = None
        start.setLocation(self.start_x, self.start_y, True)
        while self.pq.dequeue() is not None: pass
        self.pq.enqueue(start)
        map_shape = self.controller.current_slice.shape #kludge
        self.best = np.zeros((7, map_shape[0], map_shape[1])) #kludge
                        
        finished = False
        while not finished:
            node = self.pq.dequeue()
            print("node: ",str(node))
            if node is None:
                finished = True
            elif self.controller.has_won(node.x, node.y):
                end = node
                finished = True
            else:
                self.validate_node(node.generate_forward_node(self.controller))
                self.validate_node(node.generate_freefall_node(self.controller))
                self.validate_node(node.generate_freefall_angle_node(self.controller))
                self.validate_node(node.generate_jump_node(self.controller))
                self.validate_node(node.generate_jump_angle_node(self.controller))
        # end while
        return self.get_path_from_node(end)
        
    
# PROTOTYPING WORK
        
if __name__ == '__main__':
    MAP_WALKING = [[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1] ]
    MAP_BLOCKED = [[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1],[1,1,1,1,1,1,1],[0,0,0,0,0,0,1],
               [0,0,0,0,0,0,1] ]
    COMPLEX_PATH = [ [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1],[1,0,0,0,0,0,1],[1,0,0,1,0,0,0],
                [1,0,0,1,0,0,0],[1,0,0,1,0,0,0],[1,0,0,1,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],
                [0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],
                [0,0,0,0,0,0,1] ]

    #slc = np.array(MAP_WALKING)
    #slc = np.array(MAP_BLOCKED)
    slc = np.array(COMPLEX_PATH)
    controller = STMapSliceController(slc)
    pf = STAStarPath(controller, 0,5)
    path = pf.find_path()
    controller.print_map(path)
        
 
       
        