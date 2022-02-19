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
        self.block_population_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        self.best_blocking = None
        self.best_blocking_route = None
        self.blocking_population = 0
        return

    def choose_to_block(self, map, tower_route, tower_population):
        if self.best_blocking_route is None:
            return False
        if tower_route is None:
            return True
        tower_money = 0
        for i in range(len(tower_route)):
            tower_money += (25 if i == len(tower_route) - 1 else 1) * \
                           map[tower_route[i][0]][tower_route[i][1]].passability
        blocking_money = 0
        for i in range(len(self.best_blocking_route)):
            blocking_money += map[self.best_blocking_route[i][0]][self.best_blocking_route[i][1]].passability
        return self.blocking_population / blocking_money > tower_population / tower_money

    def play_turn(self, turn_num, map, player_info):
        if self.my_generators is None:
            self.width = len(map)
            self.height = len(map[0])
        self.find_tiles(map, player_info)
        route, population = self.find_best_to_build(map, player_info)
        choose_to_block_now = False
        if self.choose_to_block(map, route, population):
            choose_to_block_now = True
            route = self.best_blocking_route
        else:
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
                new_money_to_spend = money_to_spend + (
                    250 if (num_to_build == len(route) - 1 and not choose_to_block_now) else 10) * \
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
                self.build(
                    StructureType.TOWER if (i == len(route) - 1 and not choose_to_block_now) else StructureType.ROAD,
                    route[i][0], route[i][1])
            if num_to_build < len(route):
                break
            for i in range(num_to_build):
                map[route[i][0]][route[i][1]].structure = Structure(
                    StructureType.TOWER if (i == len(route) - 1 and not choose_to_block_now) else StructureType.ROAD,
                    route[i][0], route[i][1],
                    player_info.team)
            self.find_tiles(map, player_info)
            route, population = self.find_best_to_build(map, player_info)
            if route is None:
                break
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

    def route_to_block(self, start_blocking_pos, map, player_info, original_dist, original_dist_from):
        population_positions = [start_blocking_pos]
        num = 0
        while num < len(population_positions):
            for d in self.block_population_dirs:
                new_pos = (population_positions[num][0] + d[0], population_positions[num][1] + d[1])
                if new_pos in population_positions or new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or \
                        new_pos[1] >= self.height or map[new_pos[0]][new_pos[1]].population == 0:
                    continue
                population_positions.append(new_pos)
            num += 1
        num = 0
        block_positions = set()
        while num < len(population_positions):
            for d in GC.MOVE_DIRS:
                new_pos = (population_positions[num][0] + d[0], population_positions[num][1] + d[1])
                if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[1] >= self.height:
                    continue
                block_positions.add(new_pos)
            num += 1
        self.blocking_population = 0
        for pos in population_positions:
            self.blocking_population += map[pos[0]][pos[1]].population
        for pos in block_positions:
            if map[pos[0]][pos[1]].structure is not None and map[pos[0]][pos[1]].structure.team != player_info.team:
                return None  # failed to block
        upper_left = min(block_positions)
        bottom_right = max(block_positions)
        # TODO: boundaries
        S = (upper_left[0], upper_left[1] - 1)
        T = (upper_left[0] - 1, upper_left[1])
        leftmost = 10000
        rightmost = -1
        for pos in block_positions:
            leftmost = min(leftmost, pos[1])
            rightmost = max(rightmost, pos[1])
        floating_in_the_middle = True
        if upper_left[0] == 0 or bottom_right[0] == self.width - 1:
            floating_in_the_middle = False
        if leftmost == 0 or rightmost == self.height - 1:
            floating_in_the_middle = False
        if not floating_in_the_middle:
            if (upper_left[0] == 0) + (bottom_right[0] == self.width - 1) + (leftmost == 0) + (rightmost == self.height - 1) == 1:
                # only touch 1 boundary
                if upper_left[0] == 0:
                    S = (0, upper_left[1] - 1)
                    T = -1
                    for pos in block_positions:
                        if pos[0] == 0 and pos[1] > T:
                            T = pos[1]
                    T = (0, T + 1)
                elif bottom_right[0] == self.width - 1:
                    S = (self.width - 1, bottom_right[1] + 1)
                    T = 10000
                    for pos in block_positions:
                        if pos[0] == self.width - 1 and pos[1] < T:
                            T = pos[1]
                    T = (self.width - 1, T - 1)
                elif leftmost == 0:
                    S = 10000
                    T = -1
                    for pos in block_positions:
                        if pos[1] == 0:
                            S = min(S, pos[0])
                            T = max(T, pos[0])
                    S = (S - 1, 0)
                    T = (T + 1, 0)
                else:
                    S = 10000
                    T = -1
                    for pos in block_positions:
                        if pos[1] == self.height - 1:
                            S = min(S, pos[0])
                            T = max(T, pos[0])
                    S = (S - 1, 0)
                    T = (T + 1, 0)
            else:
                # TODO: 2 boundaries
                return None
        q = [[]]  # queue for bfs
        q[0] = [S]
        current_dist = 0
        maxhw = max(self.height, self.width)
        dist = np.full((maxhw, maxhw), -1)
        dist[S] = 0
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
                    if floating_in_the_middle:
                        if (pos[1] == upper_left[1] - 1 and new_pos[1] == upper_left[1]) or (
                                pos[1] == upper_left[1] and new_pos[0] == upper_left[1] - 1):
                            if pos[0] <= upper_left[0]:
                                continue  # not allowed to move
                    if map[new_pos[0]][new_pos[1]].structure is not None and map[new_pos[0]][
                        new_pos[1]].structure.team != player_info.team:
                        continue
                    if new_pos in block_positions:
                        continue
                    new_dist = current_dist + map[new_pos[0]][new_pos[1]].passability
                    if dist[new_pos] == -1 or new_dist < dist[new_pos]:
                        dist[new_pos] = new_dist
                        dist_from[new_pos] = pos
                        while len(q) <= new_dist:
                            q.append([])
                        q[new_dist].append(new_pos)
            current_dist += 1
        if dist[T] == -1:
            return None
        route = [T]
        while route[-1][0] != -1:
            route.append(dist_from[route[-1][0], route[-1][1]])
            if route[-1][0] != -1 and dist[route[-1][0], route[-1][1]] == 0:
                break
        route.reverse()
        nearest_pos = 0
        min_dist = None
        for i in range(len(route)):
            if min_dist is None or (original_dist[route[i][0], route[i][1]] != -1 and original_dist[
                route[i][0], route[i][1]] < min_dist):
                min_dist = original_dist[route[i][0], route[i][1]]
                nearest_pos = i
        route = route[nearest_pos:] + route[:nearest_pos]
        route.reverse()
        while route[-1][0] != -1 and original_dist_from[route[-1][0], route[-1][1]] != 0:
            route.append(original_dist_from[route[-1][0], route[-1][1]])
        route.reverse()
        route2 = []
        for pos in route:
            if map[pos[0]][pos[1]].structure is None:
                route2.append(pos)
        return route2

    def find_best_to_build(self, map, player_info):
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
        tower_population_other = np.full((maxhw, maxhw), 0)
        for x in range(self.width):
            for y in range(self.height):
                if map[x][y].population > 0:
                    covered_by_us = False
                    covered_by_other = False
                    for d in self.tower_dirs:
                        new_pos = (x + d[0], y + d[1])
                        if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[1] >= self.height:
                            continue
                        if map[new_pos[0]][new_pos[1]].structure is not None:
                            st = map[new_pos[0]][new_pos[1]].structure
                            if st.type == StructureType.TOWER:
                                if st.team == player_info.team:
                                    covered_by_us = True
                                else:
                                    covered_by_other = True
                    if not covered_by_us:
                        for d in self.tower_dirs:
                            new_pos = (x + d[0], y + d[1])
                            if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[
                                1] >= self.height:
                                continue
                            tower_population[new_pos[0], new_pos[1]] += map[x][y].population
                    if not covered_by_other:
                        for d in self.tower_dirs:
                            new_pos = (x + d[0], y + d[1])
                            if new_pos[0] < 0 or new_pos[0] >= self.width or new_pos[1] < 0 or new_pos[
                                1] >= self.height:
                                continue
                            tower_population_other[new_pos[0], new_pos[1]] += map[x][y].population
        self.best_blocking = None
        best_blocking_ratio = 0
        for x in range(self.width):
            for y in range(self.height):
                current_ratio = tower_population_other[x][y] / dist[x, y]
                # TODO: this ratio is a very inaccurate heuristic
                if self.best_blocking is None or current_ratio > best_blocking_ratio:
                    self.best_blocking = (x, y)
                    best_blocking_ratio = current_ratio
        self.best_blocking_route = self.route_to_block(self.best_blocking, map, player_info, dist, dist_from)
        best_tower = None
        best_tower_ratio = 0
        for x in range(self.width):
            for y in range(self.height):
                if map[x][y].structure is None:
                    current_ratio = tower_population[x][y] / (dist[x, y] + map[x][y].passability * 24)
                    if best_tower is None or (dist[x, y] > 0 and current_ratio > best_tower_ratio):
                        best_tower = (x, y)
                        best_tower_ratio = current_ratio
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
