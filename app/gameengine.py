from typing import List

UNKNOWN_CARD_ID = "HIDDEN"

class PlayerState:
    def __init__(self):
        self.life = 7
        self.deck = []
        self.hand = []

    def get_public_state(self):
        return {
            "life": self.life,
            "cards_in_deck": len(self.deck),
        }

class GameEngine:
    def __init__(self,
        previous_state:dict,
        player_ids:List[str],
        game_type : str,
    ):
        if previous_state:
            self._state = previous_state
        else:
            self._state = {
                "game_type": game_type,
                "player_ids": player_ids,
                "player_states": [PlayerState() for _ in player_ids],
            }

    def player_state(self, player_id:str):
        return self._state["player_states"][self._state["player_ids"].index(player_id)]

    def get_state(self):
        return self._state

    def get_public_state(self):
        return {
            "player_ids": self._state["player_ids"],
            "player_states": [state.get_public_state() for state in self._state["player_states"]],
        }

    def begin_game(self):
        events = []


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
        original_life = player.life
        target.life -= damage
        new_life = target.life

        for player in self._state["player_ids"]:
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