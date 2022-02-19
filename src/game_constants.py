class GameConstants:

    MIN_WIDTH = 32
    MIN_HEIGHT = 32
    MAX_WIDTH = 64
    MAX_HEIGHT = 64
    MOVE_DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    MIN_POP = 0
    MAX_POP = 10

    MIN_PASS = 1
    MAX_PASS = 10

    PLAYER_STARTING_MONEY = 250
    PLAYER_BASE_INCOME = 100

    NUM_ROUNDS = 250

    TOWER_RADIUS = 2

    INIT_TIME_LIMIT = 10
    BASE_TIME = 30
    TIME_INC = 0.25 # 0.25
    TIMEOUT = 5 # number of rounds skipped for timeout