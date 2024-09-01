import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState
from app.gameengine import EventType
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand

class TestBloom(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_bloom_1st_to_1st(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that you can do a level 1 bloom on top of another level 1 bloom"""
        # First go ahead and bloom the center with an 005.
        do_bloom(self, player1, player1.hand[-1]["game_card_id"], player1.center[0]["game_card_id"])
        # Cheat and unset the "bloomed_this_turn" flag.
        player1.center[0]["bloomed_this_turn"] = False
        reset_mainstep(self)
        # Now do the same thing again, this time blooming the 005 over top of the 005.
        do_bloom(self, player1, player1.hand[-1]["game_card_id"], player1.center[0]["game_card_id"])

    def test_cantbloom_if_would_die(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that you can't bloom if you would die"""
        # First, bloom a 006 and give it 200 damage.
        bloom_card = add_card_to_hand(self, player1, "hSD01-006")

        # Bloom over the center.
        do_bloom(self, player1, bloom_card["game_card_id"], player1.center[0]["game_card_id"])
        # Cheat and unset the "bloomed_this_turn" flag.
        player1.center[0]["bloomed_this_turn"] = False
        # Set the damage to 200.
        player1.center[0]["damage"] = 200
        actions = reset_mainstep(self)
        # Verify there is not a bloom action with target of the bloom card.
        for action in actions:
            if action["action_type"] == GameAction.MainStepBloom:
                self.assertNotEqual(action["target_id"], bloom_card["game_card_id"])

    def test_bloom_2nd(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test that you bloom level 2 works"""
        # First, bloom a 013 Soraz, also, grab a 011 2nd bloom azki
        bloom_card1 = add_card_to_hand(self, player1, "hSD01-013")
        bloom_card2 = add_card_to_hand(self, player1, "hSD01-011")

        # Bloom over the center.
        original_center = player1.center[0]
        do_bloom(self, player1, bloom_card1["game_card_id"], player1.center[0]["game_card_id"])
        # Cheat and unset the "bloomed_this_turn" flag.
        player1.center[0]["bloomed_this_turn"] = False
        # Set the damage to 100 because why not.
        player1.center[0]["damage"] = 100
        actions = reset_mainstep(self)

        # Now, we should be able to bloom the 2nd level onto center.
        do_bloom(self, player1, bloom_card2["game_card_id"], bloom_card1["game_card_id"])
        self.assertEqual(len(bloom_card2["stacked_cards"]), 2)
        self.assertEqual(bloom_card2["stacked_cards"][0]["game_card_id"], bloom_card1["game_card_id"])
        self.assertEqual(bloom_card2["stacked_cards"][1]["game_card_id"], original_center["game_card_id"])

if __name__ == '__main__':
    unittest.main()
