from typing import List
from app.card_database import CardDatabase
import random

UNKNOWN_CARD_ID = "HIDDEN"

class PlayerState:
    def __init__(self):
        self.life = 7
        self.deck = []
        self.hand = []

class GameEngine:
    def __init__(self,
        card_db:CardDatabase,
        player_ids:List[str],
        game_type : str,
    ):
        self.card_db = card_db

        self.seed = random.randint(0, 2**32 - 1)
        self.game_type = game_type
        self.player_ids = player_ids
        self.player_states = [PlayerState() for _ in player_ids]

    def player_state(self, player_id:str):
        return self.player_states[self.player_ids.index(player_id)]

    def begin_game(self):
        events = []

        # Set the seed.
        self.random_gen = random.Random(self.seed)

        # Decide first player.
        first_player = self.random_gen.choice(self._state["player_ids"])


        return events

    def handle_game_message(self, player_id:str, action_type:str, action_data: dict):
        match action_type:
            case "deal_damage":
                return self._handle_deal_damage(player_id, action_data)
            case _:
                return []

    def _handle_deal_damage(self, player_id:str, action_data:dict):
        events = []

        damage = action_data["damage"]
        target_id = action_data["target_id"]

        target = self.player_state(target_id)
        original_life = target.life
        target.life -= damage
        new_life = target.life

        for player in self.player_ids:
            events.append({
                "event_player_id": player,
                "event_type": "damage_taken",
                "dealing_player": player_id,
                "target_player": target_id,
                "damage": damage,
                "original_life": original_life,
                "new_life": new_life,
            })

        return events