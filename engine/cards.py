"""
FNAF TCG - Card Data Models
"""
import csv
import os
from dataclasses import dataclass, field
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


@dataclass
class Attack:
    name: str
    attack_type: str  # Single, Multi, Heal, Stall
    cost: int
    value: int  # damage / heal amount / stall turns


@dataclass
class AnimatronicCard:
    name: str
    max_hp: int
    max_electricity: int
    attacks: list[Attack]

    # runtime state
    current_hp: int = 0
    electricity: int = 0
    stalled_turns: int = 0  # turns unable to attack

    def __post_init__(self):
        self.current_hp = self.max_hp

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def can_attack(self) -> bool:
        return self.stalled_turns <= 0

    def take_damage(self, dmg: int):
        self.current_hp = max(0, self.current_hp - dmg)

    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def attach_electricity(self) -> bool:
        if self.electricity < self.max_electricity:
            self.electricity += 1
            return True
        return False

    def spend_electricity(self, amount: int) -> bool:
        if self.electricity >= amount:
            self.electricity -= amount
            return True
        return False

    def tick_stall(self):
        if self.stalled_turns > 0:
            self.stalled_turns -= 1

    def clone(self) -> "AnimatronicCard":
        a = AnimatronicCard(
            name=self.name,
            max_hp=self.max_hp,
            max_electricity=self.max_electricity,
            attacks=self.attacks,
        )
        return a

    def __str__(self):
        stall_str = f" [STALLED {self.stalled_turns}t]" if self.stalled_turns > 0 else ""
        return (
            f"{self.name} | HP: {self.current_hp}/{self.max_hp} "
            f"| ⚡{self.electricity}/{self.max_electricity}{stall_str}"
        )


@dataclass
class SupportCard:
    name: str
    description: str

    def __str__(self):
        return f"[Support] {self.name}: {self.description}"


class ElectricityCard:
    name = "Eletricidade"

    def __str__(self):
        return "⚡ Eletricidade"


def load_animatronics() -> dict[str, AnimatronicCard]:
    path = os.path.join(DATA_DIR, "animatronics.csv")
    animatronics = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            attacks = []
            for i in (1, 2):
                a_name = row.get(f"Attack{i}Name", "").strip()
                if a_name:
                    attacks.append(
                        Attack(
                            name=a_name,
                            attack_type=row[f"Attack{i}Type"].strip(),
                            cost=int(row[f"Attack{i}Cost"]),
                            value=int(row[f"Attack{i}Value"]) if row[f"Attack{i}Value"] else 0,
                        )
                    )
            card = AnimatronicCard(
                name=row["Name"].strip(),
                max_hp=int(row["HP"]),
                max_electricity=int(row["MaxElectricity"]),
                attacks=attacks,
            )
            animatronics[card.name] = card
    return animatronics


def load_supports() -> dict[str, SupportCard]:
    path = os.path.join(DATA_DIR, "supports.csv")
    supports = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            card = SupportCard(
                name=row["Name"].strip(),
                description=row["Description"].strip(),
            )
            supports[card.name] = card
    return supports


# Singletons for reference
ANIMATRONICS = load_animatronics()
SUPPORTS = load_supports()
