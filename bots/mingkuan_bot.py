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
        self.my_structs = None
        self.other_structs = None
        self.width = 0
        self.height = 0

        return

    def play_turn(self, turn_num, map, player_info):
        if self.my_generators is None:
            self.width = len(map)
            self.height = len(map[0])
            self.find_tiles(map, player_info)

        self.set_bid(0)
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