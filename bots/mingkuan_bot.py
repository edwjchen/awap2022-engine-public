import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC


class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0
        self.my_generators = None
        self.other_structs = None

        return

    def play_turn(self, turn_num, map, player_info):
        if self.my_generators is None:
            self.MAP_WIDTH = len(map)
            self.MAP_HEIGHT = len(map[0])
            self.find_generators(map, player_info)

        self.set_bid(0)
        return

    def find_generators(self, map, player_info):
        self.my_generators = []
        self.other_structs = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        if st.type == StructureType.GENERATOR:
                            self.my_generators.append((x, y))
                    else:
                        self.other_structs.append((x, y))
