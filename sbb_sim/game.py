import random
from itertools import cycle

from minion import MinionMediator


class Game:

    def __init__(self, p1: MinionMediator, p2: MinionMediator):
        self.p1 = p1
        self.p2 = p2
        self.turn_sequence = cycle([(self.p1, self.p2), (self.p2, self.p1)]) 
        if random.choice([True, False]):
            next(self.turn_sequence)

    def run(self) -> float:
        for attacker, opponent in self.turn_sequence:
            if self.is_terminal():
                return self.game_result()
            attacker.attack(opponent)

    def is_terminal(self) -> bool:
        return (not self.p1.has_minions) or (not self.p2.has_minions) or (not self.p1.has_attacker and not self.p2.has_attacker)

    def game_result(self) -> float:
        if (not self.p1.has_minions) and (not self.p2.has_minions):
            return 0.5 # draw
        elif not self.p1.has_minions:
            return 0
        elif not self.p2.has_minions:
            return 1
        elif not self.p1.has_attacker and not self.p2.has_attacker:
            return 0.5 # draw
        else:
            raise RuntimeError("Game hasn't ended!")