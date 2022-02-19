'''
Game
todo: add checks for connections
todo: basic viewer
'''

import random
import time
import math
import json
import signal
from contextlib import contextmanager
import os
import traceback


from .structure import *
from .player import *
from .game_constants import GameConstants as GC
from .custom_json import CustomEncoder


'''
Class containing information about a single tile

Fields:
-----
x - x position of this tile
y - y position of this tile
population - population of this tile
passability - passability of this tile

'''
class Tile:
    def __init__(self, x, y, passability, population, structure):
        self.x = x
        self.y = y
        self.passability = passability
        self.population = population
        self.structure = structure

    def _copy(self):
        return Tile(self.x, self.y, self.passability, self.population, Structure.make_copy(self.structure))

'''
Contains many useful functions for map operations
- symmetry operations
-

'''
class MapUtil:

    @classmethod
    def x_sym(self, x, y, width, height):
        return (width - 1 - x, y)

    @classmethod
    def y_sym(self, x, y, width, height):
        return (x, height - 1 - y)

    @classmethod
    def rot_sym(self, x, y, width, height):
        return (width - 1 - x, height - 1 - y)


    '''
    Returns a list of tuples containing all of the (dx, dy) pairs within rad2 distance
    '''
    def get_diffs(radius):
        max_rad = int(radius)
        diffs = []
        for di in range(-max_rad, max_rad + 1):
            for dj in range(-max_rad, max_rad + 1):
                if di * di + dj * dj <= pow(radius, 2):
                    diffs += [(di, dj)]
        return diffs

    '''
    Returns the r^2 distance between (x1, y1) and (x2, y2)
    '''
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy


'''
Contains all the necessary info to make a unique map
seed - seed number used for random generation
width - width of the map
height - height of the map
sym - type of symmetry (x, y, rotational)
num_generators - number of initial generators for each team
num_cities - number of cities
'''
class MapInfo():
    def __init__(self, seed=0, width=48, height=48, sym=MapUtil.x_sym, num_generators=1, num_cities=10, custom_map_path=None, passability=None):
        self.seed = seed
        self.width = width
        self.height = height
        self.sym = sym
        self.num_generators = num_generators
        self.num_cities = num_cities
        self.custom_map_path = custom_map_path
        self.passability = passability


