import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState, UNLIMITED_SIZE
from app.gameengine import EventType, GameOverReason
from app.gameengine import GameAction, GamePhase, EffectType
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand, do_cheer_step_on_card
from helpers import end_turn, validate_last_event_is_error, validate_last_event_not_error, do_collab_get_events, set_next_die_rolls
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, pick_choice, use_oshi_action, add_card_to_archive

class Test_hbp02_Support(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_support_hbp02_084_mikkorone24_die_roll_1(self):
        p1deck = generate_deck_with("", {"hBP02-084": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Add 2 of these to hand so we can also test limited.
        test_card = add_card_to_hand(self, player1, "hBP02-084", True)
        test_card_2nd = add_card_to_hand(self, player1, "hBP02-084", True)
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 5)

        set_next_die_rolls(self, [1,1])
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": test_card["game_card_id"],
        })
        events = self.engine.grab_events()
        # Events - play support, draw, roll die, discard, main step
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": test_card["game_card_id"],
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        validate_event(self, events[4], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[6], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": test_card["game_card_id"],
        })
        validate_event(self, events[8], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})

        self.assertEqual(len(player1.hand), 6)
        self.assertTrue(player1.used_limited_this_turn)
        self.assertEqual(player1.archive[0]["game_card_id"], test_card["game_card_id"])

        # Check that there is no action to play support because we already played a limited.
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport not in [action["action_type"] for action in actions])

        # End turn twice and we can play again.
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

    def test_support_hbp02_084_mikkorone24_die_roll_2_4_draw_again(self):
        p1deck = generate_deck_with("", {"hBP02-084": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        
        """Test"""
        test_card = add_card_to_hand(self, player1, "hBP02-084", True)
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 4)

        set_next_die_rolls(self, [2,2])
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": test_card["game_card_id"],
        })
        events = self.engine.grab_events()
        # Events - play support, draw, roll die, draw, discard, main step
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": test_card["game_card_id"],
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        validate_event(self, events[4], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 2,
            "rigged": False,
        })
        validate_event(self, events[6], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": test_card["game_card_id"],
        })
        validate_event(self, events[10], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})

        self.assertEqual(len(player1.hand), 6)
        self.assertTrue(player1.used_limited_this_turn)
        self.assertEqual(player1.archive[0]["game_card_id"], test_card["game_card_id"])