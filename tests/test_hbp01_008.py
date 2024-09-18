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

class Test_hbp01_008(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_008_prayingforrain(self):
        p1deck = generate_deck_with("hBP01-008", {"hBP01-077": 2, "hBP01-024": 2, "hSD01-012": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        player1.center = []
        id1 = put_card_in_play(self, player1, "hBP01-024", player1.center)
        id2 = put_card_in_play(self, player1, "hSD01-012", player1.collab)
        player1.backstage = player1.backstage[1:]
        id3 = put_card_in_play(self, player1, "hBP01-024", player1.backstage)
        # Archive 7 cards from the cheer deck.
        player1.archive = player1.cheer_deck[:7]
        player1.cheer_deck = player1.cheer_deck[7:]
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {
            "skill_id": "prayingforrain"
        })
        events = engine.grab_events()
        # Events - 3x holopower, oshi skill, send cheer decision
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {})
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {})
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "prayingforrain",
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 5,
            "from_zone": "archive",
            "to_zone": "holomem",
            "multi_to": True,
        })
        from_options = events[8]["from_options"]
        to_options = events[8]["to_options"]
        self.assertEqual(len(from_options), 7)
        self.assertEqual(len(to_options), 3)
        self.assertTrue(id1["game_card_id"] in to_options)
        self.assertTrue(id2["game_card_id"] in to_options)
        self.assertTrue(id3["game_card_id"] in to_options)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[1]: id1["game_card_id"],
                from_options[2]: id2["game_card_id"],
                from_options[3]: id3["game_card_id"],
                from_options[4]: id3["game_card_id"],
                from_options[6]: id1["game_card_id"],
            }
        })
        events = engine.grab_events()
        # Events - 5 move cheer, main step
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[4], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[6], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[8], EventType.EventType_MoveAttachedCard, self.player1, {})
        actions = reset_mainstep(self)
        self.assertEqual(len(id1["attached_cheer"]), 2)
        self.assertEqual(id1["attached_cheer"][0]["game_card_id"], from_options[1])
        self.assertEqual(id1["attached_cheer"][1]["game_card_id"], from_options[6])
        self.assertEqual(len(id2["attached_cheer"]), 1)
        self.assertEqual(id2["attached_cheer"][0]["game_card_id"], from_options[2])
        self.assertEqual(len(id3["attached_cheer"]), 2)
        self.assertEqual(id3["attached_cheer"][0]["game_card_id"], from_options[3])
        self.assertEqual(id3["attached_cheer"][1]["game_card_id"], from_options[4])


    def test_hbp01_008_rainshamanism(self):
        p1deck = generate_deck_with("hBP01-008", {"hBP01-077": 2, "hBP01-081": 2, "hSD01-012": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        player1.center = []
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-081", player1.center)
        s1 = put_card_in_play(self, player1, "hBP01-077", test_card["stacked_cards"])
        s2 = put_card_in_play(self, player1, "hBP01-077", test_card["stacked_cards"])
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b3")
        b4 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b4")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Events - pick archive cheer choice.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [b1["game_card_id"],b2["game_card_id"],b3["game_card_id"],b4["game_card_id"]])

        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b1["game_card_id"],b2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - archive the 2 cheer so move 2 cards, oshi choice
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "to_zone": "archive",
            "card_id": b1["game_card_id"]
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "to_zone": "archive",
            "card_id": b2["game_card_id"]
        })
        validate_event(self, events[4], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Pay 1 holo, oshi activation, choose target
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "rainshamanism",
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseHolomemForEffect , self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[4]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, ids_from_cards(player2.center + player2.collab + player2.backstage))
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player2.center[0]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - deal damage, boost, art, damage, send cheer cause dead
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "damage": 20,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 120,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": p2center["game_card_id"],
            "power": 180,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 180,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[10], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

if __name__ == '__main__':
    unittest.main()
