# AWAP 2022 Game Engine

This is the AWAP 2022 game engine.

Sample bots can be found in the `bots/` folder. Competitors should also develop their bots in this folder.

Maps should be placed in the `maps/` folder.

### Requirements
* [Python 3](https://www.python.org/downloads/) (Developed/tested in **3.8.9**, other versions probably work)

## Project Structure
* `README.md` - This file
* `run_game.py` - Runs a game between two players on a map
* `game_settings.json` - Contains game settings used in `run_game.py` (specifies players and map)
* `bots/` - Contains player source code
* `maps/` - Contains maps (download your custom maps to here)
* `replays/` - Contains match replays
* `src/` - Contains the engine source code


## How-to:

### Download
* `git clone https://github.com/rzhan11/awap2022-engine-public.git` - Downloads the repo

### Run a match
* `cd` into this repo
* `python3 run_game.py` - Runs the game
    * Specify players/maps by modifying `game_settings.json`
    * Games can also be run with CLI arguments (`python3 run_game.py -h` for details)
* Match replay files are saved in the `replays/` folder

### View match replay
* Open the viewer ([on browser](http://awap2022.com:8080/viewer) or [on local](https://github.com/rzhan11/awap2022-viewer.git))
* Upload a replay file (match replays are saved in the `replays/` folder)
