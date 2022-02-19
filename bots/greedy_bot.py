import sys

import random
import math
from heapq import heappush, heappop

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

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
        self.cluster_size = 5
        self.tower_radius = [[-2, 0], [-1, -1], [-1, 0], [-1, 1], [0, -2], [0, -1], [0, 0], [0, 1], [0, 2], [1, -1], [1, 0], [1, 1], [2, 0]]
        return


    def play_turn(self, turn_num, map, player_info):
        self.width = len(map)
        self.height = len(map[0])
        self.find_tiles(map, player_info)
        path = self.compute_cluster(map, player_info)
        remaining_money = player_info.money
        for i, (x, y) in enumerate(path):
            if i < len(path) - 1:
                if remaining_money >= map[x][y].passability * StructureType.ROAD.get_base_cost():
                    self.build(StructureType.ROAD, x, y)
                else:
                    continue
            else:
                if remaining_money >= map[x][y].passability * StructureType.TOWER.get_base_cost():
                    self.build(StructureType.TOWER, x, y)
        return

    def find_tiles(self, map, player_info):
        self.my_generators = []
        self.my_structs = []
        self.other_structs = []
        self.covered = [[0] * self.height] * self.width

        for x in range(self.width):
            for y in range(self.height):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        self.my_structs.append((x, y))
                        if st.type == StructureType.GENERATOR:
                            self.my_generators.append((x, y))
                        if st.type == StructureType.TOWER:
                            for dx, dy in self.tower_radius:
                                if x + dx in range(self.width) and y + dy in range(self.height):
                                    self.covered[x + dx][y + dy] = 1
                    else:
                        self.other_structs.append((x, y))

    def compute_cluster(self, map, player_info):
        max_ratio = 0
        max_path = []
        for x in range(self.width):
            for y in range(self.height):
                cluster_population = self.cluster_population(map, x, y, self.tower_radius)
                if cluster_population > 0:
                    distance, path = self.cluster_path(map, x, y)
                    if distance > 0 and cluster_population / distance > max_ratio:
                        max_ratio = cluster_population / distance
                        max_path = path
        return max_path

    def cluster_population(self, map, x, y, ds):
        cluster_population = 0
        for d in ds:
            cluster_population += map[x + d[0]][y + d[1]].population
        return cluster_population

    def cluster_path(self, map, x, y):
        min_distance = math.inf
        min_path = []
        for s in self.my_structs:
            distance, path = self.path(map, s[0], s[1], x, y)
            if distance <= min_distance:
                min_path = path
        return min_distance, min_path
    
    def path(self, map, x_1, y_1, x_2, y_2):
        output = []
        visited = [[0 for j in range(self.height)] for i in range(self.width)]
        for i in range(self.width): 
            for j in range(self.height): 
                if (i,j) in self.other_structs: 
                    visited[i][j] = 1

        PQ = PriorityQueue() 
        PQ.push(PQNode((x_1, y_1), [], 0), 0)
        while PQ.nonempty(): 
            curr_node = PQ.pop()
            if curr_node.state == (x_2, y_2): 
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
                            PQ.push(PQNode(next_state,next_path,curr_node.g + map[next_state_x][next_state_y].passability),0)
                    visited[curr_x][curr_y] = 1 

        return False
