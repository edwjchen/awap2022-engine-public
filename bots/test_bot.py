import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC
from heapq import heappush, heappop


class PQNode:

    def __init__(self, state, path, cost_from_start):
        self.state = state
        self.path = path
        self.g = cost_from_start

    def __gt__(self, other_node):
        return self.state > other_node.state


class PriorityQueue:

    def __init__(self):
        self.elements = []

    def nonempty(self):
        return bool(self.elements)

    def push(self, element, priority):
        heappush(self.elements, (priority, element))

    def pop(self):
        return heappop(self.elements)[1]

    def contains(self, state):
        return any(
            element.state == state
            for priority, element in self.elements
        )

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0

        return


    def play_turn(self, turn_num, map, player_info):
        self.width = len(map)
        self.height = len(map[0])
        self.find_tiles(map,player_info)

        print(self.distance(map,3,3,11,11))
        return

    def find_tiles(self, map, player_info):
        self.my_generators = []
        self.my_structs = set()
        self.other_structs = set()
        for x in range(self.width):
            for y in range(self.height):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        self.my_structs.add((x, y))
                        if st.type == StructureType.GENERATOR:
                            self.my_generators.append((x, y))
                    else:
                        self.other_structs.add((x, y))


    def distance(self, amap, x_1, y_1, x_2, y_2):
        print("INSIDE")
        output = []
        visited = [[0 for j in range(self.height)] for i in range(self.width)]
        for i in range(self.width): 
            for j in range(self.height): 
                if (i,j) in self.other_structs: 
                    visited[i][j] = 1

        PQ = PriorityQueue() 
        PQ.push(PQNode((x_1,y_1),[],0),0)#TODO HEURISTIC)
        while(PQ.nonempty()): 
            curr_node = PQ.pop()
            if curr_node.state == (x_2,y_2): 
                #FOUND GOAL 
                return curr_node.path
            else: 
                curr_x = curr_node.state[0]
                curr_y = curr_node.state[1]
                if visited[curr_x][curr_y] == 0: 
                    curr_path = curr_node.path 
                    for d in GC.MOVE_DIRS: # EXPAND NEXT POSSIBLE 
                        next_state_x = curr_x + d[0]
                        next_state_y = curr_y + d[1]
                        next_state = (next_state_x,next_state_y) 
                        next_path = curr_path.copy() 
                        next_path.append(next_state)
                        if next_state_x >= 0 and next_state_x <= self.width and next_state_y >= 0 and next_state_y <= self.height: 
                            PQ.push(PQNode(next_state,next_path,curr_node.g + amap[next_state_x][next_state_y].passability),0)
                    visited[curr_x][curr_y] = 1 

        return False