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

class TestGameOver(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_gameover_nomems(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test the oshi skill usage conditions"""
        # Prep - remove all p2 backstage and give damage to its center
        player2.backstage = []
        player2.center[0]["damage"] = 50
        reset_mainstep(self)

        performer = player1.center[0]
        target = player2.center[0]

        # Perform and hit the center to kill it.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = self.engine.grab_events()
        validate_last_event_not_error(self, events)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": performer["game_card_id"],
            "art_id": "nunnun",
            "target_id": target["game_card_id"],
        })
        events = self.engine.grab_events()
        # Events - performance, damage dealt, gameover
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": performer["game_card_id"],
            "art_id": "nunnun",
            "target_id": target["game_card_id"],
            "power": 30,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": target["game_card_id"],
            "damage": 30,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": target["game_card_id"],
            "game_over": True,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_GameOver, self.player1, {
            "loser_id": self.player2,
            "reason_id": GameOverReason.GameOverReason_NoHolomemsLeft,
        })

    def test_gameover_nolife(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test the oshi skill usage conditions"""
        # Prep - leave backstage, give damage to its center
        player2.center[0]["damage"] = 50
        # cut life down to just 1 entry
        player2.life = player2.life[:1]
        reset_mainstep(self)

        performer = player1.center[0]
        target = player2.center[0]

        # Perform and hit the center to kill it.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = self.engine.grab_events()
        validate_last_event_not_error(self, events)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": performer["game_card_id"],
            "art_id": "nunnun",
            "target_id": target["game_card_id"],
        })
        events = self.engine.grab_events()
        # Events - performance, dealt damage gameover
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": performer["game_card_id"],
            "art_id": "nunnun",
            "target_id": target["game_card_id"],
            "power": 30,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": target["game_card_id"],
            "damage": 30,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": target["game_card_id"],
            "game_over": True,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_GameOver, self.player1, {
            "loser_id": self.player2,
            "reason_id": GameOverReason.GameOverReason_NoLifeLeft,
        })

    def test_gameover_nocards(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test the oshi skill usage conditions"""
        # Prep - remove p2's deck
        player2.deck = []
        reset_mainstep(self)
        events = end_turn(self)
        # Events - end turn, turn start, reset activate/rest, die
        self.assertEqual(len(events), 10)
        validate_event(self, events[8], EventType.EventType_GameOver, self.player1, {
            "loser_id": self.player2,
            "reason_id": GameOverReason.GameOverReason_DeckEmptyDraw,
        })

if __name__ == '__main__':
    unittest.main()
