g:
	python3 run_game.py -m flappy -p1 random_bot -p2 greedy_bot

test:
	python3 run_game.py -m flappy -p1 random_bot -p2 test_bot

mk: 
	python3 run_game.py -m flappy -p1 random_bot -p2 mingkuan_bot


