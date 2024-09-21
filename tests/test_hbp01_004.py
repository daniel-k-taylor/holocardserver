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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, use_oshi_action, pick_choice

class Test_hbp01_004(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_004_nousagis_noholo(self):
        p1deck = generate_deck_with("hBP01-004", {"hBP01-114": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(1)
        actions = reset_mainstep(self)

        p1center = player1.center[0]

        # add green cheers to center
        g1 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g3")
        g4 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g4")
        g5 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g5")
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        begin_performance(self)
        # Prep p1 center to die
        p1center["damage"] = p1center["hp"] - 10
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": p1center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform art, damage, down (no holo), send cheer
        self.assertEqual(len(events), 8)
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_004_nousagis(self):
        p1deck = generate_deck_with("hBP01-004", {"hBP01-114": 4 }, [])
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
        actions = reset_mainstep(self)

        p1center = player1.center[0]

        # add green cheers to center
        g1 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g3")
        g4 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g4")
        g5 = spawn_cheer_on_card(self, player1, p1center["game_card_id"], "green", "g5")
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        begin_performance(self)
        # Prep p1 center to die
        p1center["damage"] = p1center["hp"] - 10
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": p1center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform art, damage, on down choice to use nousagis
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "target_player": self.player1,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Use it
        events = pick_choice(self, self.player1, 0)
        # Events - holox2, oshi, send cheer
        self.assertEqual(len(events), 8)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "nousagis",
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 5,
            "amount_max": 5,
            "from_zone": "downed_holomem",
            "to_zone": "holomem",
        })
        from_options = events[6]["from_options"]
        to_options = events[6]["to_options"]
        placements = {}
        placements[from_options[0]] = player1.backstage[0]["game_card_id"]
        placements[from_options[1]] = player1.backstage[2]["game_card_id"]
        placements[from_options[2]] = player1.backstage[2]["game_card_id"]
        placements[from_options[3]] = player1.backstage[2]["game_card_id"]
        placements[from_options[4]] = player1.backstage[3]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - 5 move cards, damage, send cheer
        self.assertEqual(len(events), 14)
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player1,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        self.assertEqual(len(player1.backstage[0]["attached_cheer"]), 1)
        self.assertEqual(len(player1.backstage[2]["attached_cheer"]), 3)
        self.assertEqual(len(player1.backstage[3]["attached_cheer"]), 1)


    def test_hbp01_004_oshi_luckyrabbit(self):
        p1deck = generate_deck_with("hBP01-004", {"hBP01-038": 4 }, [])
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

        events = use_oshi_action(self, "luckyrabbit")
        # Spend 3 holopower, oshi activation, main step
        self.assertEqual(len(events), 12)
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "luckyrabbit",
        })
        validate_event(self, events[8], EventType.EventType_AddTurnEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        set_next_die_rolls(self, [1,1])
        actions = reset_mainstep(self)
        player1.center = []
        c1 = put_card_in_play(self, player1, "hBP01-038", player1.center)
        c2 = put_card_in_play(self, player1, "hBP01-038", player1.collab)
        spawn_cheer_on_card(self, player1, c1["game_card_id"], "green", "g1")
        spawn_cheer_on_card(self, player1, c2["game_card_id"], "green", "g2")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": c1["game_card_id"],
            "art_id": "konpeko",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 10)
        # Events - roll die, power boost, perform art, damage, perform step
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": True,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20
        })
        self.assertEqual(player2.center[0]["damage"], 40)

        # Now attack with the collab
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": c2["game_card_id"],
            "art_id": "konpeko",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - roll die, power boost, perform art, damage, send cheer
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": True,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20
        })
        self.assertEqual(p2center["damage"], 80)
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 40,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })



if __name__ == '__main__':
    unittest.main()
