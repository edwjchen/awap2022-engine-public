import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

'''
This bot randomly builds one building per turn (on a valid tile).
Note that your bot may build multiple structures per turn, as long as you can afford them.
'''

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0

        return


    def play_turn(self, turn_num, map, player_info):


        self.MAP_WIDTH = len(map)
        self.MAP_HEIGHT = len(map[0])

        # find tiles on my team
        my_structs = []
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                st = map[x][y].structure
                # check the tile is not empty
                if st is not None:
                    # check the structure on the tile is on my team
                    if st.team == player_info.team:
                        my_structs.append(st)

        # call helper method to build randomly
        self.try_random_build(map, my_structs, player_info)

        # randomly bid 1 or 2
        self.set_bid(random.randint(1, 2))

        return


    ''' Helper method for trying to build a random structure'''
    def try_random_build(self, map, my_structs, player_info):
        # choose a type of structure to build
        # build a tower for every 4 roads
        if len(my_structs) % 5 == 4:
            build_type = StructureType.TOWER
        else:
            build_type = StructureType.ROAD

        # identify the set of tiles that we can build on
        valid_tiles = []

        # look for a empty tile that is adjacent to one of our structs
        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                # check this tile contains one of our structures
                st = map[x][y].structure
                if st is None or st.team != player_info.team:
                    continue
                # check if any of the adjacent tiles are open
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    (nx, ny) = (st.x + dx, st.y + dy)
                    # check if adjacent tile is valid (on the map and empty)
                    if 0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT:
                        if map[nx][ny].structure is None:
                            cost = build_type.get_base_cost() * map[nx][ny].passability
                            # check if my team can afford this structure
                            if player_info.money >= cost:
                                # attempt to build
                                valid_tiles.append((nx, ny))

        # choose a random tile to build on
        if(len(valid_tiles) > 0):
            tx, ty = random.choice(valid_tiles)
            self.build(build_type, tx, ty)