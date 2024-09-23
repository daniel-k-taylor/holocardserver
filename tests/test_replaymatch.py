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

card_db = CardDatabase()

class TestReplayMatch(unittest.TestCase):

    engine : GameEngine

    def setUp(self):
        pass

    def test_run_match_replay(self):
        # Read any match logs from the test_match_logs dir in this directory.
        # For each match log, load the match and replay it.
        match_logs_path = os.path.join(Path(__file__).parent, "test_match_logs")
        for match_log in os.listdir(match_logs_path):
            with open(os.path.join(match_logs_path, match_log), "r") as f:
                match_data = json.load(f)
                self.replay_match(match_data)

    def replay_match(self, match_data):

        all_game_messages = match_data["all_game_messages"]
        next_message_index = 0
        self.players = match_data["player_info"]
        engine = GameEngine(card_db, match_data["game_type"], self.players)
        engine.seed = int(match_data["seed"])
        engine.begin_game()
        all_events = []
        while not engine.is_game_over():
            events = engine.grab_events()
            self.assertNotEqual(events[-1]["event_type"], EventType.EventType_GameError)
            self.assertTrue(len(events) > 0)
            all_events += events
            next_message = all_game_messages[next_message_index]
            engine.handle_game_message(next_message["player_id"], next_message["action_type"], next_message["action_data"])
            next_message_index += 1
        events = engine.grab_events()
        all_events += events
        self.assertTrue(engine.is_game_over())


if __name__ == '__main__':
    unittest.main()
