g:
	python3 run_game.py -m flappy -p1 random_bot -p2 greedy_bot

test:
	python3 run_game.py -m flappy -p1 random_bot -p2 test_bot

mk: 
	python3 run_game.py -m flappy -p1 random_bot -p2 mingkuan_bot

mk2:
	python3 run_game.py -m flappy -p1 mingkuan_bot -p2 mingkuan_bot

block:
	python3 run_game.py -m island -p1 blocking_bot -p2 merged_bot

block2:
	python3 run_game.py -m island -p2 blocking_bot -p1 merged_bot

merge:
	python3 run_game.py -m ridges -p2 blocking_bot -p1 merged_bot

merge2:
	python3 run_game.py -m ridges -p1 blocking_bot -p2 merged_bot

merge3:
	python3 run_game.py -m island -p1 merged_bot -p2 random_bot
