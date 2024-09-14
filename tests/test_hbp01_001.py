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

class Test_hbp01_001(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        p1deck = generate_deck_with("hBP01-001")
        initialize_game_to_third_turn(self, p1deck)

    def test_hbp01_001_oshi_squeezesqueeze_set_center_hp(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        # Give p2 a center with lots of hp for fun.
        player2.center = []
        target_center = put_card_in_play(self, player2, "hSD01-006", player2.center)
        actions = reset_mainstep(self)
        events = engine.grab_events()
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)
        player2.center[0]["damage"] = 20
        self.assertEqual(player2.center[0]["damage"], 20)

        # Use the first skill.
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "squeezesqueeze"})
        events = engine.grab_events()
        # Events - 3 holopower move, oshi activation, set hp, main step
        self.assertEqual(len(events), 12)
        validate_event(self, events[8], EventType.EventType_ModifyHP, self.player1, {
            "target_player_id": self.player2,
            "card_id": target_center["game_card_id"],
            "damage_done": 170,
            "new_damage": 190,
        })
        self.assertEqual(len(player1.holopower), 0)
        self.assertEqual(player2.center[0]["damage"], 190)
        actions = reset_mainstep(self)


    def test_hbp01_001_oshi_squeezesqueeze_set_center_hp_too_low(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        # Give p2 a center with lots of hp for fun.
        player2.center = []
        target_center = put_card_in_play(self, player2, "hSD01-006", player2.center)
        actions = reset_mainstep(self)
        events = engine.grab_events()
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)
        player2.center[0]["damage"] = 200
        self.assertEqual(player2.center[0]["damage"], 200)

        # Use the first skill.
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "squeezesqueeze"})
        events = engine.grab_events()
        # Events - 3 holopower move, oshi activation, main step, skipped the modify hp event
        self.assertEqual(len(events), 10)
        self.assertEqual(len(player1.holopower), 0)
        self.assertEqual(player2.center[0]["damage"], 200)
        actions = reset_mainstep(self)

    def test_hbp01_001_oshi_illcrushyou(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        actions = reset_mainstep(self)
        events = engine.grab_events()
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)

        # Use the skill
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "illcrushyou"})
        events = engine.grab_events()
        # Events - 2 holopower move, oshi activation, choose holomem
        self.assertEqual(len(events), 8)
        can_choose = ids_from_cards(player1.get_holomem_on_stage())
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        self.assertListEqual(events[6]["cards_can_choose"], can_choose)
        self.assertEqual(len(player1.holopower), 1)

        # Just go with our center
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.center[0]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - add turn effect, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_AddTurnEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        actions = reset_mainstep(self)
        # add a cheer to a backstage member and collab with them.
        # backstage[0] is 003 and has no collab effects.
        collab_id = player1.backstage[0]["game_card_id"]
        spawn_cheer_on_card(self, player1, player1.backstage[0]["game_card_id"], "white", "w1")
        do_collab_get_events(self, player1, player1.backstage[0]["game_card_id"])
        self.assertEqual(player1.collab[0]["game_card_id"], collab_id)
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3) # 2 arts and end turn
        # First attack with collab, which should only do the 30 damage.
        p2target = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": collab_id,
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 6) # Use art, damage dealt, perf step
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": collab_id,
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"],
            "power": 30,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_player": self.player2,
            "target_id": p2target["game_card_id"],
            "damage": 30,
            "died": False,
            "game_over": False,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        actions = reset_performancestep(self)

        # Perform center art, this gets boosted.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 10) # 2 stat boosts, Use art, damage dealt, distribute cheer
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"],
            "power": 130,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2target["game_card_id"],
            "damage": 130,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
        })


    def test_hbp01_001_oshi_illcrushyou_center_notwhite(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Swap p1 center with a green card.
        player1.center = []
        put_card_in_play(self, player1, "hSD01-008", player1.center)
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        #
        player1.generate_holopower(3)
        actions = reset_mainstep(self)
        events = engine.grab_events()
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)

        # Use the skill
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "illcrushyou"})
        events = engine.grab_events()
        # Events - 2 holopower move, oshi activation, choose holomem
        self.assertEqual(len(events), 8)
        can_choose = ids_from_cards(player1.get_holomem_on_stage())
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        self.assertListEqual(events[6]["cards_can_choose"], can_choose)
        self.assertEqual(len(player1.holopower), 1)

        # Just go with our center
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.center[0]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - add turn effect, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_AddTurnEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        actions = reset_mainstep(self)
        # add a cheer to a backstage member and collab with them.
        # backstage[0] is 003 and has no collab effects.
        collab_id = player1.backstage[0]["game_card_id"]
        spawn_cheer_on_card(self, player1, player1.backstage[0]["game_card_id"], "white", "w1")
        do_collab_get_events(self, player1, player1.backstage[0]["game_card_id"])
        self.assertEqual(player1.collab[0]["game_card_id"], collab_id)
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3) # 2 arts and end turn
        # First attack with collab, which should only do the 30 damage.
        p2target = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": collab_id,
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 6) # Use art, damage, perf step
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": collab_id,
            "art_id": "nunnun",
            "target_id": p2target["game_card_id"],
            "power": 30,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2target["game_card_id"],
            "damage": 30,
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        actions = reset_performancestep(self)

        # Perform center art, this gets boosted.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "keepworkinghard",
            "target_id": p2target["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 8) # 1 stat boosts, Use art, damage, distribute cheer
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "keepworkinghard",
            "target_id": p2target["game_card_id"],
            "power": 70,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2target["game_card_id"],
            "damage": 70,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
        })


if __name__ == '__main__':
    unittest.main()
