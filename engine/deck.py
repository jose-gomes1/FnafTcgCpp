"""
FNAF TCG - Deck Management
"""
import random
from engine.cards import AnimatronicCard, SupportCard, ElectricityCard, ANIMATRONICS, SUPPORTS

MAX_DECK_SIZE = 30
MIN_DECK_SIZE = 30
MAX_COPIES_PER_NAME = 5
MAX_ACTIVE = 4


class DeckError(Exception):
    pass


def validate_deck(deck_list: list) -> tuple[bool, list[str]]:
    """Validate a deck. Returns (valid, list_of_errors)."""
    errors = []
    if len(deck_list) < MIN_DECK_SIZE:
        errors.append(f"Deck tem {len(deck_list)} cartas, mínimo é {MIN_DECK_SIZE}.")

    has_animatronic = any(isinstance(c, AnimatronicCard) for c in deck_list)
    has_electricity = any(isinstance(c, ElectricityCard) for c in deck_list)

    if not has_animatronic:
        errors.append("Deck precisa de pelo menos 1 animatronic.")
    if not has_electricity:
        errors.append("Deck precisa de pelo menos 1 eletricidade.")

    # Count copies per name
    name_counts: dict[str, int] = {}
    for card in deck_list:
        if isinstance(card, AnimatronicCard):
            name_counts[card.name] = name_counts.get(card.name, 0) + 1
    for name, count in name_counts.items():
        if count > MAX_COPIES_PER_NAME:
            errors.append(f"'{name}' tem {count} cópias (máximo: {MAX_COPIES_PER_NAME}).")

    return len(errors) == 0, errors


def build_deck_from_list(deck_spec: list[tuple[int, str]]) -> list:
    """
    Build deck from list of (quantity, card_name).
    'Eletricidade' is a special keyword.
    Returns shuffled deck list.
    """
    deck = []
    for qty, name in deck_spec:
        for _ in range(qty):
            if name == "Eletricidade":
                deck.append(ElectricityCard())
            elif name in ANIMATRONICS:
                deck.append(ANIMATRONICS[name].clone())
            elif name in SUPPORTS:
                deck.append(SupportCard(SUPPORTS[name].name, SUPPORTS[name].description))
            else:
                raise DeckError(f"Carta desconhecida: '{name}'")
    return deck


DEFAULT_DECK_SPEC = [
    (3, "Withered Freddy"),
    (2, "Shadow Freddy"),
    (2, "Jack-O-Bonnie"),
    (2, "Jack-O-Chica"),
    (3, "Freddy Mask"),
    (3, "William Afton"),
    (3, "Power Drain"),
    (12, "Eletricidade"),
]


def get_default_deck() -> list:
    deck = build_deck_from_list(DEFAULT_DECK_SPEC)
    random.shuffle(deck)
    return deck
