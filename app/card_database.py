from pathlib import Path
import os
import json
from typing import Dict, List, Any
from copy import deepcopy
import logging
logger = logging.getLogger(__name__)

REQUIRED_DECK_COUNT = 50
REQUIRED_CHEER_COUNT = 20
MAX_ANY_CARD_COUNT = 4

ALLOWED_DECK_TYPES = [
    "holomem_debut",
    "holomem_bloom",
    "holomem_spot",
    "support",
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
            json_data = json.load(f)
            card_data = []
            for card in json_data:
                card_data.append(card)
                # populate the alternates based on the original card
                for rarity in card.get("alternates", []):
                    alt_card = deepcopy(card)
                    alt_id = alt_card["alt_id"]
                    alt_card["alt_id"] = alt_id
                    alt_card["card_id"] = alt_id + "_" + rarity.upper()
                    alt_card["rarity"] = rarity
                    del alt_card["alternates"]
                    card_data.append(alt_card)
            self.all_cards = card_data

    def get_card_by_id(self, card_id):
        for card in self.all_cards:
            if card["card_id"] == card_id:
                return deepcopy(card)
        return None

    def validate_deck(self, oshi_id : str, deck : Dict[str, int], cheer_deck: Dict[str, int]):

        # Validate the oshi ID is an existing oshi.
        oshi_card = self.get_card_by_id(oshi_id)
        if not oshi_card or oshi_card["card_type"] != "oshi":
            logger.info("--Deck Invalid: Oshi")
            return False

        # Check the deck
        deck_count = 0
        alt_copies = {}
        for card_id, count in deck.items():
            deck_card = self.get_card_by_id(card_id)
            if not deck_card or deck_card["card_type"] not in ALLOWED_DECK_TYPES:
                if not deck_card:
                    logger.info("--Deck Invalid: Card not found %s" % card_id)
                elif deck_card["card_type"]:
                    logger.info("--Deck Invalid: %s not allowed" % deck_card["card_type"])
                else:
                    logger.info("--Deck Invalid: Card Type None")
                return False

            # Can only have 4 of any card, unless special_deck_limit is set.
            deck_limit = MAX_ANY_CARD_COUNT
            if "special_deck_limit" in deck_card:
                deck_limit = deck_card["special_deck_limit"]

            card_copies = 0
            if "alt_id" in deck_card:
                alt_id = deck_card["alt_id"]
                if alt_id in alt_copies:
                    card_copies = alt_copies[alt_id]
                else:
                    for key in deck.keys():
                        if key.startswith(alt_id):
                            card_copies += deck[key]
                    alt_copies[alt_id] = card_copies
            else:
                card_copies = count

            if card_copies > deck_limit:
                logger.info("--Deck Invalid: Too many cards")
                return False

            deck_count += count

        if deck_count != REQUIRED_DECK_COUNT:
            logger.info("--Deck Invalid: Not enough cards")
            return False

        # Check the cheer deck
        cheer_deck_count = 0
        for card_id, count in cheer_deck.items():
            cheer_deck_count += count
            cheer_deck_card = self.get_card_by_id(card_id)
            if not cheer_deck_card or cheer_deck_card["card_type"] != "cheer":
                logger.info("--Deck Invalid: Cheer deck wrong")
                return False

        if cheer_deck_count != REQUIRED_CHEER_COUNT:
            logger.info("--Deck Invalid: Cheer deck count wrong")
            return False

        return True