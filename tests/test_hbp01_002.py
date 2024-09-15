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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance

class Test_hbp01_002(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_002_oshi_guardianofcivilization_nopromise_nochoice(self):
        p1deck = generate_deck_with("hBP01-002", {"hBP01-016": 2 }, [])
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
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        actions = begin_performance(self)
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 16) # Use art, damage, end, start, reset, reset, draw, cheer
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)

    def test_hbp01_002_oshi_guardianofcivilization_promise_activates_pass_then_activate(self):
        p1deck = generate_deck_with("hBP01-002", {"hBP01-016": 2 }, [])
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
        put_card_in_play(self, player1, "hBP01-016", player1.center)
        end_turn(self)
        do_cheer_step_on_card(self, player2.backstage[0])
        player2.collab = [player2.backstage[0]]
        player2.backstage.remove(player2.backstage[0])
        actions = begin_performance(self)
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 4) # Use art, on_damage effect
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 1
        })
        events = engine.grab_events()
        #Events - damage, performance step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        actions = reset_performancestep(self)

        # Now the collab attacks
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.collab[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 4) # Use art, on_damage effect
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = engine.grab_events()
        # Events - spend 2 holopower, reduce damage, damage, end turn, start turn, reset x 2, draw, cheer
        self.assertEqual(len(events), 22)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "guardianofcivilization",
        })
        validate_event(self, events[6], EventType.EventType_BoostStat, self.player1, {
            "card_id": "",
            "stat": "damage_prevented",
            "amount": 50,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "damage": 0,
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)

    def test_hbp01_002_oshi_guardianofcivilization_promise_activates_then_cant_2nd_time(self):
        p1deck = generate_deck_with("hBP01-002", {"hBP01-016": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(5)
        player1.center = []
        put_card_in_play(self, player1, "hBP01-016", player1.center)
        end_turn(self)
        do_cheer_step_on_card(self, player2.backstage[0])
        player2.collab = [player2.backstage[0]]
        player2.backstage.remove(player2.backstage[0])
        actions = begin_performance(self)
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 4) # Use art, on_damage effect
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = engine.grab_events()
        #Events - 2x move card, oshi, reduce damage, damage, performance step
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "guardianofcivilization",
        })
        validate_event(self, events[6], EventType.EventType_BoostStat, self.player1, {
            "card_id": "",
            "stat": "damage_prevented",
            "amount": 50,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "damage": 0,
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        actions = reset_performancestep(self)
        self.assertEqual(player1.center[0]["damage"], 0)

        # Now the collab attacks
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.collab[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 16) # Use art, damage, end, start, reset2, draw, cheer
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)

    def test_hbp01_002_amazing_drawing(self):
        p1deck = generate_deck_with("hBP01-002", {"hBP01-016": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(5)
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {
            "skill_id": "amazingdrawing"
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 8)
        # 2 moves, oshi, choose cards.
        # Expect to have 2 holo fan circles to choose from.
        chosen_card_id = 0
        for card in player1.deck:
            if "sub_type" in card and card["sub_type"] == "event":
                chosen_card_id = card["game_card_id"]

        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [chosen_card_id]
        })
        events = engine.grab_events()
        # move card, shuffle, main
        self.assertEqual(len(events), 6)
        self.assertEqual(player1.hand[-1]["game_card_id"], chosen_card_id)



if __name__ == '__main__':
    unittest.main()
