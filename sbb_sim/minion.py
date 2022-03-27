from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple
from typing import List, Tuple, Optional, Callable
import random
import json

NUM_POSITIONS = 7
FRONT_ROW = (0, 1, 2, 3)
BACK_ROW = (4, 5, 6)
IN_FRONT_OF = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [0, 1],
    5: [1, 2],
    6: [2, 3]
}
with open('sbb_sim/data/minions.json') as f:
    MINION_DETAILS = json.loads(f.read())

@dataclass
class Bonus:
    attack: int
    health: int

@dataclass
class AttackDetails:
    attack: int
    flying: bool = False
    ranged: bool = False

@dataclass
class MinionDetails:
    """Minion characteristics and stats"""
    name: str
    base_attack: int
    base_health: int
    alignment: str
    types: List[str]
    level: int
    upgraded: bool = False
    ranged: bool = False
    flying: bool = False
    slay: bool = False

class Minion:

    def __init__(self, details: MinionDetails, position: int, mediator: MinionMediator):
        self.attack = details.base_attack
        self.health = details.base_health
        self.details = details
        self.position = position
        self.mediator = mediator
    
    def support(self) -> Tuple[Bonus, Callable[["Minion"], bool]]:
        return (0, 0), lambda x: False 

    def apply_bonus(self, bonus: Bonus) -> None:
        self.attack += bonus.attack
        self.health += bonus.health

    def take_damage(self, damage: int) -> None:
        self.health -= damage
        if self.health < 0:
            self.mediator.kill_minion(self.position)

    def on_death(self) -> Callable:
        return lambda: None

    @property
    def can_attack(self) -> bool:
        return self.attack > 0

    def __repr__(self) -> str:
        return f"{self.details.name} in position {self.position} with {self.attack} attack and {self.health} health"

class MinionMediator:

    def __init__(self, minions: List[Tuple[MinionDetails, int]]):
        self.minions = {}
        for details, position in minions:
            self.add_minion(details.name, details, position)
        self.last_attacker = None
        self.apply_supports()

    def add_minion(self, name: str, details: MinionDetails, position: int) -> None:
        if position not in self.minions:
            self.minions[position] = minion_classes[name](details=details, position=position, mediator=self)

    def _remove_minion(self, position: int) -> None:
        del self.minions[position]

    def kill_minion(self, position: int) -> None:
        on_death = self.minions[position].on_death()
        self._remove_minion(position)
        on_death() # This will later be placed on a stack

    def receive_attack(self, attack_details: AttackDetails) -> int:
        """Accept incoming attack, and return the damage to be dealt back"""
        assert self.has_minions
        defender = self._get_defender(attack_details)
        defender.take_damage(attack_details.attack)
        return defender.attack if attack_details.ranged else 0

    def _get_defender(self, attack: AttackDetails) -> Minion:
        front = [minion for minion in self.minions.values() if minion.position in FRONT_ROW]
        back = [minion for minion in self.minions.values() if minion.position in BACK_ROW]
        if len(front) == 0:
            return random.choice(back)
        elif len(back) == 0 or not attack.flying:
            return random.choice(front)
        else: # attack.flying
            return random.choice(back)
        
    def _attack_priority(self, minion: Minion) -> int:
        """Integer value to determine attacking order, lowest value has highest priority"""
        if minion is self.last_attacker:
            return NUM_POSITIONS * 3 # ensure lowest priority 
        elif minion.position >= (self.last_attacker.position if self.last_attacker else 0):
            return minion.position
        else:
            return minion.position + NUM_POSITIONS 

    @property
    def has_attacker(self) -> bool:
        return any(m.can_attack for m in self.minions.values())

    def _get_attacker(self) -> Minion:
        for minion in sorted(self.minions.values(), key=self._attack_priority):
            if minion.can_attack:
                return minion
        else:
            raise RuntimeError("Tried to get attacker but none available.")

    def attack(self, opponent: MinionMediator) -> None:
        if not self.has_attacker:
            return
        attacker = self._get_attacker()
        attack_details = AttackDetails(attack=attacker.attack, ranged=attacker.details.ranged, flying=attacker.details.flying)
        damage_taken = opponent.receive_attack(attack_details)
        attacker.take_damage(damage_taken)
        self.last_attacker = attacker

    def apply_supports(self) -> None:
        for supporter in self.minions.values():
            bonus, criteria = supporter.support()
            for target in filter(criteria, self.minions.values()):
                target.apply_bonus(bonus)

    @property
    def has_minions(self) -> bool:
        return len(self.minions) > 0


minion_classes = {}

def _register(name):
    def wrapper(cls):
        minion_classes[name] = cls
        return cls
    return wrapper

@_register(name='Mad Mim')
class MadMim(Minion):

    def support(self) -> Tuple[Bonus, Callable[[Minion], bool]]:
        return Bonus(3, 0), lambda x: x.position in IN_FRONT_OF[self.position]

@_register(name='Rainbow Unicorn')
class RainbowUnicorn(Minion):

    def support(self) -> Tuple[Bonus, Callable[[Minion], bool]]:
        return Bonus(0, 1), lambda x: x.details.alignment == 'Good' and x is not self

@_register(name='Black Cat')
class BlackCat(Minion):

    def on_death(self) -> None:
        return lambda: self.mediator.add_minion('Cat', details=MinionDetails(**MINION_DETAILS['Cat']), position=self.position)

@_register(name='Cat')
class Cat(Minion):
    pass

@_register(name='Happy Little Tree')
class HappyLittleTree(Minion):
    pass