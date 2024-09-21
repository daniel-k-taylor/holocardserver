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

class Test_hbp01_007(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_007_comet_first_emptyhp(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-076": 2, "hBP01-079": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        # 76 can do bonus damage with art, 79 with bloom

        """Test"""
        player1.generate_holopower(2)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        p1collab = put_card_in_play(self, player1, "hBP01-079", player1.collab)
        actions = reset_mainstep(self)
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b2")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b3")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b4")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - art effect first, deal damage.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from special and choice for comet
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 10,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
        })
        choice = events[2]["choice"]
        # Use or don't use.
        self.assertEqual(len(choice), 2)
        events = pick_choice(self, self.player1, 0)
        #Events 2x move, oshi, choose who to hit
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, ids_from_cards(player2.backstage))
        # Choose who to hit.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[1]]
        })
        events = engine.grab_events()
        # Events - comet damage,  art actual damage, performance step
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": backstage_options[1],
            "damage": 50,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20,
            "special": False,
        })
        reset_performancestep(self)


    def test_hbp01_007_passcomet_shootingstar_thencometoffthat(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-076": 2, "hBP01-079": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        # 76 can do bonus damage with art, 79 with bloom

        """Test"""
        player1.generate_holopower(6)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        p1collab = put_card_in_play(self, player1, "hBP01-079", player1.collab)
        actions = reset_mainstep(self)
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b2")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b3")
        spawn_cheer_on_card(self, player1, p1collab["game_card_id"], "blue", "b4")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - art effect first, deal damage.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from effect then choice for comet
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 10,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
        })
        choice = events[2]["choice"]
        # Don't use Comet this time.
        self.assertEqual(len(choice), 2)
        events = pick_choice(self, self.player1, 1)
        # then the performance step, damage from it, then a choice for shooting star.
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20, # Arts damage
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_Choice, self.player1, {
        })
        # Use shooting star.
        events = pick_choice(self, self.player1, 0)
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "shootingstar",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[1]]
        })
        events = engine.grab_events()
        # damage event and Trigger choice for comet
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "damage": 20, # Shooting star copies art damage
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
        })
        # Use comet.
        events = pick_choice(self, self.player1, 0)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[2]]
        })
        events = engine.grab_events()
        # Comet damage, we killed somebody
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": backstage_options[2],
            "damage": 50, # comet
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": backstage_options[2],
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
          "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[4]["from_options"]
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move cheer, then perf step over
        self.assertEqual(len(events), 4)

        reset_performancestep(self)


if __name__ == '__main__':
    unittest.main()
