import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState
from app.gameengine import EventType
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand
from helpers import end_turn

class TestResetStep(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_reset_replacement_choice(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that when replacing the center and you have multiple backstage options, you can choose"""
        # Prep for player 2 to have a choice.
        player2.archive_holomem_from_play(player2.center[0]["game_card_id"])
        events = end_turn(self)
        # Player 2 should have a replacement choice, all 5 backstage are valid.
        validate_event(self, events[-1], EventType.EventType_ResetStepChooseNewCenter, self.player2, {
            "active_player": self.player2
        })
        center_options = events[-1]["center_options"]
        self.assertEqual(len(center_options), 5)
        # Pick the first one.
        chosen_center = player2.backstage[0]["game_card_id"]
        self.engine.handle_game_message(self.player2, GameAction.ChooseNewCenter, {
            "new_center_card_id": chosen_center
        })
        events = self.engine.grab_events()
        # Move card and draw/cheer events.
        self.assertEqual(len(events), 6)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": chosen_center,
        })
        validate_event(self, events[3], EventType.EventType_Draw, self.player2, {
            "drawing_player_id": self.player2
        })
        validate_event(self, events[5], EventType.EventType_CheerStep, self.player2, { "active_player": self.player2, })
        self.assertEqual(chosen_center, player2.center[0]["game_card_id"])
        self.assertTrue(chosen_center not in ids_from_cards(player2.backstage))

    def test_reset_replacement_choice_skip_resting(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that when replacing the center and you have multiple backstage options, you can choose minus a rested card"""
        # Prep for player 2 to have a choice.
        player2.archive_holomem_from_play(player2.center[0]["game_card_id"])
        # Put 1 into the collab slot
        collaber = player2.backstage[0]
        collab_card, _, _ = player2.find_and_remove_card(collaber["game_card_id"])
        player2.collab.append(collab_card)
        self.assertEqual(len(player2.collab), 1)
        self.assertTrue(not collaber["resting"])
        events = end_turn(self)
        # Player 2 should have a replacement choice, only 4 backstage are valid.
        validate_event(self, events[-1], EventType.EventType_ResetStepChooseNewCenter, self.player2, {
            "active_player": self.player2
        })
        center_options = events[-1]["center_options"]
        self.assertEqual(len(center_options), 4)
        self.assertTrue(collaber["resting"])
        self.assertTrue(collaber["game_card_id"] not in center_options)
        # Pick the first one.
        chosen_center = player2.backstage[0]["game_card_id"]
        self.engine.handle_game_message(self.player2, GameAction.ChooseNewCenter, {
            "new_center_card_id": chosen_center
        })
        events = self.engine.grab_events()
        # Move card and draw/cheer events.
        self.assertEqual(len(events), 6)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": chosen_center,
        })
        validate_event(self, events[3], EventType.EventType_Draw, self.player2, {
            "drawing_player_id": self.player2
        })
        validate_event(self, events[5], EventType.EventType_CheerStep, self.player2, { "active_player": self.player2, })
        self.assertEqual(chosen_center, player2.center[0]["game_card_id"])
        self.assertTrue(chosen_center not in ids_from_cards(player2.backstage))

    def test_reset_replacement_choice_allow_resting_if_all_resting(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that when replacing the center and you have multiple backstage options,
            if all are resting, you can choose among all.
        """
        # Prep for player 2 to have a choice.
        player2.archive_holomem_from_play(player2.center[0]["game_card_id"])
        # Put 1 into the collab slot
        collaber = player2.backstage[0]
        collab_card, _, _ = player2.find_and_remove_card(collaber["game_card_id"])
        player2.collab.append(collab_card)
        self.assertEqual(len(player2.collab), 1)
        self.assertTrue(not collaber["resting"])
        for card in player2.backstage:
            card["resting"] = True
            card["rest_extra_turn"] = True
        events = end_turn(self)
        # Player 2 should have a replacement choice, all 5 should be valid since they're forced resting.
        validate_event(self, events[-1], EventType.EventType_ResetStepChooseNewCenter, self.player2, {
            "active_player": self.player2
        })
        center_options = events[-1]["center_options"]
        self.assertEqual(len(center_options), 5)
        self.assertTrue(collaber["resting"])
        self.assertTrue(collaber["game_card_id"] in center_options)
        # Pick the first one.
        chosen_center = player2.backstage[0]["game_card_id"]
        self.engine.handle_game_message(self.player2, GameAction.ChooseNewCenter, {
            "new_center_card_id": chosen_center
        })
        events = self.engine.grab_events()
        # Move card and draw/cheer events.
        self.assertEqual(len(events), 6)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": chosen_center,
        })
        validate_event(self, events[3], EventType.EventType_Draw, self.player2, {
            "drawing_player_id": self.player2
        })
        validate_event(self, events[5], EventType.EventType_CheerStep, self.player2, { "active_player": self.player2, })
        self.assertEqual(chosen_center, player2.center[0]["game_card_id"])
        self.assertTrue(chosen_center not in ids_from_cards(player2.backstage))
        self.assertTrue(player2.center[0]["resting"])


    def test_reset_replacement_choice_at_turn_end(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that when replacing the center and you have multiple backstage options, you can choose"""
        # Somehow player 1's holomem center died on their turn.
        player1.archive_holomem_from_play(player1.center[0]["game_card_id"])
        engine.handle_game_message(self.player1, GameAction.MainStepEndTurn, {})
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_EndTurn, self.player1, {
            "ending_player_id": self.player1,
            "next_player_id": self.player2,
        })
        validate_event(self, events[-1], EventType.EventType_ResetStepChooseNewCenter, self.player2, {
            "active_player": self.player1
        })
        center_options = events[-1]["center_options"]
        self.assertEqual(len(center_options), 5)
        # Pick the first one.
        chosen_center = player1.backstage[0]["game_card_id"]
        self.engine.handle_game_message(self.player1, GameAction.ChooseNewCenter, {
            "new_center_card_id": chosen_center
        })
        events = self.engine.grab_events()
        # BMove card, begin turn, resetx2, and draw/cheer events.
        self.assertEqual(len(events), 12)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": chosen_center,
        })
        validate_event(self, events[2], EventType.EventType_TurnStart, self.player1, {
            "active_player": self.player2,
        })
        validate_event(self, events[9], EventType.EventType_Draw, self.player2, {
            "drawing_player_id": self.player2
        })
        validate_event(self, events[11], EventType.EventType_CheerStep, self.player2, { "active_player": self.player2, })
        self.assertEqual(chosen_center, player1.center[0]["game_card_id"])
        self.assertTrue(chosen_center not in ids_from_cards(player1.backstage))

if __name__ == '__main__':
    unittest.main()
