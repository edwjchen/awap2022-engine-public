import sys

import random
import math

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0
        self.cluster_size = 5
        return


    def play_turn(self, turn_num, map, player_info):
        self.width = len(map)
        self.height = len(map[0])
        self.find_tiles(map, player_info)
        path = self.compute_cluster(map, player_info)
        remaining_money = player_info.money
        for i, (x, y) in enumerate(path)
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
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        self.my_structs.append((x, y))
                        if st.type == StructureType.GENERATOR:
                            self.my_generators.append((x, y))
                    else:
                        self.other_structs.append((x, y))

    def compute_cluster(self, map, player_info):
        max_ratio = 0
        max_path = []
        for x in range(self.width):
            for y in range(self.height):
                cluster_population = self.cluster_population(self, map, x, y, [[-2, 0], [-1, -1], [-1, 0], [-1, 1], [0, -2], [0, -1], [0, 0], [0, 1], [0, 2], [1, -1], [1, 0], [1, 1], [2, 0]])
                if cluster_population > 0:
                    distance, path = self.cluster_path(self, map, x, y)
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
            distance, path = path(map, s[0], s[1], x, y)
            if distance <= min_distance:
                min_path = path
        return min_distance, min_path
    
    def path(self, map, x_1, y_1, x_2, y_2):
        # todo
        return 0
