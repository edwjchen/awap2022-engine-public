import json
import sys

with open(f"../maps/{sys.argv[1]}.awap22m") as f:
    data = json.load(f)

tiles = data["tile_info"]
print(tiles[0][0])

factor = float(sys.argv[2])
for x in range(len(tiles)):
    for y in range(len(tiles[0])):
        tiles[x][y][0] *= factor

print(tiles[0][0])

with open(f"../maps/{sys.argv[1]}_scaled.awap22m", "w") as f:
    json.dump(data, f)
