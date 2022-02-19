import sys

import random

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC
# from copy import deepcopy
import numpy as np


class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0
        self.my_generators = None
        self.my_structs = None
        self.other_structs = None
        self.width = 0
        self.height = 0
        self.tower_dirs = [(-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                           (1, -1), (1, 0), (1, 1), (2, 0)]
        return

    def play_turn(self, turn_num, map, player_info):
        if self.my_generators is None:
            self.width = len(map)
            self.height = len(map[0])
        self.find_tiles(map, player_info)
        route, population = self.find_nearest_towers_to_build(map, player_info)
        if route is None:
            self.set_bid(0)
            return
        money_to_spend = 0
        bid = 0
        bid_every = 100
        # TODO: adjust bid according to opponent's action
        while True:
            num_to_build = 0
            while num_to_build < len(route):
                new_money_to_spend = money_to_spend + (250 if num_to_build == len(route) - 1 else 10) * \
                                     map[route[num_to_build][0]][route[num_to_build][1]].passability
                # bid = new_money_to_spend // bid_every
                if (turn_num % 2 == 1) == (player_info.team == Team.RED):
                    bid = 1
                else:
                    bid = 0
                if new_money_to_spend + bid <= player_info.money:
                    money_to_spend = new_money_to_spend
                    num_to_build += 1
                else:
                    break
            for i in range(num_to_build):
                self.build(StructureType.TOWER if i == len(route) - 1 else StructureType.ROAD, route[i][0], route[i][1])
            if num_to_build < len(route):
                break
            for i in range(num_to_build):
                map[route[i][0]][route[i][1]].structure = Structure(
                    StructureType.TOWER if i == len(route) - 1 else StructureType.ROAD, route[i][0], route[i][1],
                    player_info.team)
            self.find_tiles(map, player_info)
            route, population = self.find_nearest_towers_to_build(map, player_info)
        self.set_bid(bid)

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

    def find_nearest_towers_to_build(self, map, player_info):
        q = [[]]  # queue for bfs
        q[0] = list(self.my_structs)
        current_dist = 0
        maxhw = max(self.height, self.width)
        dist = np.full((maxhw, maxhw), -1)
        for st in self.my_structs:
            dist[st] = 0
        # dist[list(self.my_structs)] = 0
        value = np.empty((), dtype=object)
        value[()] = (-1, -1)
        dist_from = np.full((maxhw, maxhw), value, dtype=object)
        while current_dist < len(q):
            for pos in q[current_dist]:
                if dist[pos] != current_dist:
                    continue
                for d in GC.MOVE_DIRS:
                    new_pos = (pos[0] + d[0], pos[1] + d[1])
                    if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[1] >= self.height:
                        continue
                    if map[new_pos[0]][new_pos[1]].structure is not None and map[new_pos[0]][
                        new_pos[1]].structure.team != player_info.team:
                        continue
                    new_dist = current_dist + map[new_pos[0]][new_pos[1]].passability
                    if dist[new_pos] == -1 or new_dist < dist[new_pos]:
                        dist[new_pos] = new_dist
                        dist_from[new_pos] = pos
                        while len(q) <= new_dist:
                            q.append([])
                        q[new_dist].append(new_pos)
            current_dist += 1
        tower_population = np.full((maxhw, maxhw), 0)
        for x in range(self.width):
            for y in range(self.height):
                if map[x][y].population > 0:
                    covered_by_us = False
                    for d in self.tower_dirs:
                        new_pos = (x + d[0], y + d[1])
                        if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[1] >= self.height:
                            continue
                        if map[new_pos[0]][new_pos[1]].structure is not None:
                            st = map[new_pos[0]][new_pos[1]].structure
                            if st.type == StructureType.TOWER:
                                if st.team == player_info.team:
                                    covered_by_us = True
                                    break
                    if not covered_by_us:
                        for d in self.tower_dirs:
                            new_pos = (x + d[0], y + d[1])
                            if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[
                                1] >= self.height:
                                continue
                            tower_population[new_pos[0], new_pos[1]] += map[x][y].population
        best_tower = None
        best_tower_ratio = 0
        min_passability = 10
        for x in range(self.width):
            for y in range(self.height):
                if map[x][y].structure is None:
                    passability = map[x][y].passability
                    current_ratio = tower_population[x][y] / (dist[x, y] + map[x][y].passability * 24)
                    if best_tower is None or (dist[x, y] > 0 and current_ratio > best_tower_ratio):
                        best_tower = (x, y)
                        best_tower_ratio = current_ratio
                        min_passability = passability
                    if not best_tower_ratio and passability < min_passability:
                        # TODO: can make this random valid reachable location
                        min_passability = passability
                        best_tower = (x, y)

        if best_tower is None:
            return None, None
        best_tower_route = [best_tower]
        while best_tower_route[-1][0] != -1:
            best_tower_route.append(dist_from[best_tower_route[-1][0], best_tower_route[-1][1]])
            if best_tower_route[-1][0] != -1 and dist[best_tower_route[-1][0], best_tower_route[-1][1]] == 0:
                break
        best_tower_route.pop()
        best_tower_route.reverse()
        assert best_tower_route[-1] == best_tower
        return best_tower_route, tower_population[best_tower[0], best_tower[1]]


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