import importlib.util
import sys
def import_file(module_name, file_path):
    print("Loading", module_name, file_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module

'''
Class for timeout interruptions of turns - SIGINT non functional on Windows
'''
if os.name != 'nt':
    class TimeoutException(Exception): pass

    @contextmanager
    def time_limit(seconds):
        def signal_handler(signum, frame):
            raise TimeoutException("Timed out!")
        signal.signal(signal.SIGALRM, signal_handler)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield
        finally:
            signal.alarm(0)
else:
    class TimeoutException(Exception): pass



'''
Variables:

[Note that 'pX' can be 'p1' or 'p2']

self.pX_state contains PlayerInfo object about pX
    - Stores money/utility for each player
    - Changes to money/utility should be made to this

self.map contains 2d grid of Tiles
    - Contains information about population and structures on each tile
    - Changes to population/structures should be made to this

self.pX contains pX's bot

'''
class Game:


    '''
    Initializes the game state:
    -----
    1. Loads players from given paths
    2. Creates map based on 'map_info' specification
        - Creates extra structures for optimization
    3. Initializes data structures storing frame information for replays


    '''
    def __init__(self, p1_path, p2_path, map_info):
        # initializes players
        self.p1_name = p1_path
        self.p2_name = p2_path

        self.PlayerDQ = Player
        try:
            self.MyPlayer1 = import_file("Player1", p1_path).MyPlayer
        except Exception as e:
            print(f"Issue with loading player 1")
            traceback.print_exc()
            self.MyPlayer1 = Player
        try:
            self.MyPlayer2 = import_file("Player2", p2_path).MyPlayer
        except Exception as e:
            print(f"Issue with loading player 2")
            traceback.print_exc()
            self.MyPlayer2 = Player

        self.p1_state = PlayerInfo(Team.RED)
        self.p2_state = PlayerInfo(Team.BLUE)

        for player, state in [(self.MyPlayer1, self.p1_state),(self.MyPlayer2, self.p2_state)]:
                try:
                    if os.name == "nt":
                        t0 = time.time()
                        if state == self.p1_state: self.p1 = player()
                        else: self.p2 = player()
                        t1 = time.time()
                        if t1 - t0 > GC.INIT_TIME_LIMIT:
                            raise TimeoutException
                    else:
                        with time_limit(GC.INIT_TIME_LIMIT):
                            if state == self.p1_state: self.p1 = player()
                            else: self.p2 = player()
                except TimeoutException as _:
                    state.time_bank.windows_warning()
                    print(f"[INIT TIMEOUT] {state.team}'s bot used >{GC.INIT_TIME_LIMIT} seconds to initialize; it will not play.")
                    if state == self.p1_state:
                        self.p1 = self.PlayerDQ()
                    else: self.p2 = self.PlayerDQ()
                except Exception as e:
                    print(f"[INIT TIMEOUT] {state.team}'s had an Exception")
                    traceback.print_exc()
                    if state == self.p1_state:
                        self.p1 = self.PlayerDQ()
                    else: self.p2 = self.PlayerDQ()


        self.winner = None

        # initializes map
        self.init_map(map_info)
        self.map_neighbors = self.init_neighbors()
        # map from populated tile (x, y) to all towers that can reach it
        self.populated_tiles = {loc: [] for loc in self.get_populated_tiles()}
        self.tower_diffs = MapUtil.get_diffs(GC.TOWER_RADIUS)

        # replay info
        self.frame_changes = []
        self.money_history = []
        self.utility_history = []
        self.time_bank_history = []
        self.prev_time_history = []
        self.active_history = []
        self.bid_history = []


    '''
        Creates the initial map, either random or based on custom map
    '''
    def init_map(self, map_info):

        '''
        Creates the initial map based on map_info if no custom map path was passed in
        -----
        1. Creates all tiles for the map
        2. Assigns population to map (while maintaining symmetry)
        3. Creates generators (with symmetry)
        4. Creates 'simple_map' (used in replays)
        -----
        Output:
        self.map = 2d array of tiles, where each tile contains (x, y, population, structure)
        self.generators = [list of generators for p1, list of generators for p2]
        self.simple_map = 2d array of tuples containing (passability, population) for each tile - used for replay information

        '''

        def init_random_map():
            random.seed(map_info.seed)

            self.map_name = f"random-{map_info.seed}"
            self.width = map_info.width
            self.height = map_info.height

            assert(GC.MIN_WIDTH <= self.width <= GC.MAX_WIDTH)
            assert(GC.MIN_HEIGHT <= self.height <= GC.MAX_HEIGHT)

            # Tile(self, x, y, population, structure, passability)
            self.map = [[Tile(i, j, 1, 0, None) for j in range(self.height)] for i in range(self.width)]

            # adds cities (tiles with population)
            for i in range(map_info.num_cities):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                x2, y2 = map_info.sym(x, y, self.width, self.height)
                pop = random.randrange(GC.MIN_POP, GC.MAX_POP)
                self.map[x][y].population = pop
                self.map[x2][y2].population = pop

            # adds generators (and maintains 'generators' structure)
            self.generators = [[], []]
            for i in range(map_info.num_generators):
                x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                x2, y2 = map_info.sym(x, y, self.width, self.height)
                self.map[x][y].structure = Structure(StructureType.GENERATOR, x, y, Team.RED)
                self.map[x2][y2].structure = Structure(StructureType.GENERATOR, x2, y2, Team.BLUE)
                self.generators[0] += [(x, y)]
                self.generators[1] += [(x2, y2)]

            # adds passability
            if map_info.passability:
                for height in map_info.passability:
                    for _ in range(map_info.passability[height]):
                        # choose random obstacle center
                        x1, y1 = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                        x2, y2 = map_info.sym(x1, y1, self.width, self.height)
                        print(f'INITIALIZING ONE WITH HEIGHT {height} at {x1,y1,x2,y2}')

                        # perform bfs around center
                        for x,y in [(x1,y1),(x2,y2)]:
                            for row in range(max(0,y-height),min(y+height,self.height)):
                                for col in range(max(0,x-height),min(x+height,self.width)):
                                    h = round(height - math.sqrt(MapUtil.dist(x,y,col,row)),1)
                                    self.map[col][row].passability = max(self.map[col][row].passability,h)
            else:
                # Original, independent random passability
                for x in range(self.width):
                    for y in range(self.height):
                        x2, y2 = map_info.sym(x, y, self.width, self.height)
                        pval = random.randrange(GC.MIN_PASS, GC.MAX_PASS)
                        self.map[x][y].passability = pval
                        self.map[x2][y2].passability = pval

        def init_custom_map():
            map_file = map_info.custom_map_path
            map_data = json.load(open(map_file))

            tile_info = map_data["tile_info"]
            map_gens = map_data["generators"]

            # Parse custom map file name to name??
            self.map_name = os.path.basename(map_info.custom_map_path)
            self.width = len(tile_info)
            self.height = len(tile_info[0])

            assert(GC.MIN_WIDTH <= self.width <= GC.MAX_WIDTH)
            assert(GC.MIN_HEIGHT <= self.height <= GC.MAX_HEIGHT)

            self.map = [[Tile(i, j, tile_info[i][j][0], tile_info[i][j][1], None) for j in range(self.height)] for i in range(self.width)]

            self.generators = [[], []]
            for t in [Team.RED, Team.BLUE]:
                for x,y in map_gens[t.value]:
                    self.map[x][y].structure = Structure(StructureType.GENERATOR, x, y, t)
                    self.generators[t.value] += [(x, y)]

        if map_info.custom_map_path:
            init_custom_map()
        else:
            init_random_map()

        self.simple_map = [[[tile.passability, tile.population] for tile in col] for col in self.map]

    '''
    Returns whether (i, j) is contained in the map
    '''
    def in_bounds(self, i, j):
        return 0 <= i < self.width and 0 <= j < self.height

    def adjacent(self, s):
        for nX, nY in self.map_neighbors[s.x][s.y]:
            nS = self.map[nX][nY].structure
            if nS and nS.team == s.team:
                return True
        return False

    '''
    Initialies a matrix of neighbors for each tile
    - Used in optimizing game simulation (when running BFS)
    '''
    def init_neighbors(self):
        neighbors = [[[] for j in range(self.height)] for i in range(self.width)]

        for i in range(self.width):
            for j in range(self.height):
                for di, dj in GC.MOVE_DIRS:
                    ni, nj = i + di, j + dj
                    if self.in_bounds(ni, nj):
                        neighbors[i][j] += [(ni, nj)]

        return neighbors

    '''
    Returns True if tile (x, y) contains a structure from 'team'
    '''
    def is_team_present(self, x, y, team):
        s = self.map[x][y].structure
        return s is not None and s.team == team

    '''
    Returns the team occupying tile (x, y)
    Returns None if no team is occupying it
    '''
    def get_team_present(self, x, y):
        s = self.map[x][y].structure
        if s is None:
            return None
        return s.team

    '''
    Returns a deep copy of the current map state
    '''
    def map_copy(self):
        return [[self.map[i][j]._copy() for j in range(self.height)] for i in range(self.width)]

    '''
    Returns a list of tiles that have a non-zero population
    '''
    def get_populated_tiles(self):
        tiles = []
        for i in range(self.width):
            for j in range(self.height):
                if self.map[i][j].population > 0:
                    tiles += [(i, j)]
        return tiles

    '''
    Runs the game
    '''
    def play_game(self):
        # save initial copy of money/utility history
        self.money_history += [(self.p1_state.money, self.p2_state.money)]
        self.utility_history += [(self.p1_state.utility, self.p2_state.utility)]
        self.time_bank_history += [(self.p1_state.time_bank.time_left, self.p2_state.time_bank.time_left)]
        self.prev_time_history += [(0, 0)]
        self.bid_history += [(0, 0, -1)]

        for turn_num in range(GC.NUM_ROUNDS):
            self.play_turn(turn_num)

        rScore, bScore = self.p1_state.utility, self.p2_state.utility
        if rScore == bScore:
            # number of towers
            numStructures = { t: {st: 0 for st in StructureType} for t in [Team.RED, Team.BLUE] }
            for x in range(self.width):
                for y in range(self.height):
                    s = self.map[x][y].structure
                    if s:
                        numStructures[s.team][s.type] += 1
                        # numStructures[s.team].get(s.type.get_id(), 0) + 1
            rScore, bScore = numStructures[Team.RED][StructureType.TOWER], numStructures[Team.BLUE][StructureType.TOWER]
        if rScore == bScore:
            # number of roads
            rScore, bScore = numStructures[Team.RED][StructureType.ROAD], numStructures[Team.BLUE][StructureType.ROAD]
        if rScore == bScore:
            # final money
            rScore, bScore = self.p1_state.money, self.p2_state.money
        if rScore == bScore:
            # everything failed (basically impossible lmao)
            rScore = self.p1_state.time_bank.time_left
            bScore = self.p2_state.time_bank.time_left

        self.winner = 1 if rScore > bScore else 2
        if self.winner == 1:
            print("Team.RED wins!")
        else:
            print("Team.BLUE wins!")

    '''
    Runs a single turn of the game
    ---
    1. Checks which towers are connected to generators
    1. Give each player resources
    2. Gets build instructions from each player
    3. Applies build instructions from each player
    4. Saves relevant game info into replay data structures

    -----
    Important changed variables:

    self.frame_changes = list of successful built structures by each player
        format: [structure1, structure2, ...]

    self.money_history = list of money for each player
        format: [(round_0_p1_money, round_0_p2_money), (round_1_p1_money, round_1_p2_money), ...]

    self.utility_history = list of utility (points) for each player
        format: [(round_0_p1_utility, round_0_p2_utility), ...]

    self.time_bank_history = list of time banks (seconds) for each player
            format: [(round_0_p1_time_bank, round_0_p2_time_bank), ...]

    -----
    Important note: when giving data to players, make a copy before giving to players, so they do not modify the actual game state
    '''
    def play_turn(self, turn_num):
        self.turn = turn_num

        # get player turns
        prev_time = []
        for player, state in [(self.p1, self.p1_state),(self.p2, self.p2_state)]:
            # reset build + bid
            player._bid = 0
            player._to_build = []

            # check for timeout end
            state.time_bank.set_turn(self.turn)
            state.time_bank.time_left += GC.TIME_INC
            if state.newly_active():
                print(f"[TIMEOUT END] {self.p1_state.team} resumes turns.")

            if state.active():
                # play turn
                try:
                    if os.name == "nt": # Windows
                        t0 = time.time()
                        player.play_turn(turn_num, self.map_copy(),state._copy())
                        t1 = time.time()
                        penalty = t1 - t0
                        if state.time_bank.time_left < 0:
                            raise TimeoutException
                    else:
                        t0 = time.time()
                        with time_limit(state.time_bank.time_left):
                            player.play_turn(turn_num, self.map_copy(),state._copy())
                        t1 = time.time()
                        penalty = t1 - t0
                    state.time_bank.time_left -= penalty
                except TimeoutException as _:
                    state.time_bank.windows_warning()
                    print(f"[{GC.TIMEOUT} ROUND TIMEOUT START] {state.team} emptied their time bank.")
                    state.time_bank.paused_at = turn_num
                    penalty = state.time_bank.time_left
                    state.time_bank.time_left = 0
                except Exception as e:
                    print("Exception from", state.team)
                    traceback.print_exc()
                    penalty = state.time_bank.time_left
                    state.time_bank.time_left = 0

                # apply time penalty
                prev_time.append(penalty)
            else:
                print(f"{state.team} turn skipped - in timeout")
        # update game state based on player actions
        # give build priority based on bid
        print(f'Round {turn_num} Bids: R : {self.p1._bid}, B : {self.p2._bid} - ', end='')
        if self.p1._bid > self.p2._bid or self.p1._bid == self.p2._bid and turn_num % 2 == 0: # alternate build priority (if two players try to build on the same tile)
            print(f"RED starts")
            bid_winner = 0
            p1_changes = self.try_builds(self.p1._to_build, self.p1_state, Team.RED)
            p2_changes = self.try_builds(self.p2._to_build, self.p2_state, Team.BLUE)
        else:
            print(f"BLUE starts")
            bid_winner = 1
            p2_changes = self.try_builds(self.p2._to_build, self.p2_state, Team.BLUE)
            p1_changes = self.try_builds(self.p1._to_build, self.p1_state, Team.RED)

        # update time bank history
        self.prev_time_history += [tuple(prev_time)]
        self.active_history += [(self.p1_state.active(), self.p2_state.active())]
        self.time_bank_history += [(self.p1_state.time_bank.time_left, self.p2_state.time_bank.time_left)]

        # update bid history
        self.bid_history += [(self.p1._bid, self.p2._bid, bid_winner)]

        # update money
        self.update_resources()
        self.money_history += [(self.p1_state.money, self.p2_state.money)]

        # calculate utility
        self.calculate_utility()
        self.utility_history += [(self.p1_state.utility, self.p2_state.utility)]

        # save replay info with changes
        self.frame_changes += [p1_changes + p2_changes]

    '''
    Helper method for running dfs - should be unnecessary / deprecated
    '''
    def run_tower_dfs(self, x, y, visited, cur_team):
        visited[x][y] = True
        for nx, ny in self.map_neighbors[x][y]:
            if self.is_team_present(nx, ny, cur_team):
                if not visited[nx][ny]:
                    self.run_tower_dfs(x, y, visited, cur_team)


    '''
    Updates resources of players
    -----
    1. Gives each player base income
    2. Gives players money/utility score based on tower income
    -----
    Output:
    self.pX_state = PlayerInfo() object for pX

    '''
    def update_resources(self):
        self.p1_state.money += GC.PLAYER_BASE_INCOME
        self.p2_state.money += GC.PLAYER_BASE_INCOME

        # TODO: test alternative money systems
        for (x, y), towers in self.populated_tiles.items():
            tile = self.map[x][y]
            r, b = False, False
            for tow in towers:
                if tow.team == Team.RED: r = True
                elif tow.team == Team.BLUE: b = True
            # toggle based allocation
            if r and b:
                self.p1_state.money += tile.population / 2
                self.p2_state.money += tile.population / 2
            elif r and not b:
                self.p1_state.money += tile.population
            elif not r and b:
                self.p2_state.money += tile.population

        # round money to the nearest 0.1 at end of each round
        for p_state in [self.p1_state, self.p2_state]:
            p_state.money = round(p_state.money, 1)

    '''
    Calculates utility for each team
    '''
    def calculate_utility(self):
        self.p1_state.utility = 0
        self.p2_state.utility = 0
        for (x, y), towers in self.populated_tiles.items():
            tile = self.map[x][y]
            r, b = False, False
            for tow in towers:
                if tow.team == Team.RED: r = True
                elif tow.team == Team.BLUE: b = True
            # toggle based allocation
            if r and b:
                self.p1_state.utility += tile.population / 2
                self.p2_state.utility += tile.population / 2
            elif r and not b:
                self.p1_state.utility += tile.population
            elif not r and b:
                self.p2_state.utility += tile.population

        for p_state in [self.p1_state, self.p2_state]:
            p_state.utility = round(p_state.utility, 1)



    '''
    Attempts to build structure instructions for a given player/team
    -----
    1. Iterates through each build request
        - checks if they can afford it and if the tile can be built on
        - if valid, then adds structure to map and subtracts costs from player resources
    -----
    Output:
    Adds built structures to 'self.map'
    Returns a list of successfully built structures
        Format: [structure1, structure2, ...]
    '''
    def try_builds(self, builds, p_state, team):
        new_builds = []
        structures = [Structure(struct_type, x, y, team) for (struct_type, x, y) in builds]
        for s in structures:
            # check if can build
            s_cost = s.get_cost(self.map[s.x][s.y].passability)
            if self.can_build(s) and p_state.money >= s_cost:
                p_state.money -= s_cost
                self.map[s.x][s.y].structure = s
                new_builds += [s]
                # add towers to populated tiles (for our updates on our side)
                if s.type == StructureType.TOWER:
                    for (dx, dy) in self.tower_diffs:
                        nx, ny = s.x + dx, s.y + dy
                        if (nx, ny) in self.populated_tiles:
                            self.populated_tiles[(nx, ny)] += [s]

        return new_builds


    '''
    Returns whether or not a given structure can be built
    -----
    Checks if position in bounds, blocked by other buildings
    '''
    # potential todo: distance requirement from other towers
    def can_build(self, s):
        # not in bounds or not buildable
        # check if adjacent to other tiles

        if not self.in_bounds(s.x, s.y) or not self.adjacent(s) or not s.type.get_can_build():
            return False
        return self.map[s.x][s.y].structure is None

    '''
    Saves replay information to a file (in JSON format)
    '''
    def save_replay(self, save_dir, save_file_name):
        random.seed()
        id = random.randint(1e6, 1e7 - 1)

        self.metadata = {
            "p1_name": self.p1_name,
            "p2_name": self.p2_name,
            "map_name": self.map_name,
            "num_frames": GC.NUM_ROUNDS,
            "version": "1.0.0"
        }

        structure_type_ids = [(st.value.id, st.value.name) for st in StructureType]

        game_constants = {}
        for k, v in GC.__dict__.items():
            if k.isupper():
                game_constants[k] = v

        if save_file_name is None:
            save_file_name = f"replay-{id}"

        save_file_path = f"{save_dir}/{save_file_name}.awap22r"

        with open(save_file_path, "w") as f:
            obj = {
                "metadata": self.metadata,
                "map": self.simple_map,
                "generators": self.generators,
                "game_constants": game_constants,
                "frame_changes": self.frame_changes,
                "money_history": self.money_history,
                "utility_history": self.utility_history,
                "time_bank_history": self.time_bank_history,
                "prev_time_history": self.prev_time_history,
                "active_history": self.active_history,
                "bid_history": self.bid_history,
                "structure_type_ids": structure_type_ids,
                "winner": self.winner
            }
            json.dump(obj, f, cls=CustomEncoder)

        print(f"\nSaved replay file in {save_file_path}")
        print(f"Match ended: '{self.p1_name}' vs '{self.p2_name}' on '{self.map_name}'")
