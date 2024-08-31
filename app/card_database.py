from pathlib import Path
import os
import json
from typing import Dict, List, Any

REQUIRED_DECK_COUNT = 50
REQUIRED_CHEER_COUNT = 20
MAX_ANY_CARD_COUNT = 4

ALLOWED_DECK_TYPES = [
    "holomem_debut",
    "holomem_bloom",
    "holomem_spot",
]

class CardDatabase:
    def __init__(self):
        self.all_cards = []

        # The card_definitions.json file is in root\decks\card_definitions.json
        # This file is in root\app
        # Build the file path from this file's location.
        card_definitions_path = os.path.join(Path(__file__).parent.parent, "decks", "card_definitions.json")

        self.load_cards(card_definitions_path)

    def load_cards(self, path):
        # Load all the cards from the definitions file.
        with open(path, "r") as f:
            card_data = json.load(f)
            self.all_cards = card_data

    def get_card_by_id(self, card_id):
        for card in self.all_cards:
            if card["id"] == card_id:
                return card
        return None

    def validate_deck(self, oshi_id : str, deck : Dict[str, int], cheer_deck: Dict[str, int]):

        # Validate the oshi ID is an existing oshi.
        oshi_card = self.get_card_by_id(oshi_id)
        if not oshi_card or oshi_card["card_type"] != "oshi":
            return False

        # Check the deck
        deck_count = 0
        for card_id, count in deck.items():
            if count > MAX_ANY_CARD_COUNT:
                return False

            deck_count += count
            deck_card = self.get_card_by_id(card_id)
            if not deck_card or deck_card["card_type"] not in ALLOWED_DECK_TYPES:
                return False

        if deck_count != REQUIRED_DECK_COUNT:
            return False

        # Check the cheer deck
        cheer_deck_count = 0
        for card_id, count in cheer_deck.items():
            cheer_deck_count += count
            cheer_deck_card = self.get_card_by_id(card_id)
            if not cheer_deck_card or cheer_deck_card["card_type"] != "cheer":
                return False

        if cheer_deck_count != REQUIRED_CHEER_COUNT:
            return False

        return True