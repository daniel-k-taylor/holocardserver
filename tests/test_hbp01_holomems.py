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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with

class Test_hbp01_holomems(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_009_konkanata_centeronly(self):
        p1deck = generate_deck_with([], {"hBP01-009": 1}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Put p1's center in the collab spot.
        player1.collab = [player1.center[0]]
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-009", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        # Give p2 a collab.
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        actions = reset_mainstep(self)
        events = engine.grab_events()

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)
        self.assertEqual(len(actions[0]["valid_targets"]), 1)
        # Collab still has expected 2 targets.
        self.assertEqual(len(actions[1]["valid_targets"]), 2)

    def test_hbp01_010_tag_missing(self):
        p1deck = generate_deck_with([], {"hBP01-010": 1}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        # Give a cheer so when collabing it doesn't end turn after first attack.
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        actions = reset_mainstep(self)
        events = engine.grab_events()
        # Do a collab with the 010.
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {"card_id": test_card["game_card_id"] })
        events = self.engine.grab_events()
        # Events: Collab, turn effect added and back to main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
            })
        validate_event(self, events[2], EventType.EventType_AddTurnEffect, self.player1, { "effect_player_id": self.player1 })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

        actions = reset_mainstep(self)

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)


        self.assertEqual(len(actions[0]["valid_targets"]), 1)

        # Perform the art.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost stat, perform art, performance step
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 10,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player2.center[0]["game_card_id"],
            "power": 40,
            "died": False,
            "game_over": False,
        })
        events = reset_performancestep(self)

    def test_hbp01_010_tag_present(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        # Give a cheer so when collabing it doesn't end turn after first attack.
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        player1.center = []
        center_card = put_card_in_play(self, player1, "hBP01-010", player1.center)
        spawn_cheer_on_card(self, player1, center_card["game_card_id"], "white", "w2")
        actions = reset_mainstep(self)
        events = engine.grab_events()
        # Do a collab with the 010.
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {"card_id": test_card["game_card_id"] })
        events = self.engine.grab_events()
        # Events: Collab, turn effect added and back to main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
            })
        validate_event(self, events[2], EventType.EventType_AddTurnEffect, self.player1, { "effect_player_id": self.player1 })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

        actions = reset_mainstep(self)

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)


        self.assertEqual(len(actions[0]["valid_targets"]), 1)

        # Perform the art.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "imoffnow",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost stat, perform art, performance step
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 10,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 20,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "imoffnow",
            "target_id": player2.center[0]["game_card_id"],
            "power": 50,
            "died": False,
            "game_over": False,
        })
        events = reset_performancestep(self)

if __name__ == '__main__':
    unittest.main()
