TEST_RUNS = 10

import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState, UNLIMITED_SIZE
from app.gameengine import EventType, GameOverReason
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand, do_cheer_step_on_card
from helpers import end_turn, validate_last_event_is_error, validate_last_event_not_error, do_collab_get_events, set_next_die_rolls
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep

from app.aiplayer import AIPlayer

card_db = CardDatabase()

# Load the starter deck from decks/starter_azki.json
decks_path = os.path.join(Path(__file__).parent.parent, "decks")
azki_path = os.path.join(decks_path, "starter_azki.json")
sora_path = os.path.join(decks_path, "starter_sora.json")
with open(azki_path, "r") as f:
    azki_starter = json.load(f)
with open(sora_path, "r") as f:
    sora_starter = json.load(f)

class TestStarterDeckCards(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_ai_game(self):
        for i in range(TEST_RUNS):
            print("Game Run:", i + 1)
            self.run_ai_game()

    def test_ai_game_just_setup(self):
        for i in range(TEST_RUNS):
            print("Game Run:", i + 1)
            self.run_ai_game(abort_after_placement=True)

    def run_ai_game(self, abort_after_placement=False):
        self.players = [
            {
                "player_id": "player1",
                "oshi_id": azki_starter["oshi_id"],
                "deck": azki_starter["deck"],
                "cheer_deck": azki_starter["cheer_deck"]
            },
            {
                "player_id": "player2",
                "oshi_id": sora_starter["oshi_id"],
                "deck": sora_starter["deck"],
                "cheer_deck": sora_starter["cheer_deck"]
            }
        ]
        engine = GameEngine(card_db, "versus", self.players)

        self.player1 = self.players[0]["player_id"]
        self.player2 = self.players[1]["player_id"]
        player1 = engine.get_player(self.players[0]["player_id"])
        player2 = engine.get_player(self.players[1]["player_id"])
        ai1 = AIPlayer(self.player1)
        ai2 = AIPlayer(self.player2)

        engine.begin_game()
        while not engine.is_game_over():
            events = engine.grab_events()
            if abort_after_placement and engine.phase == GamePhase.PlayerTurn:
                break

            self.assertNotEqual(events[-1]["event_type"], EventType.EventType_GameError)
            self.assertTrue(len(events) > 0)
            last_events = events
            ai_performing_action1, action_info = ai1.ai_process_events(events)
            if ai_performing_action1:
                engine.handle_game_message(ai1.player_id, action_info["action_type"], action_info["action_data"])

            ai_performing_action2, action_info = ai2.ai_process_events(events)
            self.assertTrue(not (ai_performing_action1 and ai_performing_action2))
            if ai_performing_action2:
                engine.handle_game_message(ai2.player_id, action_info["action_type"], action_info["action_data"])


if __name__ == '__main__':
    unittest.main()
