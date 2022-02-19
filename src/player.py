import os

from .structure import *
from .game_constants import GameConstants as GC

from enum import Enum
from abc import ABC, abstractmethod

class Team(Enum):
    RED = 0
    BLUE = 1
    NEUTRAL = 2

class TimeBank:
    def __init__(self, paused_at=None, turn_num=0,
        time_left=GC.BASE_TIME):
        self.time_left = time_left
        self.paused_at = paused_at
        self.turn_num = turn_num

    def set_turn(self, turn_num):
        self.turn_num = turn_num

    def newly_active(self):
        return self.paused_at != None and self.turn_num - self.paused_at == GC.TIMEOUT

    def active(self):
        return self.paused_at == None or self.turn_num - self.paused_at >= GC.TIMEOUT

    def windows_warning(self):
        if os.name == "nt":
            print(f"[WINDOWS WARNING] Bot just exceeded a time limit on your \
                function call. Our server will terminate it early, possibly with \
                different effects than on your machine.")
    
    def __str__(self):
        return f"time_left: {round(self.time_left,4)}, paused_at: {self.paused_at}"

    def _copy(self):
        return TimeBank(self.paused_at, self.turn_num, self.time_left)

class PlayerInfo:
    def __init__(self, team, money=GC.PLAYER_STARTING_MONEY, utility=0.0,
        time_bank = None, dq=False):
        self.team = team
        self.money = money
        self.utility = utility
        self.bid = 0
        if time_bank: self.time_bank = time_bank
        else: self.time_bank = TimeBank()
        self.dq = dq

    def newly_active(self):
        return (not self.dq) and self.time_bank.newly_active()
    
    def active(self):
        return (not self.dq) and self.time_bank.active()

    def __str__(self):
        return f"[T: {self.team}, M: {self.money}, U: {self.utility}]"

    def _copy(self):
        return PlayerInfo(self.team, self.money, self.utility, self.time_bank)


class Player:

    def __init__(self):
        print("DQ Bot - This bot will not play.")
        self._bid = -1

    def play_turn(self, turn_num, map, player_info):
        print("Default Bot [disqualified] - turn played.")
        self._bid = -1

    def set_bid(self, bid):
        self._bid = bid

    def build(self, struct_type, x, y):
        self._to_build += [(struct_type, x, y)]
