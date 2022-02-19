import json
import argparse
import os
import sys

from src.structure import *
from src.game import *
from src.custom_json import *
from src.game_constants import GameConstants as GC

dir_path = "./"
#dir_path = "./cell-towers"

if __name__ == "__main__":

    save_path = os.path.join(dir_path, "./replays")

    # Exact format of a custom map file:
    # .json file with "info", "generators1", and "generators2" entries
    # info is a 2d array of (passability, population) tuples for each tile location
    # generators1 is a 1d array of (x,y) coordinates if there exist a generator for team 1 at (x,y)
    # generators2 is a 1d array of (x,y) coordinates if there exist a generator for team 2 at (x,y)

    # load game settings from json file
    with open(os.path.join(dir_path, "./game_settings.json"), "r") as f:
        game_settings = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--map_name", help="Run with custom map (./maps/map-CUSTOM_MAP_NAME.awap22m).", default=None)
    parser.add_argument("-p1","--p1_bot_name", help="Player 1 bot name (./bots/P1_BOT_NAME.py).", default=None)
    parser.add_argument("-p2","--p2_bot_name", help="Player 2 bot name (./bots/P2_BOT_NAME.py).", default=None)
    parser.add_argument("-replay","--replay_file_name", help="Replay file name (./replays/{REPLAY_NAME}.awap22r)", default=None)
    args = parser.parse_args()

    if args.map_name:
        game_settings["map"] = args.map_name
    if args.p1_bot_name:
        game_settings["p1"] = args.p1_bot_name
    if args.p2_bot_name:
        game_settings["p2"] = args.p2_bot_name
    if args.replay_file_name:
        game_settings["replay"] = args.replay_file_name

    # if args.custom_map_name:
    map_path = os.path.join(dir_path, f'./maps/{game_settings["map"]}.awap22m')
    if os.path.isfile(map_path):
        map_settings = MapInfo(custom_map_path=map_path)
    else:
        print(f"Map {map_path} could not be found. Run python3 main.py -h for help. Exiting")
        exit(0)

    bot_folder = os.path.join(dir_path, "./bots")
    bot1_path = f"{bot_folder}/{game_settings['p1']}.py"
    bot2_path = f"{bot_folder}/{game_settings['p2']}.py"

    game = Game(bot1_path, bot2_path, map_settings)

    game.play_game()

    game.save_replay(save_path, game_settings["replay"])
