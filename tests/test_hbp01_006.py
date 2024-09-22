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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, use_oshi_action, pick_choice

class Test_hbp01_006(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_006_phoenixtail(self):
        p1deck = generate_deck_with("hBP01-006", {"hBP01-059": 4, "hBP01-103": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Make the holopower is not holomems
        test1 = add_card_to_hand(self, player1, "hBP01-103")
        test2 = add_card_to_hand(self, player1, "hBP01-103")
        player1.deck.insert(0, test1)
        player1.deck.insert(0, test2)
        player1.hand = player1.hand[:2]
        player1.generate_holopower(2)
        retrieve_card = put_card_in_play(self, player1, "hBP01-059", player1.archive)
        put_card_in_play(self, player1, "hBP01-103", player1.archive)
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.archive), 2)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 1)
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "phoenixtail"})
        events = engine.grab_events()
        # Events - 2x holo, oshi activation, choose cards from archive
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "phoenixtail",
        })
        validate_event(self, events[6], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "archive",
            "to_zone": "hand"
        })
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 1)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {"card_ids": [retrieve_card["game_card_id"]]})
        events = engine.grab_events()
        # Events - move card, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "hand",
            "card_id": retrieve_card["game_card_id"]
        })

    def test_hbp01_006_risefromtheashes(self):
        p1deck = generate_deck_with("hBP01-006", {"hBP01-057": 2, "hBP01-058": 2, "hBP01-059": 2,  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(2)
        player1.center = []
        test1 = put_card_in_play(self, player1, "hBP01-057", player1.center)
        b1 = add_card_to_hand(self, player1, "hBP01-058")
        b2 = add_card_to_hand(self, player1, "hBP01-059")
        b3 = add_card_to_hand(self, player1, "hBP01-059")
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": b1["game_card_id"],
            "target_id": test1["game_card_id"]
        })
        events = engine.grab_events()
        # Bloom, main step
        self.assertEqual(len(events), 4)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)
        end_turn(self)
        do_cheer_step_on_card(self, player1.center[0])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": b2["game_card_id"],
            "target_id": b1["game_card_id"]
        })
        events = engine.grab_events()
        # Bloom, main step
        self.assertEqual(len(events), 4)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])  # P1 turn start, cheer on center
        actions = reset_mainstep(self)
        end_turn(self)
        do_cheer_step_on_card(self, player1.center[0])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": b3["game_card_id"],
            "target_id": b2["game_card_id"]
        })
        events = engine.grab_events()
        # Bloom, main step
        self.assertEqual(len(events), 4)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])  # P1 turn start, cheer on center
        actions = reset_mainstep(self)
        # Ok, now that p1's bloom is stacked up, kill it with p2 and we trigger rise and get all the cards back.
        player1.center[0]["damage"] = player1.center[0]["hp"] - 10
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": b3["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform, damage, on kill effect choice
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": b3["game_card_id"],
            "damage": 30,
            "special": False,
        })
        events = pick_choice(self, self.player1, 0)
        # Events - 2 holopower, oshi, down, send cheer
        self.assertEqual(len(events), 18)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "risefromtheashes",
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": b3["game_card_id"],
            "life_lost": 0
        })
        archived_ids = events[6]["archived_ids"]
        hand_ids = events[6]["hand_ids"]
        self.assertListEqual(archived_ids, cheer_on_p1)
        self.assertTrue(b1["game_card_id"] in hand_ids)
        self.assertTrue(b2["game_card_id"] in hand_ids)
        self.assertTrue(b3["game_card_id"] in hand_ids)
        self.assertTrue(test1["game_card_id"] in hand_ids)
        validate_event(self, events[8], EventType.EventType_EndTurn, self.player1, {})

        validate_event(self, events[16], EventType.EventType_ResetStepChooseNewCenter, self.player1, {
            "active_player": self.player1
        })
        inhand = ids_from_cards(player1.hand)
        self.assertTrue(b1["game_card_id"] in inhand)
        self.assertTrue(b2["game_card_id"] in inhand)
        self.assertTrue(b3["game_card_id"] in inhand)
        self.assertTrue(test1["game_card_id"] in inhand)


if __name__ == '__main__':
    unittest.main()
