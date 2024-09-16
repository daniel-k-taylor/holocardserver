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

class Test_hbp01_005(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_005_hawkeye(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
        p2deck = generate_deck_with("", { "hBP01-106": 4 }, [])
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        swap_card = add_card_to_hand(self, player2, "hBP01-106") # Swap center with back card
        player1.generate_holopower(2)
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 1)
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "hawkeye"})
        events = engine.grab_events()
        # Events - 2x holo, oshi activation, main step
        self.assertEqual(len(events), 8)
        reset_mainstep(self)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])

        # Validate baton pass is not in action list.
        actions = reset_mainstep(self)
        baton_pass = [action for action in actions if action["action_type"] == GameAction.MainStepBatonPass]
        self.assertEqual(len(baton_pass), 0)
        # Their collab is still there.
        self.assertEqual(len(player2.collab), 1)
        # They don't have a play support action with that card in it.
        support_actions = [action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport]
        for support in support_actions:
            self.assertNotEqual(support["card_id"], swap_card["game_card_id"])

        # Verify it goes back to normal
        end_turn(self)
        self.assertFalse(player2.block_movement_for_turn)
        do_cheer_step_on_card(self, player1.center[0])
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)
        baton_pass = [action for action in actions if action["action_type"] == GameAction.MainStepBatonPass]
        self.assertEqual(len(baton_pass), 1)


    def test_hbp01_005_executivesorder_lui59_no_holopower_or_hand(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-059", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)
        player1.hand = []

        # Attack with Lui's Party.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform, damage, end turn etc
        self.assertEqual(len(events), 16)
        validate_event(self, events[0], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })

    def test_hbp01_005_executivesorder_lui59_no_holopower(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-059", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)

        # Attack with Lui's Party.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        # Use the ability
        events = pick_choice(self, player1.player_id, 0)
        # Events - choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [card["game_card_id"] for card in player1.hand])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]],
        })
        events = engine.grab_events()
        # Events - move card from hand to archive, trigger 59 ability
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": cards_can_choose[0],
            "from_zone": "hand",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "from_zone": "deck",
            "to_zone": "hand",
        })
        gain_card_choices = events[2]["cards_can_choose"]
        for id in gain_card_choices:
            card, _, zone_name = player1.find_card(id)
            self.assertEqual(zone_name, "deck")
            self.assertEqual(card["card_type"], "holomem_bloom")
            self.assertEqual(card["bloom_level"], 1)

        # Just pick one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [gain_card_choices[0]],
        })
        events = engine.grab_events()
        # Events - move to hand, perform, etc.
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": gain_card_choices[0],
            "from_zone": "deck",
            "to_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, player1.player_id, {})
        self.assertEqual(player1.hand[-1]["game_card_id"], gain_card_choices[0])
        validate_event(self, events[4], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)


    def test_hbp01_005_executivesorder_lui59_no_holopower(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-059", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)

        # Attack with Lui's Party.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        # Use the ability
        events = pick_choice(self, player1.player_id, 0)
        # Events - choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [card["game_card_id"] for card in player1.hand])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]],
        })
        events = engine.grab_events()
        # Events - move card from hand to archive, trigger 59 ability
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": cards_can_choose[0],
            "from_zone": "hand",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "from_zone": "deck",
            "to_zone": "hand",
        })
        gain_card_choices = events[2]["cards_can_choose"]
        for id in gain_card_choices:
            card, _, zone_name = player1.find_card(id)
            self.assertEqual(zone_name, "deck")
            self.assertEqual(card["card_type"], "holomem_bloom")
            self.assertEqual(card["bloom_level"], 1)

        # Just pick one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [gain_card_choices[0]],
        })
        events = engine.grab_events()
        # Events - move to hand, perform, etc.
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": gain_card_choices[0],
            "from_zone": "deck",
            "to_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, player1.player_id, {})
        self.assertEqual(player1.hand[-1]["game_card_id"], gain_card_choices[0])
        validate_event(self, events[4], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)

    def test_hbp01_005_executivesorder_lui59_hashp_pass(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-059", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)

        # Attack with Lui's Party.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        # Use the ability
        events = pick_choice(self, player1.player_id, 0)
        # Events - Choice to use execute orders.
        self.assertEqual(len(events), 2)

        # Pass
        events = pick_choice(self, player1.player_id, 1)

        # Events - choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, [card["game_card_id"] for card in player1.hand])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]],
        })
        events = engine.grab_events()
        # Events - move card from hand to archive, trigger 59 ability
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": cards_can_choose[0],
            "from_zone": "hand",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "from_zone": "deck",
            "to_zone": "hand",
        })
        gain_card_choices = events[2]["cards_can_choose"]
        for id in gain_card_choices:
            card, _, zone_name = player1.find_card(id)
            self.assertEqual(zone_name, "deck")
            self.assertEqual(card["card_type"], "holomem_bloom")
            self.assertEqual(card["bloom_level"], 1)

        # Just pick one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [gain_card_choices[0]],
        })
        events = engine.grab_events()
        # Events - move to hand, perform, etc.
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": gain_card_choices[0],
            "from_zone": "deck",
            "to_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, player1.player_id, {})
        self.assertEqual(player1.hand[-1]["game_card_id"], gain_card_choices[0])
        validate_event(self, events[4], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)


    def test_hbp01_005_executivesorder_lui59_use_hp_no_archivehand(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-059": 4 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-059", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)

        # Attack with Lui's Party.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        # Use the ability
        events = pick_choice(self, player1.player_id, 0)
        # Events - Choice to use execute orders.
        self.assertEqual(len(events), 2)

        # use the ability
        top_holop = player1.holopower[0]["game_card_id"]
        events = pick_choice(self, player1.player_id, 0)

        # Events - archive 1 holopower, oshis kill, get the card ability choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": top_holop,
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "from_zone": "deck",
            "to_zone": "hand",
        })
        self.assertEqual(len(player1.holopower), 1)
        self.assertEqual(player1.archive[0]["game_card_id"], top_holop)
        gain_card_choices = events[4]["cards_can_choose"]
        for id in gain_card_choices:
            card, _, zone_name = player1.find_card(id)
            self.assertEqual(zone_name, "deck")
            self.assertEqual(card["card_type"], "holomem_bloom")
            self.assertEqual(card["bloom_level"], 1)

        # Just pick one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [gain_card_choices[0]],
        })
        events = engine.grab_events()
        # Events - move to hand, perform, etc.
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": gain_card_choices[0],
            "from_zone": "deck",
            "to_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, player1.player_id, {})
        self.assertEqual(player1.hand[-1]["game_card_id"], gain_card_choices[0])
        validate_event(self, events[4], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "luisparty",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)


    def test_hbp01_005_executivesorder_lui61_hawkrave_no_hp_nohand(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        #player1.generate_holopower(2)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        begin_performance(self)
        player1.hand = []

        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform, damage, send cheer
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_005_executivesorder_lui61_hawkrave_no_hp(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        #player1.generate_holopower(2)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        self.assertEqual(len(player1.hand), 3)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 4 choices (1,2,3, and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[3]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 2, should be 3 cards archive and deal 60 damage.
        events = pick_choice(self, player1.player_id, 2)
        # Events - choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 3,
            "amount_max": 3,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [card["game_card_id"] for card in player1.hand],
        })
        events = engine.grab_events()
        # Events - move 3 cards, deal damage choice
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2center["game_card_id"]],
        })
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2collab["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, skip damage because dead, go to next turn
        self.assertEqual(len(events), 14)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2collab["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_EndTurn, player1.player_id, {
            "ending_player_id": self.player1,
        })
        validate_event(self, events[-2], EventType.EventType_ResetStepChooseNewCenter, player1.player_id, {
            "active_player": self.player2
        })




    def test_hbp01_005_executivesorder_lui61_hawkrave_holopower2_forced_to_use_it(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        self.assertEqual(len(player1.hand), 3)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 6 choices (1,2,3,4,5 and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[5]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 4, should be 5 cards archive and deal 100 damage.
        events = pick_choice(self, player1.player_id, 4)
        # Events - forced to use executives to pay 2 holopower towards this, then we're choosing cards.
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })
        validate_event(self, events[6], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 3,
            "amount_max": 3,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [card["game_card_id"] for card in player1.hand],
        })
        events = engine.grab_events()
        # Events - move 3 cards, deal damage choice
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[6], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2collab["game_card_id"]],
        })
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2collab["game_card_id"],
            "damage": 100,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, deal damage, send cheer again since center is now dead
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2center["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": False,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_005_executivesorder_lui61_hawkrave_holopower4_can_choose_how_much(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(4)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        self.assertEqual(len(player1.hand), 3)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 6 choices (1,2,3,4,5 and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[5]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 4, should be 5 cards archive and deal 100 damage.
        events = pick_choice(self, player1.player_id, 4)
        # Events - executivesorder choice, can choose 2-4, but no pass
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(len(choice), 3) # 2,3,4 holopower
        for option in choice:
            self.assertNotEqual(option["effect_type"], EffectType.EffectType_Pass)

        # Choose 3 holopower, so we'll still discard 2 cards but have 1 holopower left.
        events = pick_choice(self, player1.player_id, 1)
        # Events - 3 hp, oshi activation, choose cards
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        self.assertEqual(len(player1.holopower), 1)
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })
        validate_event(self, events[8], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "archive",
            "amount_min": 2,
            "amount_max": 2,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        # Pick our 2 cards
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [card["game_card_id"] for card in player1.hand[1:]],
        })
        events = engine.grab_events()
        # Events - move 2 cards, deal damage choice
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {})
        validate_event(self, events[4], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[4]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2collab["game_card_id"]],
        })
        self.assertEqual(len(player1.hand), 1)
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2collab["game_card_id"],
            "damage": 100,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, deal damage, send cheer again since center is now dead
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2center["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": False,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_005_executivesorder_lui61_hawkrave_holopowerall(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(10)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        self.assertEqual(len(player1.hand), 3)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 6 choices (1,2,3,4,5 and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[5]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 4, should be 5 cards archive and deal 100 damage.
        events = pick_choice(self, player1.player_id, 4)
        # Events - executivesorder choice, can choose 2-5, but no pass
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(len(choice), 4) # 2,3,4,5 holopower
        for option in choice:
            self.assertNotEqual(option["effect_type"], EffectType.EffectType_Pass)

        # Choose 5 holopower
        events = pick_choice(self, player1.player_id, 3)
        # Events - 5 hp, oshi activation, choose cards
        self.assertEqual(len(events), 14)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[6], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        self.assertEqual(len(player1.holopower), 5)
        validate_event(self, events[10], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })

        # Skip the choose cards to archive since we did it all.
        # Straight to target choice.
        validate_event(self, events[12], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[12]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2collab["game_card_id"]],
        })
        self.assertEqual(len(player1.hand), 3)
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2collab["game_card_id"],
            "damage": 100,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, deal damage, send cheer again since center is now dead
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2center["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": False,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_005_executivesorder_lui61_hawkrave_lots_cards_all_holopower(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(10)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        add_card_to_hand(self, player1, "hSD01-010", False)
        add_card_to_hand(self, player1, "hSD01-010", False)
        add_card_to_hand(self, player1, "hSD01-010", False)
        self.assertEqual(len(player1.hand), 6)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 6 choices (1,2,3,4,5 and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[5]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 4, should be 5 cards archive and deal 100 damage.
        events = pick_choice(self, player1.player_id, 4)
        # Events - executivesorder choice, can choose 1-5 and pass
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(len(choice), 6) # 1,2,3,4,5, pass
        self.assertEqual(choice[-1]["effect_type"], EffectType.EffectType_Pass)

        # Choose 5 holopower
        events = pick_choice(self, player1.player_id, 4)
        # Events - 5 hp, oshi activation, choose cards
        self.assertEqual(len(events), 14)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[6], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        self.assertEqual(len(player1.holopower), 5)
        validate_event(self, events[10], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })

        # Skip the choose cards to archive since we did it all.
        # Straight to target choice.
        validate_event(self, events[12], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[12]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2collab["game_card_id"]],
        })
        self.assertEqual(len(player1.hand), 6)
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2collab["game_card_id"],
            "damage": 100,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, deal damage, send cheer again since center is now dead
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2center["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": False,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_005_executivesorder_lui61_hawkrave_0_cards_all_holopower(self):
        p1deck = generate_deck_with("hBP01-005", {"hBP01-061": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(10)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-061", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        p1center = player1.center[0]
        p2center = player2.center[0]
        player2.collab = [player2.backstage[0]]
        p2collab = player2.collab[0]
        player2.backstage = player2.backstage[1:]
        begin_performance(self)

        player1.hand = []
        self.assertEqual(len(player1.hand), 0)
        # Attack with Hawk Rave
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice for variable archive, should be 6 choices (1,2,3,4,5 and pass)
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, player1.player_id, {
            "effect_player_id": self.player1,
        })
        choice = events[0]["choice"]
        self.assertEqual(choice[5]["effect_type"], EffectType.EffectType_Pass)

        # Pick choice 4, should be 5 cards archive and deal 100 damage.
        events = pick_choice(self, player1.player_id, 4)
        # Events - executivesorder forced to use all 5 hp
        # Events - 5 hp, oshi activation, choose cards
        self.assertEqual(len(events), 14)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[6], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, player1.player_id, {
            "from_zone": "holopower",
            "to_zone": "archive",
        })
        self.assertEqual(len(player1.holopower), 5)
        validate_event(self, events[10], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "executivesorder",
        })

        # Skip the choose cards to archive since we did it all.
        # Straight to target choice.
        validate_event(self, events[12], EventType.EventType_Decision_ChooseHolomemForEffect, player1.player_id, {})
        cards_can_choose = events[12]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2) # center or collab
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2collab["game_card_id"]],
        })
        self.assertEqual(len(player1.hand), 0)
        events = engine.grab_events()
        # Events - deal damage, send cheer because kill
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2collab["game_card_id"],
            "damage": 100,
            "special": True,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[2]["from_options"]
        self.assertEqual(len(from_options), 1)
        placements = {
            from_options[0]: p2center["game_card_id"],
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = engine.grab_events()
        # Events - move the cheer, perform, deal damage, send cheer again since center is now dead
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": p2center["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, player1.player_id, {
            "performer_id": p1center["game_card_id"],
            "art_id": "hawkrave",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, player1.player_id, {
            "target_id": p2center["game_card_id"],
            "damage": 60,
            "special": False,
            "died": True,
            "life_lost": 1
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

if __name__ == '__main__':
    unittest.main()
