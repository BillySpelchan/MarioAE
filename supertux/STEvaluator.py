# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:36:47 2019

@author: Billy D. Spelchan
"""

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
        elif self.head_node.time_taken > node.time_taken:
            self.head_node.prev = node
            node.next =self.head_node
            self.head_node = node
        else:
            nextnode = self.head_node
            notdone = True
            while notdone:
                if nextnode.next is None:
                    notdone = False
                elif node.time_taken < nextnode.next.time_taken:
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
    
    def __init__(self, parent=None, time=0):
        self.parent = parent
        if parent is not None:            
            self.x = parent.x
            self.y = parent.y
            self.move_speed = parent.move_speed
            self.jump_start = parent.jump_start
            self.jump_state = parent.jump_state
            self.time_taken = parent.time_taken
        else:
            self.x = 0
            self.y = 0
            self.move_speed = 0
            self.jump_start = 0
            self.jump_state = 0
            self.time_taken = time
            
        self.prev = None
        self.next = None

    def setLocation(self, x, y, isFalling):
        self.x = x
        self.y = y
        self.jump_state = STANode.JUMP_FREEFALL if isFalling else STANode.JUMP_NONE
        
    
    def generate_forward_node(self, controller):
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
        
        child.time_taken += (4-child.move_speed)
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
        return child
    
    def generate_jump_node(self, controller):
        if self.jump_state < 0 or self.jump_state > STANode.JUMP_PEEK:
            return None
        if self.jump_state == 0 and self.jump_start == self.x:
            return None
        child = STANode(self)
        if child.jump_state == 0:
            child.jump_start = child.x
        child.time_taken += 1
        child.jump_state += 1
        if (child.jump_state > STANode.JUMP_PEEK):
            child.jump_state = STANode.JUMP_FREEFALL
        elif controller.can_enter(child.x, child.y-1):
            child.y -= 1
        return child
    
class STMapSliceController:
    """
    Remember that we are using c,r format for maps as we care about vertical
    slices of the column.
    """
    
    def __init__(self, slc = None):
        self.current_slice = slc
        
    def set_slice(self, slc):
        self.current_slice = slc
        
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


       
        