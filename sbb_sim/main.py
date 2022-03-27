from game import Game
from minion import MinionMediator, MinionDetails, MINION_DETAILS

def play():
    p1 = MinionMediator([
        (MinionDetails(**MINION_DETAILS['Mad Mim']), 4), 
        (MinionDetails(**MINION_DETAILS['Rainbow Unicorn']), 0), 
        (MinionDetails(**MINION_DETAILS['Black Cat']), 1),
        (MinionDetails(**MINION_DETAILS['Happy Little Tree']), 3)
    ])
    p2 = MinionMediator([
            (MinionDetails(**MINION_DETAILS['Mad Mim']), 4), 
            (MinionDetails(**MINION_DETAILS['Rainbow Unicorn']), 0), 
            (MinionDetails(**MINION_DETAILS['Black Cat']), 1),
            (MinionDetails(**MINION_DETAILS['Happy Little Tree']), 3)
        ])
    game = Game(p1, p2)
    return game.run()

def main():
    TRIALS = 1000
    print(sum([play() for _ in range(TRIALS)]) / TRIALS)


if __name__ == "__main__":
    main()