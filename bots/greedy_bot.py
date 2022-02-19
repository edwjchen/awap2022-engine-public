import sys

import random

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
        self.find_tiles


        for i in range(self.width, self)

        return

    def find_tiles(self, map, player_info):
        self.my_generators = []
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
        for x in range(self.width - self.cluster_size):
            for y in range(self.height - self.cluster_size):
                cluster_population = 0
                for i in range(self.cluster_size):
                    for j in range(self.cluster_size):
                        cluster_population += map[x + i][y + j].population

    def cluster_distance(self, map, x_2, y_2):
        for 
    
    def distance(self, map, x_1, y_1, x_2, y_2):
        # todo
        return 0
