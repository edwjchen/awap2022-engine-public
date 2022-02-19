import sys

import random
import time

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

class MyPlayer(Player):

    def __init__(self):
        print("Init")
        self.turn = 0

        return


    def play_turn(self, turn_num, map, player_info):
        start_time = time.time()
        last_print = 0
        while True:
            if time.time() - last_print > 1:
                print(time.time() - start_time)
                last_print = time.time()

        return
