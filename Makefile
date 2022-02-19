g:
	python3 run_game.py -m flappy -p1 random_bot -p2 greedy_bot

test:
	python3 run_game.py -m flappy -p1 random_bot -p2 test_bot

mk: 
	python3 run_game.py -m flappy -p1 random_bot -p2 mingkuan_bot

mk2:
	python3 run_game.py -m flappy -p1 mingkuan_bot -p2 mingkuan_bot

block:
	python3 run_game.py -m island -p1 blocking_bot -p2 mingkuan_bot

