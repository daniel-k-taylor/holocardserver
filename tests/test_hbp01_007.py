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

    def test_hbp01_007_art_effect_oshis_skills_timing(self):
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
        # Events - art effect first = deal damage
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        comet_target = backstage_options[0]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from special - comet choice
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
        #Events 2x move, oshi, deal the damage to that target and continue
        self.assertEqual(len(events), 14)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": comet_target,
            "damage": 50,
            "special": True,
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": comet_target,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[12], EventType.EventType_Decision_SendCheer, self.player1, {})
        from_options = events[12]["from_options"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: p2center["game_card_id"],
            }
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20,
            "special": False,
        })
        reset_performancestep(self)


    def test_hbp01_007_cant_use_comet_if_killed(self):
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
        # Events - art effect first = deal damage
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        comet_target = player2.backstage[0]
        comet_target["damage"] = comet_target["hp"] - 10
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from special, life loss prevented, no comet
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": comet_target["game_card_id"],
            "damage": 10,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": comet_target["game_card_id"],
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
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
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
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
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20, # Arts damage
            "special": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
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
        comet_target = player2.backstage[1]["game_card_id"]
        events = pick_choice(self, self.player1, 0)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": comet_target,
            "damage": 50, # comet
            "special": True,
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": comet_target,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[12], EventType.EventType_Decision_SendCheer, self.player1, {
          "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[12]["from_options"]
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


    def test_hbp01_007_comet_vs_mumei(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-076": 2, "hBP01-079": 2 }, [])
        p2deck = generate_deck_with("hBP01-002", {"hBP01-015": 50 }, [])
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(2)
        player2.generate_holopower(2)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        player1.backstage = player1.backstage[1:]

        actions = reset_mainstep(self)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - art effect first, deal damage.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from effect immediatley mumei choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player2,
        })
        choices = events[0]["choice"]
        self.assertEqual(choices[0]["incoming_damage_info"]["amount"], 10)
        # Don't use it on this one.
        events = pick_choice(self, self.player2, 1)
        # Events damage dealt, choice for comet
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 10,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        comet_target = player2.backstage[0]
        # Use comet
        events = pick_choice(self, self.player1, 0)
        # spend 2 holo, oshi activation, mumei choice to reduce.
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        validate_event(self, events[6], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player2,
        })
        events = pick_choice(self, self.player2, 0)
        # Events - no deal damage event because 0 damage
        self.assertEqual(comet_target["damage"], 10) # From the art special
        # 2x move card, oshi activation, Reduce damage, damage dealt 0
        # perform art, damage, performance step
        self.assertEqual(len(events), 14)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player2,
            "skill_id": "guardianofcivilization",
        })
        validate_event(self, events[6], EventType.EventType_BoostStat, self.player1, {
            "stat": "damage_prevented",
            "amount": 50
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": comet_target["game_card_id"],
            "damage": 0,
            "special": True,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20,
            "special": False,
        })

        reset_performancestep(self)


    def test_hbp01_007_mumei_prevent_comet_completely(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-076": 2, "hBP01-079": 2 }, [])
        p2deck = generate_deck_with("hBP01-002", {"hBP01-015": 50 }, [])
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(2)
        player2.generate_holopower(2)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        player1.backstage = player1.backstage[1:]

        actions = reset_mainstep(self)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - art effect first, deal damage.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from effect immediatley mumei choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player2,
        })
        choices = events[0]["choice"]
        self.assertEqual(choices[0]["incoming_damage_info"]["amount"], 10)
        # Prevent this!
        events = pick_choice(self, self.player2, 0)
        # Events 2x move, oshi activation, reduce damage, damage dealt = 0, perform art, etc.
        # Events - no deal damage event because 0 damage
        self.assertEqual(player2.backstage[0]["damage"], 0) # No damage
        # 2x move card, oshi activation, Reduce damage, damage dealt 0
        # perform art, damage, performance step
        self.assertEqual(len(events), 14)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player2,
            "skill_id": "guardianofcivilization",
        })
        validate_event(self, events[6], EventType.EventType_BoostStat, self.player1, {
            "stat": "damage_prevented",
            "amount": 50
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 0,
            "special": True,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20,
            "special": False,
        })
        reset_performancestep(self)


    def test_hbp01_007_shiningcomet_back_then_comet_to_kill(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-081": 2 }, [])
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
        player1.backstage = []
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-081", player1.center)
        actions = reset_mainstep(self)
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        player2.backstage = []
        # Give p2 a high hp back
        # Give it enough damage so it survives shining but dies to comet.
        p2back = put_card_in_play(self, player2, "hSD01-006", player2.backstage)
        p2back["damage"] = 160
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b3")
        b4 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b4")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": p2back["game_card_id"]
        })
        events = engine.grab_events()
        # Events - art effect first, archive 2 blue cheers
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": p2back["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
        })
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [b1["game_card_id"], b2["game_card_id"], b3["game_card_id"], b4["game_card_id"]])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b1["game_card_id"], b2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move 2 archive cards, no power boost because 0 stacked.
        # So perform art then damage, then choice for comet
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2back["game_card_id"],
            "damage": 60, # Arts damage
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_Choice, self.player1, {
        })
        comet_target = p2back
        # Use comet
        events = pick_choice(self, self.player1, 0)
        self.assertEqual(len(events), 14)
        # Events - 2x move card, oshi activation, only 1 back so deal damage, down, send cheer
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "comet",
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2back["game_card_id"],
            "damage": 50, # Comet damage
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[12], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 2,
            "amount_max": 2,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[12]["from_options"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: p2center["game_card_id"],
                from_options[1]: p2center["game_card_id"],
            }
        })
        events = engine.grab_events()
        # Move cheer, perf step
        self.assertEqual(len(events), 6)
        reset_performancestep(self)



    def test_hbp01_007_shiningcomet_thenshootingstar_to_kill(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-081": 2, "hBP01-076": 2 }, [])
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
        player1.backstage = []
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-081", player1.center)
        stack1 = put_card_in_play(self, player1, "hBP01-076", test_card["stacked_cards"])
        stack2 = put_card_in_play(self, player1, "hBP01-076", test_card["stacked_cards"])
        actions = reset_mainstep(self)
        p2center = player2.center[0]
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b3")
        b4 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b4")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - since we targeted center, the first event is a choice to use the archive ability.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "shiningcomet",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Events - art effect first, archive 2 blue cheers
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [b1["game_card_id"], b2["game_card_id"], b3["game_card_id"], b4["game_card_id"]])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b1["game_card_id"], b2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move 2 archive cards, boost power by 120 since 2 stacked
        # So perform art then damage, downed, send cheer
        self.assertEqual(len(events), 14)
        validate_event(self, events[4], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 120,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 180, # Arts damage
            "special": False,
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2center["game_card_id"],
            "life_lost": 1
        })
        validate_event(self, events[12], EventType.EventType_Decision_SendCheer, self.player1, {})
        from_options = events[12]["from_options"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: player2.backstage[0]["game_card_id"],
            }
        })
        events = engine.grab_events()
        # Events - move cheer, then choice for shooting star
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        # Use shooting star
        events = pick_choice(self, self.player1, 0)
        # Events - move card x2, oshi skill, pick target
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "shootingstar",
        })
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {})
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, ids_from_cards(player2.backstage))
        target = player2.backstage[0]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [target["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - deal damage, down, send cheer
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": target["game_card_id"],
            "damage": 180, # Shooting star damage equals the art damage
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_DownedHolomem_Before, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": target["game_card_id"],
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {})
        from_options = events[6]["from_options"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: player2.backstage[0]["game_card_id"], # New backstage 0
            }
        })
        events = engine.grab_events()
        # Events - move cheer, no comet because the target is dead!
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, player1.player_id, {})
        validate_event(self, events[2], EventType.EventType_EndTurn, player1.player_id, {})
        validate_event(self, events[10], EventType.EventType_ResetStepChooseNewCenter, player1.player_id, {})

if __name__ == '__main__':
    unittest.main()
