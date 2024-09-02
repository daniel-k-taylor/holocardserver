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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep

class TestStarterDeckCards(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_support_hSD01_006_required_member_not_there(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-006"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hSD01-006", player1.center)
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepBatonPass in [action["action_type"] for action in actions])
        baton_action = [action for action in actions if action["action_type"] == GameAction.MainStepBatonPass][0]
        self.assertEqual(baton_action["cost"], 2)
        engine.handle_game_message(self.player1, GameAction.MainStepBatonPass, {"card_id": player1.backstage[0]["game_card_id"]})
        events = engine.grab_events()
        # Events - 2 moves, archive 2 cheer, main step
        self.assertEqual(len(events), 10)
        self.assertEqual(len(player1.archive), 2)
        self.assertEqual(player1.backstage[-1]["game_card_id"], test_card["game_card_id"])

        # Put it back and begin performance
        player1.backstage.remove(test_card)
        player1.center = [test_card]

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 1) # No cheer

        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "whitecheer1")
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 1) # Not enough cheer

        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "greencheer1")
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["art_id"], "dreamlive")

        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "greencheer1")
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0]["art_id"], "dreamlive")
        self.assertEqual(actions[1]["art_id"], "sorazsympathy")

        # Perform the art, no azki so no bonus
        target = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazsympathy",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - use art, killed their center
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazsympathy",
            "target_id": target,
            "power": 60,
            "died": True,
            "game_over": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_MoveCheerChoice, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_life_pool": True,
        })
        available_cheer = events[2]["available_cheer"]
        available_targets = events[2]["available_targets"]
        self.assertEqual(len(available_cheer), 1)
        self.assertEqual(available_targets[0], player2.backstage[0]["game_card_id"])
        self.assertEqual(len(player2.archive), 2)
        cheer_placement = {
            available_cheer[0]: available_targets[0]
        }
        self.engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Events - move card, performance step
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player1 })


    def test_support_hSD01_006_required_member_met(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-006"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hSD01-006", player1.center)
        actions = reset_mainstep(self)

        player1.backstage = []
        azki_card = put_card_in_play(self, player1, "hSD01-008", player1.backstage)

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)

        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "whitecheer1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "greencheer1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "greencheer1")
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0]["art_id"], "dreamlive")
        self.assertEqual(actions[1]["art_id"], "sorazsympathy")

        # Perform the art, azki so get bonus
        target = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazsympathy",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - power boost, use art, killed their center
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": test_card["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazsympathy",
            "target_id": target,
            "power": 110,
            "died": True,
            "game_over": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MoveCheerChoice, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_life_pool": True,
        })
        available_cheer = events[4]["available_cheer"]
        available_targets = events[4]["available_targets"]
        self.assertEqual(len(available_cheer), 1)
        self.assertEqual(available_targets[0], player2.backstage[0]["game_card_id"])
        self.assertEqual(len(player2.archive), 2)
        cheer_placement = {
            available_cheer[0]: available_targets[0]
        }
        self.engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Events - move card, performance step
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player1 })

    def test_support_hSD01_006_death_costs_2(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-006"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hSD01-006", player1.center)
        test_card["damage"] = 230
        actions = reset_mainstep(self)

        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        engine.handle_game_message(self.player2, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)

        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["art_id"], "nunnun")

        # Perform the art
        life1 = player1.life[0]
        life2 = player1.life[1]
        target = test_card["game_card_id"]
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - use art killed their center, distribute 2 life
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": target,
            "power": 30,
            "died": True,
            "game_over": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_MoveCheerChoice, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 2,
            "amount_max": 2,
            "from_life_pool": True,
        })
        available_cheer = events[2]["available_cheer"]
        available_targets = events[2]["available_targets"]
        self.assertEqual(len(available_cheer), 2)
        self.assertEqual(available_targets[0], player1.backstage[0]["game_card_id"])
        self.assertEqual(len(player1.backstage[0]["attached_cards"]), 0)
        cheer_placement = {
            available_cheer[0]: available_targets[0],
            available_cheer[1]: available_targets[0]
        }
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Events - move card * 2, performance step
        self.assertEqual(len(events), 6)
        self.assertEqual(len(player1.life), 3)
        self.assertTrue(life1["game_card_id"] in [card["game_card_id"] for card in player1.backstage[0]["attached_cards"]])
        self.assertTrue(life2["game_card_id"] in [card["game_card_id"] for card in player1.backstage[0]["attached_cards"]])
        self.assertEqual(len(player1.backstage[0]["attached_cards"]), 2)
        validate_event(self, events[4], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player2 })


    def test_support_hSD01_011_weakness_boost_none(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-011"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hSD01-011", player1.center)
        test_card_id = test_card["game_card_id"]
        spawn_cheer_on_card(self, player1, test_card_id, "green", "g1")
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)

        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["art_id"], "sorazgravity")

        # Perform the art
        top_cheer = player1.cheer_deck[0]["game_card_id"]
        target = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazgravity",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - no weakness boost, send_cheer from sora for any holomem
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        from_options = events[0]["from_options"]
        to_options = events[0]["to_options"]
        cheer_placement = {
            from_options[0]: player1.backstage[0]["game_card_id"]
        }
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 6)
        # Events - move cheer, use art, p2 distribute life
        validate_event(self, events[0], EventType.EventType_MoveCheer, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": player1.backstage[0]["game_card_id"],
            "cheer_id": top_cheer,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazgravity",
            "target_id": target,
            "power": 60,
            "died": True,
            "game_over": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MoveCheerChoice, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_life_pool": True,
        })

    def test_support_hSD01_011_weakness_boost_active(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-011"""
        # Force a color onto p2's center.
        player2.center[0]["colors"].append("blue")
        player1.center = []
        player1.backstage = [] # Clear out the backstage
        test_card = put_card_in_play(self, player1, "hSD01-011", player1.center)
        test_card_id = test_card["game_card_id"]
        spawn_cheer_on_card(self, player1, test_card_id, "green", "g1")
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)

        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["art_id"], "sorazgravity")

        # Perform the art
        top_cheer = player1.cheer_deck[0]["game_card_id"]
        target = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazgravity",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - weakness boost, art, distribute
        self.assertEqual(len(events), 6)
        # Events - move cheer, use art, p2 distribute life
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": test_card["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "sorazgravity",
            "target_id": target,
            "power": 110,
            "died": True,
            "game_over": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MoveCheerChoice, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_life_pool": True,
        })


    def test_support_hSD01_012_send_cheer_color_in(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-012"""
        player1.backstage.pop()
        test_card = put_card_in_play(self, player1, "hSD01-012", player1.backstage)
        test_card_id = test_card["game_card_id"]
        actions = reset_mainstep(self)

        # As prep, put some cheer in the archive.
        spawn_cheer_on_card(self, player1, "archive", "white", "whitecheer1")
        spawn_cheer_on_card(self, player1, "archive", "white", "whitecheer2")
        spawn_cheer_on_card(self, player1, "archive", "green", "greencheer1")
        spawn_cheer_on_card(self, player1, "archive", "red", "redcheer1")
        spawn_cheer_on_card(self, player1, "archive", "blue", "bluecheer1")

        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card_id,
        })
        events = engine.grab_events()
        # Events - collab, send_cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "archive",
            "to_zone": "holomem",
            "to_limitation": "center",
        })
        from_options = events[2]["from_options"]
        to_options = events[2]["to_options"]
        self.assertEqual(len(to_options), 1)
        self.assertEqual(to_options[0], player1.center[0]["game_card_id"])
        self.assertEqual(len(from_options), 3) # Only white and green.
        self.assertTrue("redcheer1" not in from_options)
        self.assertTrue("bluecheer1" not in from_options)
        cheer_placement = {
            from_options[1]: to_options[0]
        }
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Events - move card, back to main
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCheer, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "archive",
            "to_holomem_id": player1.center[0]["game_card_id"],
            "cheer_id": from_options[1],
        })
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(player1.center[0]["attached_cards"][-1]["game_card_id"], from_options[1])


    def test_support_hSD01_013_send_cheer_thismem(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-013"""
        player1.center = []
        set_next_die_rolls(self, [1])
        test_card = put_card_in_play(self, player1, "hSD01-013", player1.center)
        test_card_id = test_card["game_card_id"]
        spawn_cheer_on_card(self, player1, test_card_id, "red", "redcheer1")
        spawn_cheer_on_card(self, player1, test_card_id, "red", "redcheer2")
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        validate_last_event_not_error(self, events)

        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]["art_id"], "brighterfuture")

        # Perform the art
        top_cheer = player1.cheer_deck[0]["game_card_id"]
        target = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "brighterfuture",
            "target_id": target
        })
        events = engine.grab_events()
        # Events - roll die, send_cheer, use art, performance step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_MoveCheer, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": player1.center[0]["game_card_id"],
            "cheer_id": top_cheer,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "brighterfuture",
            "target_id": target,
            "power": 50,
            "died": False,
            "game_over": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player1 })


    def test_support_hSD01_015_collab_with_member_sora(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-015"""
        player1.backstage.pop()
        test_card = put_card_in_play(self, player1, "hSD01-015", player1.backstage)
        test_card_id = test_card["game_card_id"]
        actions = reset_mainstep(self)

        self.assertEqual(len(player1.hand), 3)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card_id,
        })
        events = engine.grab_events()
        # Events - collab, draw, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(len(player1.hand), 4)

    def test_support_hSD01_015_collab_with_member_none(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-015"""
        player1.center = []
        put_card_in_play(self, player1, "hSD01-007", player1.center)
        player1.backstage.pop()
        test_card = put_card_in_play(self, player1, "hSD01-015", player1.backstage)
        test_card_id = test_card["game_card_id"]
        actions = reset_mainstep(self)

        self.assertEqual(len(player1.hand), 3)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card_id,
        })
        events = engine.grab_events()
        # Events - collab, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(len(player1.hand), 3)

    def test_support_hSD01_015_collab_with_member_azki(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-015"""
        player1.center = []
        put_card_in_play(self, player1, "hSD01-008", player1.center)
        player1.backstage.pop()
        test_card = put_card_in_play(self, player1, "hSD01-015", player1.backstage)
        test_card_id = test_card["game_card_id"]
        actions = reset_mainstep(self)

        top_cheer_id = player1.cheer_deck[0]["game_card_id"]
        self.assertEqual(len(player1.hand), 3)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card_id,
        })
        events = engine.grab_events()
        # Events - collab, move cheer to center,main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_MoveCheer, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": player1.center[0]["game_card_id"],
            "cheer_id": top_cheer_id,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(len(player1.hand), 3)

if __name__ == '__main__':
    unittest.main()
