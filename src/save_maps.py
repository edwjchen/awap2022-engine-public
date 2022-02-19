import json
import os
import argparse

# TEMPORARY: being used to make a sample map in the correct format
# to test the code used for reading custom maps

replay_path = "../replays"
map_path = "../maps"

def save_map(replay_file, seed):
    replay_data = None
    # load simple map entry from replay json file
    try:
        with open(replay_file) as f:
            replay_data = json.load(f)
    except FileNotFoundError:
        print(f"{replay_file} does not exist")
        return

    simple_map = replay_data["map"]

    rows, cols = len(simple_map[0]), len(simple_map)
    tile_info = [[0 for _ in range(cols)] for _ in range(rows)]
    generators = [[], []]

    # iterate through simple map to get info
    for i in range(cols):
        for j in range(rows):
            passability, population, structure = simple_map[i][j]
            tile_info[i][j] = (passability, population)

            # ref structure.py: code for generator type is 0
            if structure and structure[3] == 0:
                    generators[structure[2]] += [(i,j)]

    # save into map json file
        with open(f"{map_path}/map-{seed}.awap22m", "w") as f:
            obj = {
                "tile_info": tile_info,
                "generators": generators,
            }
            json.dump(obj, f)
    print(f'Saved map of {replay_file} into {map_path}/map-{seed}.awap22m')


parser = argparse.ArgumentParser()
parser.add_argument("-r","--replay_seed", help="specify a map to save (path = ../replays/replay-REPLAY_SEED.awap22r)", default=None)
args = parser.parse_args()

if args.replay_seed:
    save_map(f'{replay_path}/replay-{args.replay_seed}.awap22r', args.replay_seed)
else:
    print(f"No replay file specified (run python3 save_maps.py -h for info) - saving all maps from {replay_path}")
    replays = list(set(os.listdir(replay_path)) - set(['.gitignore']))
    for replay_file in replays:
        seed = replay_file[7:14]
        save_map(f'{replay_path}/{replay_file}', seed)
