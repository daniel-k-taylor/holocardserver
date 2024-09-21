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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, pick_choice, use_oshi_action, add_card_to_archive

class Test_hbp01_holomems(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_009_konkanata_centeronly(self):
        p1deck = generate_deck_with([], {"hBP01-009": 1}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Put p1's center in the collab spot.
        player1.collab = [player1.center[0]]
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-009", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        # Give p2 a collab.
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        actions = reset_mainstep(self)
        events = engine.grab_events()

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)
        self.assertEqual(len(actions[0]["valid_targets"]), 1)
        # Collab still has expected 2 targets.
        self.assertEqual(len(actions[1]["valid_targets"]), 2)

    def test_hbp01_010_tag_missing(self):
        p1deck = generate_deck_with([], {"hBP01-010": 1}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        # Give a cheer so when collabing it doesn't end turn after first attack.
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        actions = reset_mainstep(self)
        events = engine.grab_events()
        # Do a collab with the 010.
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {"card_id": test_card["game_card_id"] })
        events = self.engine.grab_events()
        # Events: Collab, turn effect added and back to main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
            })
        validate_event(self, events[2], EventType.EventType_AddTurnEffect, self.player1, { "effect_player_id": self.player1 })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

        actions = reset_mainstep(self)

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)


        self.assertEqual(len(actions[0]["valid_targets"]), 1)

        # Perform the art.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost stat, perform art, damage dealt, performance step
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 10,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player2.center[0]["game_card_id"],
            "power": 40,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 40,
            "target_player": self.player2,
            "special": False,
        })
        events = reset_performancestep(self)

    def test_hbp01_010_tag_present(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        # Give a cheer so when collabing it doesn't end turn after first attack.
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        player1.center = []
        center_card = put_card_in_play(self, player1, "hBP01-010", player1.center)
        spawn_cheer_on_card(self, player1, center_card["game_card_id"], "white", "w2")
        actions = reset_mainstep(self)
        events = engine.grab_events()
        # Do a collab with the 010.
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {"card_id": test_card["game_card_id"] })
        events = self.engine.grab_events()
        # Events: Collab, turn effect added and back to main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
            })
        validate_event(self, events[2], EventType.EventType_AddTurnEffect, self.player1, { "effect_player_id": self.player1 })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

        actions = reset_mainstep(self)

        # Begin Performance.
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = engine.grab_events()
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3)


        self.assertEqual(len(actions[0]["valid_targets"]), 1)

        # Perform the art.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "imoffnow",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost stat, perform art, damage dealt, performance step
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 10,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "card_id": player1.center[0]["game_card_id"],
            "stat": "power",
            "amount": 20,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "imoffnow",
            "target_id": player2.center[0]["game_card_id"],
            "power": 50,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 50,
            "target_player": self.player2,
            "special": False,
        })
        events = reset_performancestep(self)


    def test_hbp01_011_baton_0cost(self):
        p1deck = generate_deck_with([], {"hBP01-011": 2}, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-011", player1.center)
        actions = reset_mainstep(self)
        # Ensure the batonpass action is in the list.
        self.assertTrue(GameAction.MainStepBatonPass in [action["action_type"] for action in actions])

        passto = player1.backstage[0]
        engine.handle_game_message(self.player1, GameAction.MainStepBatonPass,  {
            "card_id": passto["game_card_id"],
            "cheer_ids": []
        })
        events = engine.grab_events()
        # Events - move 2 cards, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "center",
            "to_zone": "backstage",
            "card_id": test_card["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": passto["game_card_id"],
        })
        reset_mainstep(self)


    def test_hbp01_012_fail_roll(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-012": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-012")
        actions = reset_mainstep(self)

        # Bloom 012, which has a bloom effect to roll a die.
        # On 3 or less, reveal a mascot, attach to any holomem, then shuffle.
        set_next_die_rolls(self, [6])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, roll die, main step.
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        actions = reset_mainstep(self)

    def test_hbp01_012_no_mascots(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-012": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-012")
        actions = reset_mainstep(self)

        # Bloom 012, which has a bloom effect to roll a die.
        # On 3 or less, reveal a mascot, attach to any holomem, then shuffle.
        set_next_die_rolls(self, [1])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, roll die, choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "amount_min": 0,
            "amount_max": 0,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        from_options = events[4]["cards_can_choose"]
        all_options = events[4]["all_card_seen"]
        self.assertEqual(len(player1.deck), len(all_options))
        self.assertEqual(len(from_options), 0)
        # Choose no cards.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": []
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

    def test_hbp01_012_attach_mascot(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-012": 2, "hBP01-116": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-012")
        actions = reset_mainstep(self)

        # Bloom 012, which has a bloom effect to roll a die.
        # On 3 or less, reveal a mascot, attach to any holomem, then shuffle.
        set_next_die_rolls(self, [1])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, roll die, choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        from_options = events[4]["cards_can_choose"]
        self.assertEqual(len(from_options), 3) # 3 to choose from
        # Choose no cards.
        chosen_card_id = from_options[0]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [chosen_card_id]
        })
        events = engine.grab_events()
        # Events choose holomem to attach.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        effect = events[0]["effect"]
        self.assertEqual(effect["effect_type"], "attach_card_to_holomem_internal")
        holomems = ids_from_cards(player1.get_holomem_on_stage())
        self.assertListEqual(cards_can_choose, holomems)

        # Choose a holomem to attach, just center.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.center[0]["game_card_id"]]
        })
        events = engine.grab_events()

        # Events - attach mascot, shuffle, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "zone_card_id": player1.center[0]["game_card_id"],
            "card_id": chosen_card_id,
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })

    def test_hbp01_012_attach_mascot_discard_prev_mascot(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-012": 2, "hBP01-116": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        already_attached = add_card_to_hand(self, player1, "hBP01-116")
        player1.hand.remove(already_attached)
        test_card["attached_support"] = [already_attached]
        bloom_card = add_card_to_hand(self, player1, "hBP01-012")
        actions = reset_mainstep(self)

        # Bloom 012, which has a bloom effect to roll a die.
        # On 3 or less, reveal a mascot, attach to any holomem, then shuffle.
        set_next_die_rolls(self, [1])
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, roll die, choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        from_options = events[4]["cards_can_choose"]
        self.assertEqual(len(from_options), 2) # 2 to choose from
        self.assertTrue(already_attached["game_card_id"] not in from_options)
        # Choose no cards.
        chosen_card_id = from_options[0]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [chosen_card_id]
        })
        events = engine.grab_events()
        # Events choose holomem to attach.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        effect = events[0]["effect"]
        self.assertEqual(effect["effect_type"], "attach_card_to_holomem_internal")
        holomems = ids_from_cards(player1.get_holomem_on_stage())
        self.assertListEqual(cards_can_choose, holomems)

        # Choose a holomem to attach, just center.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.center[0]["game_card_id"]]
        })
        events = engine.grab_events()

        # Events - attach mascot, discard previous, shuffle, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.center[0]["game_card_id"],
            "to_holomem_id": "archive",
            "attached_id": already_attached["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "zone_card_id": player1.center[0]["game_card_id"],
            "card_id": chosen_card_id,
        })
        validate_event(self, events[4], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1,
        })
        validate_event(self, events[6], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })


    def test_hbp01_013_deal_damage_no_kill(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-013": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-013")
        actions = reset_mainstep(self)

        # Bloom 013, which has a bloom effect to deal damage.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, deal damage, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "target_player": self.player2,
            "special": True,
        })
        self.assertEqual(player2.center[0]["damage"], 30)
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        actions = reset_mainstep(self)


    def test_hbp01_013_deal_damage_finish_center(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-013": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-013")
        actions = reset_mainstep(self)

        # Give enemy center damage.
        p2center = player2.center[0]
        p2center["damage"] = 50

        # Bloom 013, which has a bloom effect to deal damage.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, deal damage, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        validate_event(self, events[6], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(len(player2.life), 5)
        self.assertEqual(p2center["damage"], 80)
        actions = reset_mainstep(self)


    def test_hbp01_013_deal_damage_no_center(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-013": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        test_card = put_card_in_play(self, player1, "hBP01-010", player1.backstage)
        player1.backstage = []
        player1.center = [test_card]
        bloom_card = add_card_to_hand(self, player1, "hBP01-013")
        actions = reset_mainstep(self)

        # Remove player2 center, like we already killed it.
        player2.center = []

        # Bloom 013, which has a bloom effect to deal damage.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, deal damage, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(len(player2.life), 5)
        actions = reset_mainstep(self)


    def test_hbp01_014_deal_damage_collab_deal_damage(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-014": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        test_card = put_card_in_play(self, player1, "hBP01-014", player1.backstage)
        actions = reset_mainstep(self)

        # Give enemy center damage.
        p2center = player2.center[0]
        p2center["damage"] = 50


        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, deal damage, send cheer cause kill
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 50,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[6]["from_options"]
        to_options = events[6]["to_options"]
        p2backstage_ids = ids_from_cards(player2.backstage)
        self.assertListEqual(to_options, p2backstage_ids)
        self.assertEqual(p2center["damage"], 100)
        self.assertEqual(len(player2.life), 5)
        # Send that cheer and get back to main
        placements = {}
        placements[from_options[0]] = player2.backstage[0]["game_card_id"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements,
        })
        events = engine.grab_events()
        # Events - cheer, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": player2.backstage[0]["game_card_id"],
            "attached_id": from_options[0],
        })
        actions = reset_mainstep(self)

    def test_hbp01_014_deal_damage_collab_deal_damage_gameover(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-014": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        test_card = put_card_in_play(self, player1, "hBP01-014", player1.backstage)
        actions = reset_mainstep(self)

        # Give enemy center damage.
        p2center = player2.center[0]
        p2center["damage"] = 50
        # Zero out backstage
        player2.backstage = []


        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, deal damage, Game over
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 50,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": True,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[6], EventType.EventType_GameOver, self.player1, {
            "loser_id": self.player2,
            "reason_id": GameOverReason.GameOverReason_NoHolomemsLeft,
        })


    def test_hbp01_014_kill_effect_failscondition(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-014": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-014", player1.center)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)

        # Use attack
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, send cheer from kill
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
            "power": 100,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 100,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2center["game_card_id"],
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

    def test_hbp01_014_kill_effect_overkill(self):
        p1deck = generate_deck_with([], {"hBP01-010": 2, "hBP01-014": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-014", player1.center)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2)

        # Give p2 damage
        p2center["damage"] = 50

        # Use attack
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, send cheer from kill
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
            "power": 100,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 100,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2center["game_card_id"],
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 2,
            "life_loss_prevented": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 2,
            "amount_max": 2,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_015_playedsupport_thisturn_nosupport(self):
        p1deck = generate_deck_with([], {"hBP01-015": 2, "hSD01-016": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        support = add_card_to_hand(self, player1, "hSD01-016")
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-015", player1.center)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        # Use attack
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "ohhi",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, end turn etc.
        self.assertEqual(len(events), 16)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "ohhi",
            "target_id": p2center["game_card_id"],
            "power": 10,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": False,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)

    def test_hbp01_015_playedsupport_thisturn(self):
        p1deck = generate_deck_with([], {"hBP01-015": 2, "hSD01-016": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        support = add_card_to_hand(self, player1, "hSD01-016")
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-015", player1.center)
        p2center = player2.center[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        actions = reset_mainstep(self)

        # First play the support card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": support["game_card_id"],
        })
        events = engine.grab_events()
        # Events - play support, draw, discard, main step
        self.assertEqual(len(events), 8)
        reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        actions = reset_performancestep(self)
        # Use attack
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "ohhi",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events -boost perform, damage, end turn etc.
        self.assertEqual(len(events), 18)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "ohhi",
            "target_id": p2center["game_card_id"],
            "power": 30,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 30,
            "target_player": self.player2,
            "special": False,
        })
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)

    def test_hbp01_016_nopromise_nodraw(self):
        p1deck = generate_deck_with([], {"hBP01-016": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-016", player1.backstage)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        actions = reset_mainstep(self)

    def test_hbp01_016_promise_draw(self):
        p1deck = generate_deck_with([], {"hBP01-016": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-016", player1.backstage)
        player1.center = []
        player1.hand = []
        center_card = put_card_in_play(self, player1, "hBP01-016", player1.center)
        self.assertEqual(len(player1.hand), 0)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, draw, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 1)

    def test_hbp01_018_revealtopdeck_notpromise(self):
        p1deck = generate_deck_with([], {"hBP01-018": 1 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-018", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "piecesofmemories",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        topdeckcardid = player1.deck[0]["game_card_id"]
        # Events - before choice
        self.assertEqual(len(player1.hand), 3)
        self.assertEqual(len(events), 2)
        events = pick_choice(self, self.player1, 0)
        # Events - Reveal topdeck, perform, damage, end turn etc.
        self.assertEqual(len(events), 18)
        validate_event(self, events[0], EventType.EventType_RevealCards, self.player1, {
            "effect_player_id": self.player1,
            "source": "topdeck"
        })
        card_ids = events[0]["card_ids"]
        self.assertEqual(len(card_ids), 1)
        self.assertEqual(topdeckcardid, card_ids[0])
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "piecesofmemories",
            "target_id": player2.center[0]["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_EndTurn, self.player1, {})
        do_cheer_step_on_card(self, player2.center[0])
        self.assertEqual(len(player1.hand), 3)

    def test_hbp01_018_revealtopdeck_is_promise(self):
        p1deck = generate_deck_with([], {"hBP01-018": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-018", player1.center)
        topdeck = add_card_to_hand(self, player1, "hBP01-018")
        player1.deck.insert(0, topdeck)
        player1.hand.remove(topdeck)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "piecesofmemories",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        topdeckcardid = topdeck["game_card_id"]
        # Events - before choice
        self.assertEqual(len(player1.hand), 3)
        self.assertEqual(len(events), 2)
        events = pick_choice(self, self.player1, 0)
        # Events - Reveal topdeck, boost, draw, perform, damage, end turn etc.
        self.assertEqual(len(events), 22)
        validate_event(self, events[0], EventType.EventType_RevealCards, self.player1, {
            "effect_player_id": self.player1,
            "source": "topdeck"
        })
        card_ids = events[0]["card_ids"]
        self.assertEqual(len(card_ids), 1)
        self.assertEqual(topdeckcardid, card_ids[0])
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20
        })
        validate_event(self, events[4], EventType.EventType_Draw, self.player1, {})
        validate_event(self, events[6], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "piecesofmemories",
            "target_id": player2.center[0]["game_card_id"],
            "power": 40,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 40,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[10], EventType.EventType_EndTurn, self.player1, {})
        do_cheer_step_on_card(self, player2.center[0])
        self.assertEqual(len(player1.hand), 4)

    def test_hbp01_019_bloom_promise(self):
        p1deck = generate_deck_with([], {"hBP01-016": 3, "hBP01-019": 3, "hBP01-020": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        self.assertEqual(len(player2.life), 5)
        player1.center = []
        start_card = put_card_in_play(self, player1, "hBP01-016", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-019")
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": start_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choose cards,
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": start_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        available_to_choose = events[2]["cards_can_choose"]
        # This should only include holomem debut/bloom and only promise.
        for id in available_to_choose:
            card_id = engine.all_game_cards_map[id]
            card = engine.card_db.get_card_by_id(card_id)
            self.assertTrue(card["card_type"] in ["holomem_debut", "holomem_bloom"])
            if "bloom_level" in card:
                self.assertEqual(card["bloom_level"], 1)
            self.assertTrue("#Promise" in card["tags"])


    def test_hbp01_020_backstage_boost(self):
        p1deck = generate_deck_with([], {"hBP01-016": 3, "hBP01-019": 3, "hBP01-020": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Give p2 a collab that has lots of hp.
        p2collab = put_card_in_play(self, player2, "hSD01-006", player2.collab)
        # Remove 1 backstage just to stay consistent.
        player1.backstage = player1.backstage[:-1]
        test_card = put_card_in_play(self, player1, "hBP01-020", player1.backstage)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, choose cards,
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        available_to_choose = events[2]["cards_can_choose"]
        # This should only include holomem debut/bloom and only promise.
        for id in available_to_choose:
            card_id = engine.all_game_cards_map[id]
            card = engine.card_db.get_card_by_id(card_id)
            self.assertTrue(card["card_type"] in ["holomem_debut", "holomem_bloom"])
            if "bloom_level" in card:
                self.assertTrue(card["bloom_level"] in [1,2])
            self.assertTrue("#Promise" in card["tags"])
        # Choose one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [available_to_choose[0]]
        })
        self.assertEqual(player1.hand[-1]["game_card_id"], available_to_choose[0])
        actions = reset_mainstep(self)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "everyonetogether",
            "target_id": p2collab["game_card_id"],
        })
        events = engine.grab_events()
        # Events - add turn, 40 boost, perform, deal damage, performance step
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_AddTurnEffect, self.player1, {
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 40,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 110,
            "target_player": self.player2,
            "special": False,
        })
        actions = reset_performancestep(self)

        # Now attack with the center and we should still get a boost.
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - boost 40, perform, damage, send cheer
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 40,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 70,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })



    def test_hbp01_023_repeat_art(self):
        p1deck = generate_deck_with([], {"hBP01-023": 3, "hBP01-019": 3, "hBP01-020": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Give p2 a collab that has lots of hp.
        p2collab = put_card_in_play(self, player2, "hSD01-006", player2.collab)
        # Remove 1 backstage.
        player1.backstage = player1.backstage[:-1]
        test_card = put_card_in_play(self, player1, "hBP01-023", player1.backstage)
        actions = reset_mainstep(self)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")

        # DO a collab
        player1.hand = []
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, draw 2, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1,
        })
        self.assertEqual(len(player1.hand), 2)

        set_next_die_rolls(self, [1,1,1,1,1])
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "itwontstop",
            "target_id": p2collab["game_card_id"],
        })
        events = engine.grab_events()
        # Events - (Roll die, perform, damage) x 3 then cheer
        self.assertEqual(len(events), 22)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "itwontstop",
            "target_id": p2collab["game_card_id"],
            "power": 80,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2collab["game_card_id"],
            "damage": 80,
            "target_player": self.player2,
            "special": False,
        })

        validate_event(self, events[6], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[8], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "itwontstop",
            "target_id": p2collab["game_card_id"],
            "power": 80,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2collab["game_card_id"],
            "damage": 80,
            "target_player": self.player2,
            "special": False,
        })

        validate_event(self, events[12], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[14], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "itwontstop",
            "target_id": p2collab["game_card_id"],
            "power": 80,
        })
        validate_event(self, events[16], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2collab["game_card_id"],
            "damage": 80,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[18], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2collab["game_card_id"],
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 2,
            "life_loss_prevented": False,
        })
        validate_event(self, events[20], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 2,
            "amount_max": 2,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[20]["from_options"]
        # Send that cheer to center
        placements = {}
        placements[from_options[0]] = player2.center[0]["game_card_id"]
        placements[from_options[1]] = player2.center[0]["game_card_id"]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements,
        })
        events = engine.grab_events()
        # Events - cheer, performance step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": player2.center[0]["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player2,
            "from_holomem_id": "life",
            "to_holomem_id": player2.center[0]["game_card_id"],
            "attached_id": from_options[1],
        })
        actions = reset_performancestep(self)



    def test_hbp01_027_gift_ondamage_this_card_is_collab_reduce_damage_doublepass(self):
        p1deck = generate_deck_with([], {"hBP01-027": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])

        # For this test, p1 collab needs to be the gift card
        test_card = put_card_in_play(self, player1, "hBP01-027", player1.collab)
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        spawn_cheer_on_card(self, player2, p2collab["game_card_id"], "white", "w1")
        begin_performance(self)

        # First, attack with p2 center, pass.
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        events = pick_choice(self, self.player1, 1)
        # Events - damage, perform step
        self.assertEqual(len(events), 4)
        self.assertEqual(player1.center[0]["damage"], 30)

        # Second, attack with p2 collab, pass.
        p1center = player1.center[0]
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.collab[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        events = pick_choice(self, self.player1, 1)
        # Events - damage, send cheer cause dead
        self.assertEqual(len(events), 6)
        self.assertEqual(p1center["damage"], 60)
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hbp01_027_gift_ondamage_this_card_is_collab_reduce_damage_rollsucceed(self):
        p1deck = generate_deck_with([], {"hBP01-027": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])

        # For this test, p1 collab needs to be the gift card
        test_card = put_card_in_play(self, player1, "hBP01-027", player1.collab)
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        spawn_cheer_on_card(self, player2, p2collab["game_card_id"], "white", "w1")
        begin_performance(self)

        # First, attack with p2 center, pass.
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        set_next_die_rolls(self, [1])
        events = pick_choice(self, self.player1, 0)
        # Events - roll die, boost stat, damage, perform step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "damage_prevented",
            "amount": "all"
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 0,
            "target_player": self.player1,
            "special": False,
        })
        self.assertEqual(player1.center[0]["damage"], 0)

        # Second, attack with p2 collab, no choice.
        p1center = player1.center[0]
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.collab[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, end turn
        self.assertEqual(len(events), 16)
        self.assertEqual(p1center["damage"], 30)
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)




    def test_hBP01_031_boostpowerperholomem(self):
        p1deck = generate_deck_with([], {"hBP01-031": 3 }, [])
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
        player1.backstage = []

        put_card_in_play(self, player1, "hBP01-031", player1.center)
        put_card_in_play(self, player1, "hBP01-031", player1.backstage)
        put_card_in_play(self, player1, "hBP01-031", player1.backstage)
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "white", "w1")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "white", "w2")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "powerofpromise",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost, perform, damage, cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 60
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 110,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

    def test_hBP01_031_collab_generateholopower(self):
        p1deck = generate_deck_with([], {"hBP01-031": 3 }, [])
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
        player1.backstage = []

        put_card_in_play(self, player1, "hBP01-031", player1.center)
        put_card_in_play(self, player1, "hBP01-031", player1.backstage)
        put_card_in_play(self, player1, "hBP01-031", player1.backstage)
        collaber = player1.backstage[0]
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": player1.backstage[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, choose cards
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": collaber["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        chosen_card_id = player1.holopower[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.holopower[0]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move card, generate 1 holopower, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "hand",
            "card_id": chosen_card_id,
        })
        validate_event(self, events[2], EventType.EventType_GenerateHolopower, self.player1, {
            "generating_player_id": self.player1,
            "holopower_generated": 1
        })
        actions = reset_mainstep(self)
        self.assertEqual(player1.hand[-1]["game_card_id"], chosen_card_id)


    def test_hBP01_033_collab_restorehp_chooseholomem(self):
        p1deck = generate_deck_with([], {"hBP01-033": 3 }, [])
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
        player1.backstage = []

        put_card_in_play(self, player1, "hBP01-033", player1.center)
        put_card_in_play(self, player1, "hBP01-033", player1.backstage)
        put_card_in_play(self, player1, "hBP01-033", player1.backstage)
        collaber = player1.backstage[0]
        actions = reset_mainstep(self)
        set_next_die_rolls(self, [1])

        # Give some damage to heal
        player1.center[0]["damage"] = 40

        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": player1.backstage[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": collaber["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[4]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 3) # Only green.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]]
        })
        events = engine.grab_events()
        # Events - restore hp, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player1,
            "card_id": player1.center[0]["game_card_id"],
            "healed_amount": 20,
            "new_damage": 20,
        })
        actions = reset_mainstep(self)



    def test_hBP01_035_art_hasattachment_bonus_bloom_searchtool(self):
        p1deck = generate_deck_with([], {"hBP01-033": 3, "hBP01-035": 3, "hBP01-114": 4 }, [])
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
        bloom_from = put_card_in_play(self, player1, "hBP01-033", player1.center)

        axe = put_card_in_play(self, player1, "hBP01-114", player1.archive)
        bloom_card = add_card_to_hand(self, player1, "hBP01-035")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        actions = reset_mainstep(self)

        # Bloom for the search effect to attach.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choose cards,
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": bloom_from["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "holomem",
            "amount_min": 0,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        # Grab axe
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [axe["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - attach ask choose member
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.center[0]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - attach, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "holomem",
            "zone_card_id": player1.center[0]["game_card_id"],
            "card_id": axe["game_card_id"],
        })
        actions = reset_mainstep(self)

        # Now we have an axe, attack!
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "akirosefantasy",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - boost stat, punch self, art effect send cheer with tool
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 10,
            "target_player": self.player1,
            "special": True,
        })
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                events[4]["from_options"][0]: player1.center[0]["game_card_id"]
            }
        })
        events = engine.grab_events()
        # Events - move cheer, perform, damage, send cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": player1.center[0]["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "akirosefantasy",
            "target_id": p2center["game_card_id"],
            "power": 60,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 60,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })


    def test_hBP01_037_bloom_cheer_and_restore_self(self):
        p1deck = generate_deck_with([], {"hBP01-037": 3,"hBP01-036": 3, "hBP01-114": 4   }, [])
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
        bloom_from = put_card_in_play(self, player1, "hBP01-036", player1.center)
        bloom_from["damage"] = 70

        axe = add_card_to_hand(self, player1, "hBP01-114")
        bloom_card = add_card_to_hand(self, player1, "hBP01-037")
        bloom_from["attached_support"] = [axe]
        player1.hand = [bloom_card]
        actions = reset_mainstep(self)

        # Bloom for the effect.
        topcheer = player1.cheer_deck[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, send cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": bloom_from["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        # Pick cheer
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                topcheer: player1.center[0]["game_card_id"]
            }
        })
        events = engine.grab_events()
        # events - move cheer, restore hp, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[2], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player1,
            "card_id": bloom_card["game_card_id"],
            "healed_amount": 40,
            "new_damage": 30,
        })
        actions = reset_mainstep(self)


    def test_hBP01_041_center_or_collab(self):
        p1deck = generate_deck_with([], {"hBP01-038": 3, "hBP01-041": 3 }, [])
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
        bloom_from = put_card_in_play(self, player1, "hBP01-038", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-041")
        player1.hand = [bloom_card]
        player1.collab = [player1.backstage[0]]
        player1.backstage = player1.backstage[1:]
        actions = reset_mainstep(self)

        # Bloom for the effect.
        topcheer = player1.cheer_deck[0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, send cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": bloom_from["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        to_options = events[2]["to_options"]
        self.assertEqual(len(to_options), 2)
        self.assertEqual(to_options[0], player1.center[0]["game_card_id"])
        self.assertEqual(to_options[1], player1.collab[0]["game_card_id"])


    def test_hBP01_042_die_multiplier(self):
        p1deck = generate_deck_with([], {"hBP01-042": 3, "hBP01-041": 3 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-042", player1.center)
        set_next_die_rolls(self, [4])
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g2")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "kitraaaa",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - roll die, power boost, perform, damage, cheer
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 4,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 40,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "kitraaaa",
            "target_id": p2center["game_card_id"],
            "power": 90,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 90,
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


    def test_hBP01_043_roll_3_dice(self):
        p1deck = generate_deck_with([], {"hBP01-043": 3, "hBP01-041": 3 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-043", player1.center)
        set_next_die_rolls(self, [4,1,6])
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g2")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g3")
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g4")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "humanrabbitalityproject",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - (roll die, power boost)x 3, perform, damage, cheer
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 4,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 40,
        })
        validate_event(self, events[4], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[6], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 10,
        })
        validate_event(self, events[8], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": False,
        })
        validate_event(self, events[10], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 60,
        })
        validate_event(self, events[12], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "humanrabbitalityproject",
            "target_id": p2center["game_card_id"],
            "power": 170,
        })
        validate_event(self, events[14], EventType.EventType_DamageDealt, self.player1, {
            "damage": 170,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[16], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[18], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

    def test_hBP01_045_bloomskip(self):
        p1deck = generate_deck_with([], {"hBP01-045": 3, "hBP01-047": 3 }, [])
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
        player1.hand = []
        test_card = put_card_in_play(self, player1, "hBP01-045", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-047")
        test_card["damage"] = 30
        actions = reset_mainstep(self)
        # Validate theere is no bloom action.
        self.assertFalse(GameAction.MainStepBloom in [action["action_type"] for action in actions])

        # Lower life to 3.
        player1.life = player1.life[0:3]
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepBloom in [action["action_type"] for action in actions])

        set_next_die_rolls(self, [1])
        # Go ahead and do it.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, restore hp, roll die, send cheer from archive (nothing there, so go to main step)
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player1,
            "card_id": bloom_card["game_card_id"],
            "healed_amount": 30,
            "new_damage": 0,
        })
        validate_event(self, events[4], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        actions = reset_mainstep(self)

    def test_hBP01_045_bloomskip_hascheer_for_047(self):
        p1deck = generate_deck_with([], {"hBP01-045": 3, "hBP01-047": 3 }, [])
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
        player1.hand = []
        test_card = put_card_in_play(self, player1, "hBP01-045", player1.center)
        player1.archive = player1.cheer_deck[:9]
        player1.cheer_deck = player1.cheer_deck[9:]
        bloom_card = add_card_to_hand(self, player1, "hBP01-047")
        test_card["damage"] = 30
        actions = reset_mainstep(self)
        # Validate theere is no bloom action.
        self.assertFalse(GameAction.MainStepBloom in [action["action_type"] for action in actions])

        # Lower life to 3.
        player1.life = player1.life[0:3]
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepBloom in [action["action_type"] for action in actions])

        set_next_die_rolls(self, [1])
        # Go ahead and do it.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, restore hp, roll die, send cheer from archive
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player1,
            "card_id": bloom_card["game_card_id"],
            "healed_amount": 30,
            "new_damage": 0,
        })
        validate_event(self, events[4], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 3,
            "from_zone": "archive",
            "to_zone": "this_holomem",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                player1.archive[-1]["game_card_id"]: player1.center[0]["game_card_id"],
                player1.archive[-2]["game_card_id"]: player1.center[0]["game_card_id"],
                player1.archive[-3]["game_card_id"]: player1.center[0]["game_card_id"],
            }
        })
        events = engine.grab_events()
        self.assertEqual(len(player1.center[0]["attached_cheer"]), 3)
        reset_mainstep(self)


    def test_hBP01_046_distribute_cheer(self):
        p1deck = generate_deck_with([], {"hBP01-045": 3, "hBP01-046": 3 }, [])
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
        player1.hand = []
        test_card = put_card_in_play(self, player1, "hBP01-045", player1.center)
        player1.archive = player1.cheer_deck[:9]
        player1.cheer_deck = player1.cheer_deck[9:]
        bloom_card = add_card_to_hand(self, player1, "hBP01-046")

        # Spread cheer around.
        g1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        w1 = spawn_cheer_on_card(self, player1, player1.backstage[0]["game_card_id"], "white", "w1")
        w2 = spawn_cheer_on_card(self, player1, player1.backstage[0]["game_card_id"], "white", "w2")
        w3 = spawn_cheer_on_card(self, player1, player1.backstage[2]["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        # Go ahead and do it.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": player1.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, send cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 0,
            "amount_max": 3,
            "from_zone": "holomem",
            "to_zone": "holomem",
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                w1["game_card_id"]: player1.center[0]["game_card_id"],
                w2["game_card_id"]: player1.backstage[1]["game_card_id"],
                g1["game_card_id"]: player1.backstage[1]["game_card_id"],
            }
        })
        events = engine.grab_events()
        self.assertEqual(len(player1.center[0]["attached_cheer"]), 1)
        self.assertEqual(len(player1.backstage[0]["attached_cheer"]), 0)
        self.assertEqual(len(player1.backstage[1]["attached_cheer"]), 2)
        self.assertEqual(len(player1.backstage[2]["attached_cheer"]), 1)
        reset_mainstep(self)


    def test_hBP01_050_sendcheer_exclude_and_bodyguard(self):
        p1deck = generate_deck_with([], {"hBP01-050": 3, "hBP01-057": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        test_card = put_card_in_play(self, player1, "hBP01-050", player1.collab)
        player1.backstage = player1.backstage[2:]
        lui = put_card_in_play(self, player1, "hBP01-057", player1.backstage)
        lui2 = put_card_in_play(self, player1, "hBP01-057", player1.backstage)

        w1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        w2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "illgiveyouallmyenergy",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - send cheer
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        from_options = events[0]["from_options"]
        to_options = events[0]["to_options"]
        self.assertTrue(test_card["game_card_id"] not in to_options)
        self.assertTrue(lui["game_card_id"] in to_options)
        self.assertTrue(lui2["game_card_id"] in to_options)
        self.assertEqual(len(to_options), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: to_options[0]
            }
        })
        events = engine.grab_events()
        # Events - move cheer, perform, damage, performance step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {})
        actions = reset_performancestep(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepEndTurn, {})
        do_cheer_step_on_card(self, player2.backstage[0])
        engine.handle_game_message(self.player2, GameAction.MainStepCollab, {
            "card_id": player2.backstage[0]["game_card_id"]
        })
        events = engine.grab_events()
        self.assertEqual(len(events), 4)
        begin_performance(self)
        # Normally there would be options to attack center or collab, but Iroha bodyguards the center.
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 3) # 2 attacks to collab and end turn.
        self.assertListEqual(actions[0]["valid_targets"], [test_card["game_card_id"]])
        self.assertListEqual(actions[1]["valid_targets"], [test_card["game_card_id"]])
        # Make iroha weak so we insta kill her.
        test_card["damage"] = test_card["hp"] - 10
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, down, cheer
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {})
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                events[6]["from_options"][0]: player1.center[0]["game_card_id"]
            }
        })
        events = engine.grab_events()
        # Events - move cheer, next attack.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        actions = reset_performancestep(self)
        self.assertEqual(len(actions), 2) # 1 attack to center now that iroha is dead and end turn.
        self.assertListEqual(actions[0]["valid_targets"], [player1.center[0]["game_card_id"]])


    def test_hBP01_051_powerboost_per_attached_cheer_collab(self):
        p1deck = generate_deck_with([], {"hBP01-051": 3, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[1:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-051", player1.collab)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g3")
        g4 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g4")
        g5 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g5")
        w2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        w3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "bundleupyourcheers",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - boost, perform, damage, down send cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 100
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "bundleupyourcheers",
            "target_id": p2center["game_card_id"],
            "power": 150,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 150
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {})

    def test_hBP01_051_powerboost_per_attached_cheer_nocollab_noboost(self):
        p1deck = generate_deck_with([], {"hBP01-051": 3, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[1:]
        player1.collab = player1.center
        player1.center = []
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-051", player1.center)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g3")
        g4 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g4")
        g5 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g5")
        w2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w2")
        w3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "white", "w3")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "bundleupyourcheers",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, perform step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "bundleupyourcheers",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 50
        })
        reset_performancestep(self)


    def test_hBP01_052_movecheerbetweenmems_target_tag(self):
        p1deck = generate_deck_with([], {"hBP01-052": 3, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[2:]
        player1.collab = player1.center
        player1.center = []
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-052", player1.center)
        otherid = put_card_in_play(self, player1, "hBP01-052", player1.backstage)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "selamatpagi",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - move cheer between mems only to ID though.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {})
        to_options = events[0]["to_options"]
        from_options = events[0]["from_options"]
        self.assertEqual(len(to_options), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[0]: to_options[1]
            }
        })
        events = engine.grab_events()
        # Events - move cheer, perform, damage, perform step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {})
        reset_performancestep(self)
        self.assertEqual(otherid["attached_cheer"][0]["game_card_id"], from_options[0])


    def test_hBP01_055_exclude_powerboost_no_other_id(self):
        p1deck = generate_deck_with([], {"hBP01-052": 2,"hBP01-055": 2, }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[2:]
        player1.collab = player1.center
        player1.center = []
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-055", player1.center)
        otherid = put_card_in_play(self, player1, "hBP01-052", player1.backstage)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g3")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "relationsky",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, down, send cheer
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 100,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[6], EventType.EventType_Decision_SendCheer, self.player1, {})

    def test_hBP01_055_exclude_powerboost_has_non_airani_id(self):
        p1deck = generate_deck_with([], {"hBP01-052": 2,"hBP01-055": 2, "hBP01-088": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[3:]
        player1.collab = player1.center
        player1.center = []
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-055", player1.center)
        otherid = put_card_in_play(self, player1, "hBP01-052", player1.backstage)
        moona = put_card_in_play(self, player1, "hBP01-088", player1.backstage)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g3")
        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "relationsky",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - boost, perform, damage, down, send cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 50
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 150,
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {})


    def test_hBP01_055_sendcheer_archive_onepermember_limit(self):
        p1deck = generate_deck_with([], {"hBP01-052": 2,"hBP01-055": 2, "hBP01-088": 2}, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[3:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-055", player1.backstage)
        otherid = put_card_in_play(self, player1, "hBP01-052", player1.backstage)
        moona = put_card_in_play(self, player1, "hBP01-088", player1.backstage)
        g1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g3")
        player1.archive = player1.cheer_deck[:5]
        player1.cheer_deck = player1.cheer_deck[5:]
        actions = reset_mainstep(self)

        # Collab for effect.
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, send cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {})
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {})
        from_options = events[2]["from_options"]
        to_options = events[2]["to_options"]
        self.assertEqual(len(from_options), 5)
        self.assertEqual(len(to_options), 3)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                from_options[1]: test_card["game_card_id"],
                from_options[4]: otherid["game_card_id"],
                from_options[3]: moona["game_card_id"],
            }
        })
        events = engine.grab_events()
        # events - 3 move cheer, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_MoveAttachedCard, self.player1, {})
        validate_event(self, events[4], EventType.EventType_MoveAttachedCard, self.player1, {})
        reset_mainstep(self)

    def test_hBP01_057_lui_collab_snipe_nocollab(self):
        p1deck = generate_deck_with([], {"hBP01-057": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-057", player1.backstage)
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, main step (there was no target)
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        actions = reset_mainstep(self)

    def test_hBP01_057_lui_collab_snipe_target(self):
        p1deck = generate_deck_with([], {"hBP01-057": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        player2.collab = [player2.backstage[0]]
        player2.backstage = player2.backstage[1:]
        p2collab = player2.collab[0]
        test_card = put_card_in_play(self, player1, "hBP01-057", player1.backstage)
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, deal damage, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 10,
            "target_player": self.player2,
            "special": True,
        })
        actions = reset_mainstep(self)



    def test_hBP01_065_remainingcards_archive(self):
        p1deck = generate_deck_with([], {"hBP01-065": 3, "hBP01-063": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        test_card = put_card_in_play(self, player1, "hBP01-063", player1.backstage)
        bloom_card = add_card_to_hand(self, player1, "hBP01-065")

        td1 = add_card_to_hand(self, player1, "hBP01-063")
        td2 = add_card_to_hand(self, player1, "hBP01-065")
        td3 = add_card_to_hand(self, player1, "hBP01-065")
        player1.deck.insert(0, td1)
        player1.deck.insert(0, td2)
        player1.deck.insert(0, td3)
        player1.hand.remove(td1)
        player1.hand.remove(td2)
        player1.hand.remove(td3)
        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choose cards
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {})
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {})
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 3)
        self.assertTrue(td1["game_card_id"] in cards_can_choose)
        self.assertTrue(td2["game_card_id"] in cards_can_choose)
        self.assertTrue(td3["game_card_id"] in cards_can_choose)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [td1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move to hand, move 2 to archive, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {})
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {})
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {})
        reset_mainstep(self)
        self.assertEqual(player1.hand[-1]["game_card_id"], td1["game_card_id"])
        self.assertEqual(len(player1.archive), 2)
        self.assertTrue(td2["game_card_id"] in ids_from_cards(player1.archive))
        self.assertTrue(td3["game_card_id"] in ids_from_cards(player1.archive))


    def test_hBP01_066_hasstacked_none(self):
        p1deck = generate_deck_with([], {"hBP01-066": 3, "hBP01-063": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-066", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "kneel",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform, damage, down, cheer
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 40
        })
        reset_performancestep(self)


    def test_hBP01_066_hasstacked_ability(self):
        p1deck = generate_deck_with([], {"hBP01-066": 3, "hBP01-063": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-066", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")

        stack1 = add_card_to_hand(self, player1, "hBP01-063")
        stack2 = add_card_to_hand(self, player1, "hBP01-063")
        test_card["stacked_cards"] = [stack1, stack2]
        player1.hand.remove(stack1)
        player1.hand.remove(stack2)
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "kneel",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Events - choose cards from stacked.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {})
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2)
        self.assertTrue(stack1["game_card_id"] in cards_can_choose)
        self.assertTrue(stack2["game_card_id"] in cards_can_choose)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [stack1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move card to archive, deal damage to collab, perform, damage, next perf
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": test_card["game_card_id"],
            "to_zone": "archive",
            "card_id": stack1["game_card_id"],
        })
        self.assertEqual(player1.archive[0]["game_card_id"], stack1["game_card_id"])
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 40,
            "special": True,
            "target_id": p2collab["game_card_id"],
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 40,
            "special": False
        })
        reset_performancestep(self)


    def test_hBP01_067_boostperarchived_shuffleintodeck(self):
        p1deck = generate_deck_with([], {"hBP01-067": 3, "hBP01-063": 3,"hBP01-103": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-067", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")

        stack1 = add_card_to_hand(self, player1, "hBP01-063")
        stack2 = add_card_to_hand(self, player1, "hBP01-063")
        junk1 = add_card_to_hand(self, player1, "hBP01-103")
        junk2 = add_card_to_hand(self, player1, "hBP01-103")
        junk3 = add_card_to_hand(self, player1, "hBP01-103")
        player1.archive = [stack1, stack2, junk1, junk2, junk3]
        player1.hand = []
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "majesticphoenix",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - power boost per archived, choose cards to shuffle
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "amount_min": 2,
            "amount_max": 2
        })
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2)
        self.assertTrue(stack1["game_card_id"] in cards_can_choose)
        self.assertTrue(stack2["game_card_id"] in cards_can_choose)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": cards_can_choose
        })
        events = engine.grab_events()
        # Events - move card to deck x 2, shuffle, perform, damage, down, cheer
        self.assertEqual(len(events), 14)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "deck",
            "card_id": cards_can_choose[0],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "deck",
            "card_id": cards_can_choose[1],
        })
        validate_event(self, events[4], EventType.EventType_ShuffleDeck, self.player1, {})
        validate_event(self, events[6], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "damage": 100,
            "special": False
        })
        validate_event(self, events[10], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[12], EventType.EventType_Decision_SendCheer, self.player1, {})
        self.assertTrue(junk1["game_card_id"] in ids_from_cards(player1.archive))
        self.assertTrue(junk2["game_card_id"] in ids_from_cards(player1.archive))
        self.assertTrue(junk3["game_card_id"] in ids_from_cards(player1.archive))
        self.assertTrue(stack1["game_card_id"] in ids_from_cards(player1.deck))
        self.assertTrue(stack2["game_card_id"] in ids_from_cards(player1.deck))


    def test_hBP01_070_needs_zain(self):
        p1deck = generate_deck_with([], {"hBP01-070": 3, "hBP01-126": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-070", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r2")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r3")

        zain = add_card_to_hand(self, player1, "hBP01-126")
        actions = reset_mainstep(self)
        actions = begin_performance(self)
        self.assertEqual(len(actions), 2) # No polka.


    def test_hBP01_070_has_zain(self):
        p1deck = generate_deck_with([], {"hBP01-070": 3, "hBP01-126": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-070", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")

        zain = add_card_to_hand(self, player1, "hBP01-126")
        test_card["attached_support"].append(zain)
        player1.hand = []
        actions = reset_mainstep(self)
        actions = begin_performance(self)
        self.assertEqual(len(actions), 3)


    def test_hBP01_071_boost_per_fans(self):
        p1deck = generate_deck_with([], {"hBP01-071": 3, "hBP01-126": 4, "hBP01-116": 2 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        # Prepopulate the top deck
        self.assertEqual(len(player1.archive), 0)
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-071", player1.center)

        z1 = put_card_in_play(self, player1, "hBP01-126", test_card["attached_support"])
        z2 = put_card_in_play(self, player1, "hBP01-126", test_card["attached_support"])
        z3 = put_card_in_play(self, player1, "hBP01-126", player1.backstage[0]["attached_support"])
        z4 = put_card_in_play(self, player1, "hBP01-126", player1.backstage[1]["attached_support"])
        m1 = put_card_in_play(self, player1, "hBP01-116", test_card["attached_support"])
        m2 = put_card_in_play(self, player1, "hBP01-116", player1.collab[0]["attached_support"])

        actions = reset_mainstep(self)
        actions = begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "polkacircus",
            "target_id": player2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - boost, boost, perform, damage, down, cheer
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 10 # Upao
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 80 # 4 fans in play
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {})
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "damage": 140
        })
        validate_event(self, events[8], EventType.EventType_DownedHolomem, self.player1, {})
        validate_event(self, events[10], EventType.EventType_Decision_SendCheer, self.player1, {})


    def test_hBP01_072_self_has_cheer_color_failed(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-072", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "green", "g1")
        actions = reset_mainstep(self)
        begin_performance(self)
        set_next_die_rolls(self, [1])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "wazzup",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # No bonus since not red, perform, damage, performance step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "wazzup",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": False,
        })
        reset_performancestep(self)


    def test_hBP01_072_self_has_cheer_color_success(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-072", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        actions = reset_mainstep(self)
        begin_performance(self)
        set_next_die_rolls(self, [1])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "wazzup",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # roll die, deal damage to collab, perform, damage, performance step
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2collab["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "wazzup",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": False,
        })
        reset_performancestep(self)


    def test_hBP01_074_bloom_choose_not_en_no_snipe(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3, "hBP01-074": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-072", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-074")
        archived_card = add_card_to_archive(self, player1, "hSD01-006")
        self.assertEqual(len(player1.archive), 1)
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - Bloom, Choose cards from archive
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "archive",
            "to_zone": "hand",
            "amount_min": 0,
            "amount_max": 1,
            "remaining_cards_action": "nothing"
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [archived_card["game_card_id"]],
        })
        events = engine.grab_events()
        # Events - move card to hand, main step
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "hand",
            "zone_card_id": "",
            "card_id": archived_card["game_card_id"],
        })
        actions = reset_mainstep(self)


    def test_hBP01_074_bloom_choose_en_do_snipe(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3, "hBP01-074": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        p2center = player2.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-072", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-074")
        archived_card = add_card_to_archive(self, player1, "hBP01-072")
        self.assertEqual(len(player1.archive), 1)
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - Bloom, Choose cards from archive
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "archive",
            "to_zone": "hand",
            "amount_min": 0,
            "amount_max": 1,
            "remaining_cards_action": "nothing"
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [archived_card["game_card_id"]],
        })
        events = engine.grab_events()
        # Events - move card to hand, deal damage to collab, main step
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "archive",
            "to_zone": "hand",
            "zone_card_id": "",
            "card_id": archived_card["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2collab["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": True,
        })
        actions = reset_mainstep(self)


    def test_hBP01_075_collab_orderanddraw(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3, "hBP01-075": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-075", player1.backstage)
        actions = reset_mainstep(self)

        self.assertEqual(len(player2.hand), 2)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - Collab, order cards p1,
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "bottom": True,
        })
        card_ids = events[2]["card_ids"]
        self.assertListEqual(card_ids, [card["game_card_id"] for card in player1.hand])
        self.assertEqual(len(player1.hand), 3)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, {
            "card_ids": card_ids
        })
        # events - move the 3 hand cards to deck, draw cards, p2 order cards
        events = engine.grab_events()
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[0],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[1],
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[2],
        })
        validate_event(self, events[6], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1,
        })
        self.assertEqual(len(player1.hand), 3)
        self.assertFalse(any(card_id in [card["game_card_id"] for card in player1.hand] for card_id in card_ids))
        p1newhand_ids = ids_from_cards(player1.hand)
        validate_event(self, events[8], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player2,
            "from_zone": "hand",
            "to_zone": "deck",
            "bottom": True,
        })
        hidden_card_ids = events[8]["card_ids"]
        self.assertListEqual(hidden_card_ids, ["HIDDEN", "HIDDEN"])
        # Begin p2 ordering
        card_ids = events[9]["card_ids"]
        self.assertListEqual(card_ids, [card["game_card_id"] for card in player2.hand])
        self.assertEqual(len(player2.hand), 2)
        engine.handle_game_message(self.player2, GameAction.EffectResolution_OrderCards, {
            "card_ids": card_ids
        })
        # events - move the 2 cards, draw cards, main step
        events = engine.grab_events()
        self.assertEqual(len(events), 8)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[0],
        })
        validate_event(self, events[3], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[1],
        })
        validate_event(self, events[4], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player2,
        })
        self.assertEqual(len(player2.hand), 2)
        self.assertFalse(any(card_id in [card["game_card_id"] for card in player2.hand] for card_id in card_ids))
        self.assertListEqual(ids_from_cards(player1.hand), p1newhand_ids)
        reset_mainstep(self)

    def test_hBP01_075_collab_orderanddraw_p2empty(self):
        p1deck = generate_deck_with([], {"hBP01-072": 3, "hBP01-075": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-075", player1.backstage)
        actions = reset_mainstep(self)

        player2.hand = []
        self.assertEqual(len(player2.hand), 0)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - Collab, order cards p1,
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "bottom": True,
        })
        card_ids = events[2]["card_ids"]
        self.assertListEqual(card_ids, [card["game_card_id"] for card in player1.hand])
        self.assertEqual(len(player1.hand), 3)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, {
            "card_ids": card_ids
        })
        # events - move the 3 hand cards to deck, draw cards, main step
        events = engine.grab_events()
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[0],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[1],
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "zone_card_id": "",
            "card_id": card_ids[2],
        })
        validate_event(self, events[6], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1,
        })
        self.assertEqual(len(player1.hand), 3)
        self.assertFalse(any(card_id in [card["game_card_id"] for card in player1.hand] for card_id in card_ids))
        p1newhand_ids = ids_from_cards(player1.hand)
        self.assertListEqual(ids_from_cards(player1.hand), p1newhand_ids)
        self.assertEqual(len(player2.hand), 0)
        reset_mainstep(self)

    def test_hBP01_076_suisei_back_snipe(self):
        p1deck = generate_deck_with([], {"hBP01-076": 3 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g4")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - before art back snipe
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        self.assertListEqual(cards_can_choose, backstage_options)

        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[1]]
        })
        events = engine.grab_events()
        # Events - deal damage, perform, damage, end turn
        self.assertEqual(len(events), 18)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)


    def test_hBP01_076_suisei_back_snipe_no_options(self):
        p1deck = generate_deck_with([], {"hBP01-076": 3 }, [])
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
        player2.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g4")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - perform, damage, end turn
        self.assertEqual(len(events), 16)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)


    def test_hBP01_076_suisei_back_snipe_kill(self):
        p1deck = generate_deck_with([], {"hBP01-076": 3 }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g4")
        actions = reset_mainstep(self)
        begin_performance(self)
        p2center = player2.center[0]
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - before art back snipe
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        self.assertListEqual(cards_can_choose, backstage_options)

        sniped = player2.backstage[1]
        player2.backstage[1]["damage"] = player2.backstage[1]["hp"] - 10
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[1]]
        })
        events = engine.grab_events()
        # Events - deal damage, perform art, turn etc. (no cheer because no life loss)
        self.assertEqual(len(events), 20)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": sniped["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": sniped["game_card_id"],
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)
        self.assertEqual(player2.archive[0]["game_card_id"], sniped["game_card_id"])


    def test_hBP01_077_suisei_oshi_archive_cheer_from_mem_has0(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-077": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-077", player1.backstage)
        actions = reset_mainstep(self)

        # Collab
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        actions = reset_mainstep(self)


    def test_hBP01_077_suisei_oshi_archive_cheer_from_mem_has1(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-077": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-077", player1.backstage)
        b1 = spawn_cheer_on_card(self, player1, player1.backstage[-1]["game_card_id"], "blue", "b1")
        actions = reset_mainstep(self)

        # Collab
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        choice = events[2]["choice"]
        self.assertEqual(len(player1.hand), 3)
        self.assertEqual(len(choice), 2) # Use ability or pass
        events = pick_choice(self, self.player1, 0)
        # Events - only 1 cheer, so it happens, draw 2, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": test_card["game_card_id"],
            "to_holomem_id": "archive",
            "attached_id": b1["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        self.assertEqual(len(player1.hand), 5)
        self.assertEqual(player1.archive[0]["game_card_id"], b1["game_card_id"])
        actions = reset_mainstep(self)

    def test_hBP01_077_suisei_oshi_archive_cheer_from_mem_has3(self):
        p1deck = generate_deck_with("hBP01-007", {"hBP01-077": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-077", player1.backstage)
        b1 = spawn_cheer_on_card(self, player1, player1.backstage[-1]["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, player1.backstage[-1]["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, player1.backstage[-1]["game_card_id"], "blue", "b3")
        actions = reset_mainstep(self)

        # Collab
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - collab, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        choice = events[2]["choice"]
        self.assertEqual(len(player1.hand), 3)
        self.assertEqual(len(choice), 2) # Use ability or pass
        events = pick_choice(self, self.player1, 0)
        # Events - 3 cheer so choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
            "remaining_cards_action": "nothing"
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move cheer, draw 2, main step
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": test_card["game_card_id"],
            "to_zone": "archive",
            "zone_card_id": "",
            "card_id": b2["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        self.assertEqual(len(player1.hand), 5)
        self.assertEqual(len(test_card["attached_cheer"]), 2)
        self.assertEqual(player1.archive[0]["game_card_id"], b2["game_card_id"])
        actions = reset_mainstep(self)

    def test_hBP01_079_suisei_bloom_snipe_kill(self):
        p1deck = generate_deck_with([], {"hBP01-076": 3,"hBP01-079": 3  }, [])
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
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-079")
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, snipe
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[2]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        self.assertListEqual(cards_can_choose, backstage_options)

        sniped = player2.backstage[2]
        player2.backstage[2]["damage"] = player2.backstage[1]["hp"] - 10
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[2]]
        })
        events = engine.grab_events()
        # Events - deal damage, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": sniped["game_card_id"],
            "damage": 20,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": sniped["game_card_id"],
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        actions = reset_mainstep(self)

    def test_hBP01_080_down_holomem(self):
        p1deck = generate_deck_with([], {"hBP01-080": 3,"hBP01-079": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-080", player1.backstage)
        player2.center[0]["damage"] = 40
        player2.backstage[1]["damage"] = 40
        p2target = player2.backstage[1]
        actions = reset_mainstep(self)

        set_next_die_rolls(self, [5])
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, roll die, automatic since only 1 so down them, no cheer since prevented, so main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 5,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2target["game_card_id"],
            "target_player": self.player2,
            "life_lost": 0,
            "life_loss_prevented": True,
            "game_over": False,
        })
        reset_mainstep(self)


    def test_hBP01_080_down_holomem_2_options(self):
        p1deck = generate_deck_with([], {"hBP01-080": 3,"hBP01-079": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-080", player1.backstage)
        player2.center[0]["damage"] = 40
        player2.backstage[1]["damage"] = 40
        player2.backstage[2]["damage"] = 40
        p2target = player2.backstage[2]
        actions = reset_mainstep(self)

        set_next_die_rolls(self, [5])
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, roll die, choose cards
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 5,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [p2target["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - down, no cheer, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DownedHolomem, self.player1, {
            "target_id": p2target["game_card_id"],
            "target_player": self.player2,
            "life_lost": 0,
            "life_loss_prevented": True,
            "game_over": False,
        })
        reset_mainstep(self)


    def test_hBP01_081_collabsendcheer_toblue(self):
        p1deck = generate_deck_with([], {"hBP01-081": 3,"hBP01-079": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-081", player1.backstage)
        player1.center = []
        other_card = put_card_in_play(self, player1, "hBP01-081", player1.center)
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, send cheer with 2 options
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
        })
        to_options = events[2]["to_options"]
        self.assertEqual(to_options[0], other_card["game_card_id"])
        self.assertEqual(to_options[1], test_card["game_card_id"])


    def test_hBP01_085_damage_multiple_less_than_allowed(self):
        p1deck = generate_deck_with([], {"hBP01-085": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[1:]
        test_card = put_card_in_play(self, player1, "hBP01-085", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")

        p1center = player1.center[0]
        p2center = player2.center[0]

        # Setup opponent stage.
        # Make it so there are only 2 backstage.
        player2.backstage = player2.backstage[:2]

        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - deal damage to 3 backstage, only 2 so 2 just happen, then perform, damage, perform step.
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[4], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "special": False,
            "damage": 50,
        })
        reset_performancestep(self)


    def test_hBP01_085_damage_multiple_exactly_3(self):
        p1deck = generate_deck_with([], {"hBP01-085": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[1:]
        test_card = put_card_in_play(self, player1, "hBP01-085", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")

        p1center = player1.center[0]
        p2center = player2.center[0]

        # Setup opponent stage.
        # Make it so there are only 3 backstage.
        player2.backstage = player2.backstage[:3]

        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - deal damage to 3 backstage, only 2 so 2 just happen, then perform, damage, perform step.
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[6], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "special": False,
            "damage": 50,
        })
        reset_performancestep(self)

    def test_hBP01_085_damage_multiple_morethan_3(self):
        p1deck = generate_deck_with([], {"hBP01-085": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[1:]
        test_card = put_card_in_play(self, player1, "hBP01-085", player1.center)
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")

        p1center = player1.center[0]
        p2center = player2.center[0]

        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Events - deal damage choose cards
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, ids_from_cards(player2.backstage))
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player2.backstage[3]["game_card_id"], player2.backstage[1]["game_card_id"], player2.backstage[2]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - deal damage to 3 backstage, only 2 so 2 just happen, then perform, damage, perform step.
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[3]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[6], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "raindrops",
            "target_id": p2center["game_card_id"],
            "power": 50,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "special": False,
            "damage": 50,
        })
        reset_performancestep(self)


    def test_hBP01_086_damage_bloom_nocheer_no_multiple_all(self):
        p1deck = generate_deck_with([], {"hBP01-086": 3, "hBP01-082": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[1:]
        test_card = put_card_in_play(self, player1, "hBP01-082", player1.center)
        #spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        #spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        bloom_card = add_card_to_hand(self, player1, "hBP01-086")

        p1center = player1.center[0]
        p2center = player2.center[0]

        actions = reset_mainstep(self)

        # Do the bloom
        # No cheer, on an ID character, so pass the effect.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": p1center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, mainstep
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": p1center["game_card_id"],
            "bloom_from_zone": "hand",
        })
        actions = reset_mainstep(self)

    def test_hBP01_086_damage_bloom_exactly1cheer_multiple_all(self):
        p1deck = generate_deck_with([], {"hBP01-086": 3, "hBP01-082": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[1:]
        test_card = put_card_in_play(self, player1, "hBP01-082", player1.center)
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        #spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        bloom_card = add_card_to_hand(self, player1, "hBP01-086")

        p1center = player1.center[0]
        p2center = player2.center[0]

        actions = reset_mainstep(self)

        # Do the bloom
        # No cheer, on an ID character, so pass the effect.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": p1center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": p1center["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Events - auto choose the cheer, deal damage to all backstage, main step
        self.assertEqual(len(events), 14)
        # Move cheer first
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.center[0]["game_card_id"],
            "to_holomem_id": "archive",
            "attached_id": b1["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[3]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[4]["game_card_id"],
            "special": True,
            "damage": 10,
        })

        actions = reset_mainstep(self)


    def test_hBP01_086_damage_bloom_cheeron2holomems_multiple_all(self):
        p1deck = generate_deck_with([], {"hBP01-086": 3, "hBP01-082": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[2:]
        test_card = put_card_in_play(self, player1, "hBP01-082", player1.center)
        otherbackid = put_card_in_play(self, player1, "hBP01-082", player1.backstage)
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, otherbackid["game_card_id"], "blue", "b2")
        #spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")
        bloom_card = add_card_to_hand(self, player1, "hBP01-086")

        p1center = player1.center[0]
        p2center = player2.center[0]

        actions = reset_mainstep(self)

        # Do the bloom
        # No cheer, on an ID character, so pass the effect.
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": p1center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": p1center["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {})
        events = pick_choice(self, self.player1, 0)
        # Events - choose cheer cards to discard.
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
        })
        from_options = events[0]["from_options"]
        to_options = events[0]["to_options"]
        self.assertEqual(len(to_options), 1)
        self.assertEqual(to_options[0], "archive")
        self.assertEqual(len(from_options), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": {
                b2["game_card_id"]: "archive"
            }
        })
        events = engine.grab_events()
        # Events - move cheer, deal damage to all backstage, main step
        self.assertEqual(len(events), 14)
        # Move cheer first
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.backstage[-1]["game_card_id"],
            "to_holomem_id": "archive",
            "attached_id": b2["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[3]["game_card_id"],
            "special": True,
            "damage": 10,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[4]["game_card_id"],
            "special": True,
            "damage": 10,
        })

        actions = reset_mainstep(self)


    def test_hBP01_087_rainmantra_archiveanycolor(self):
        p1deck = generate_deck_with([], {"hBP01-087": 3, "hBP01-082": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        player1.backstage = player1.backstage[2:]
        test_card = put_card_in_play(self, player1, "hBP01-087", player1.center)
        b1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        r1 = spawn_cheer_on_card(self, player1, test_card["game_card_id"], "red", "r1")
        #spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b2")

        p1center = player1.center[0]
        p2center = player2.center[0]

        actions = reset_mainstep(self)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "rainmantra",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Choice
        events = pick_choice(self, self.player1, 0)
        # Events - choose cheer cards to discard.
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [r1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move cheer, deal damage to all backstage, perform, damage, perform step.
        self.assertEqual(len(events), 18)
        # Move cheer first
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": test_card["game_card_id"],
            "to_zone": "archive",
            "zone_card_id": "",
            "card_id": r1["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "special": True,
            "damage": 20,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[1]["game_card_id"],
            "special": True,
            "damage": 20,
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "special": True,
            "damage": 20,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[3]["game_card_id"],
            "special": True,
            "damage": 20,
        })
        validate_event(self, events[10], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[4]["game_card_id"],
            "special": True,
            "damage": 20,
        })
        validate_event(self, events[12], EventType.EventType_PerformArt, self.player1, {
            "power": 40,
        })
        validate_event(self, events[14], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "special": False,
            "damage": 40,
        })

        actions = reset_performancestep(self)


    def test_hBP01_090_bloom_choosecards_requirement_colors(self):
        p1deck = generate_deck_with([], {"hBP01-089": 3,"hBP01-090": 3  }, {
            "hY02-001": 7,
            "hY04-001": 7,
            "hY01-001": 6,
        })
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
        test_card = put_card_in_play(self, player1, "hBP01-089", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-090")
        actions = reset_mainstep(self)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, send cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "cheer_deck",
            "to_zone": "holomem"
        })
        cards_can_choose = events[2]["cards_can_choose"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]]
        })
        chosen_cheer = cards_can_choose[0]
        events = engine.grab_events()
        # Choose holomem
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 6)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player1.backstage[2]["game_card_id"]]
        })
        events = engine.grab_events()
        # Move cheer, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "zone_card_id": player1.backstage[2]["game_card_id"],
            "card_id": chosen_cheer,
        })
        reset_mainstep(self)

    def test_hBP01_091_hascheer_colors(self):
        p1deck = generate_deck_with([], {"hBP01-091": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-091", player1.center)
        p2center = player2.center[0]
        p2collab = player2.backstage[0]
        player2.collab = [p2collab]
        player2.backstage = player2.backstage[1:]
        g1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g4")
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b2")
        w2 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "white", "w2")
        actions = reset_mainstep(self)
        begin_performance(self)
        # Attack
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "moonnightdiva",
            "target_id": p2center["game_card_id"],
        })
        events = engine.grab_events()
        # Choice to use ability, do it.
        events = pick_choice(self, self.player1, 0)
        # Events - before archive cheer
        validate_event(self, events[0], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "holomem",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertTrue(b1["game_card_id"] in cards_can_choose)
        self.assertTrue(b2["game_card_id"] in cards_can_choose)
        self.assertTrue(g1["game_card_id"] in cards_can_choose)
        self.assertFalse(w2["game_card_id"] in cards_can_choose)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move card to archive, damage choice
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": test_card["game_card_id"],
            "to_zone": "archive",
            "card_id": b1["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {})
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [player2.backstage[2]["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - bonus damage, perform, damage, down, send cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[2]["game_card_id"],
            "damage": 30,
            "target_player": self.player2,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "moonnightdiva",
            "target_id": p2center["game_card_id"],
            "power": 80,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 80,
            "target_player": self.player2,
            "special": False,
        })
        validate_event(self, events[6], EventType.EventType_DownedHolomem, self.player1, {
            "game_over": False,
            "target_player": self.player2,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {})


    def test_hBP01_092_sendcheer_self_nootherpromise(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-092", player1.center)
        p1center = player1.center[0]
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        g1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - (can't send cheer no targets), perform, damage, perform step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
            "power": 10,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": False,
        })
        reset_performancestep(self)


    def test_hBP01_092_sendcheer_self_one_promise(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-092", player1.center)
        player1.backstage = player1.backstage[:1]
        testcard2 = put_card_in_play(self, player1, "hBP01-092", player1.backstage)
        p1center = player1.center[0]
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        g1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - send cheer effect, 2 cheer 1 target
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 0,
            "amount_max": 1,
            "from_zone": "holomem",
            "to_zone": "holomem",
        })
        from_options = events[0]["from_options"]
        self.assertEqual(len(from_options), 2)
        to_options = events[0]["to_options"]
        self.assertEqual(len(to_options), 1)

        placements = {}
        placements[from_options[0]] = testcard2["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements,
        })
        events = engine.grab_events()
        # Events - move cheer, perform, damage, perform step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.center[0]["game_card_id"],
            "to_holomem_id": testcard2["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
            "power": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": False,
        })
        reset_performancestep(self)


    def test_hBP01_092_sendcheer_self_2promise(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-092", player1.center)
        player1.backstage = player1.backstage[:2]
        testcard2 = put_card_in_play(self, player1, "hBP01-092", player1.backstage)
        testcard3 = put_card_in_play(self, player1, "hBP01-092", player1.backstage)
        p1center = player1.center[0]
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        g1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "green", "g1")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
        })
        events = engine.grab_events()
        # Events - send cheer effect, 2 cheer 1 target
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 0,
            "amount_max": 1,
            "from_zone": "holomem",
            "to_zone": "holomem",
        })
        from_options = events[0]["from_options"]
        self.assertEqual(len(from_options), 2)
        to_options = events[0]["to_options"]
        self.assertEqual(len(to_options), 2)

        placements = {}
        placements[from_options[0]] = testcard3["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements,
        })
        events = engine.grab_events()
        # Events - move cheer, perform, damage, perform step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.center[0]["game_card_id"],
            "to_holomem_id": testcard3["game_card_id"],
            "attached_id": from_options[0],
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": p1center["game_card_id"],
            "art_id": "kronichiwa",
            "target_id": player2.center[0]["game_card_id"],
            "power": 10,
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 10,
            "target_player": self.player2,
            "special": False,
        })
        reset_performancestep(self)


    def test_hBP01_094_choose_cheer_matching_holomem_tagged(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3,"hBP01-094": 3   }, {
            "hY02-001": 10,
            "hY03-001": 10,
        })
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.collab = player1.center
        player1.center = []
        test_card = put_card_in_play(self, player1, "hBP01-092", player1.center)
        bloom_card = add_card_to_hand(self, player1, "hBP01-094")
        player1.backstage = player1.backstage[:1]
        testcard2 = put_card_in_play(self, player1, "hBP01-092", player1.backstage)
        p1center = player1.center[0]
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        p1center["attached_cheer"] = []
        player1.cheer_deck.append(b1)

        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card["game_card_id"],
            "target_id": test_card["game_card_id"]
        })
        events = engine.grab_events()
        # Events - bloom, choose cheer
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {})
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "cheer_deck",
            "to_zone": "holomem"
        })
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 1)
        self.assertEqual(cards_can_choose[0], b1["game_card_id"])
        # Only 1 cheer, so choose it.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [b1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - Ask where to place.
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {})
        cards_can_choose = events[0]["cards_can_choose"]
        # Only promise are options
        self.assertEqual(len(cards_can_choose), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [testcard2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move cheer, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "zone_card_id": testcard2["game_card_id"],
            "card_id": b1["game_card_id"],
        })
        reset_mainstep(self)


    def test_hBP01_095_return_to_debut(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3,"hBP01-094": 3, "hBP01-095": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        p2deck = generate_deck_with([], {"hBP01-116": 1 }, {})
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-095", player1.backstage)
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b3")

        # Set up player 2's stack card.
        bloom2 = player2.hand[-1] # This is 005
        bloom1 = add_card_to_hand(self, player2, "hSD01-013")
        bloom3 = add_card_to_hand(self, player2, "hSD01-011")
        attach1 = add_card_to_hand(self, player2, "hBP01-116")
        p2debut = player2.backstage[0]
        player2.backstage = player2.backstage[1:]
        player2.backstage.append(bloom3)
        bloom3["stacked_cards"] = [bloom1, bloom2, p2debut]
        bloom3["attached_support"] = [attach1]
        player2.hand = []
        g1 = spawn_cheer_on_card(self, player2, bloom3["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player2, bloom3["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player2, bloom3["game_card_id"], "green", "g3")
        bloom3["damage"] = 100
        bloom3["resting"] = True

        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, return to debut pick
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {})
        validate_event(self, events[2], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {})
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertListEqual(cards_can_choose, ids_from_cards(player2.backstage))
        # Choose our target card.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [bloom3["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move a bunch of cards to hand, bloom, move debut to hand, main step
        self.assertEqual(len(events), 16)
        validate_event(self, events[0], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player2,
            "card_id": bloom3["game_card_id"],
            "healed_amount": 100,
            "new_damage": 0,
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "card_id": attach1["game_card_id"], })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "card_id": bloom1["game_card_id"], })
        validate_event(self, events[6], EventType.EventType_MoveCard, self.player1, {
            "card_id": bloom2["game_card_id"], })
        validate_event(self, events[8], EventType.EventType_MoveCard, self.player1, {
            "card_id": p2debut["game_card_id"], })
        validate_event(self, events[10], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player2,
            "bloom_card_id": p2debut["game_card_id"],
            "target_card_id": bloom3["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[12], EventType.EventType_MoveCard, self.player1, {
            "card_id": bloom3["game_card_id"], })
        reset_mainstep(self)
        self.assertEqual(len(player2.hand), 4)
        self.assertEqual(p2debut["damage"], 0)
        self.assertEqual(p2debut["resting"], True)


    def test_hBP01_095_return_to_debut_forced_to_hit_damaged_debut(self):
        p1deck = generate_deck_with([], {"hBP01-092": 3,"hBP01-094": 3, "hBP01-095": 3   }, {
            "hY02-001": 10,
            "hY04-001": 10,
        })
        p2deck = generate_deck_with([], {"hBP01-116": 1 }, {})
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = player1.backstage[:1]
        test_card = put_card_in_play(self, player1, "hBP01-095", player1.backstage)
        b1 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b1")
        b2 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b2")
        b3 = spawn_cheer_on_card(self, player1, player1.center[0]["game_card_id"], "blue", "b3")

        # This time, the target will be a debut with 1 attachment.
        p2debut = player2.backstage[0]
        player2.backstage = [p2debut]
        attach1 = add_card_to_hand(self, player2, "hBP01-116")
        p2debut["attached_support"] = [attach1]
        player2.hand = []
        g1 = spawn_cheer_on_card(self, player2, p2debut["game_card_id"], "green", "g1")
        g2 = spawn_cheer_on_card(self, player2, p2debut["game_card_id"], "green", "g2")
        g3 = spawn_cheer_on_card(self, player2, p2debut["game_card_id"], "green", "g3")
        p2debut["damage"] = 30
        p2debut["resting"] = True

        actions = reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, return to debut is forced, heal, move attachment to hand, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {})
        validate_event(self, events[2], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player2,
            "card_id": p2debut["game_card_id"],
            "healed_amount": 30,
            "new_damage": 0,
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "card_id": attach1["game_card_id"], })
        reset_mainstep(self)
        self.assertEqual(len(player2.hand), 1)
        self.assertEqual(p2debut["damage"], 0)
        self.assertEqual(p2debut["resting"], True)



    def test_hBP01_096_search_buzz(self):
        p1deck = generate_deck_with([], {"hBP01-096": 3 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        set_next_die_rolls(self, [2])
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-096", player1.backstage)

        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, roll die, choose buzz
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 2,
            "rigged": False
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "deck",
            "to_zone": "hand"
        })
        cards_can_choose = events[4]["cards_can_choose"]
        for card_id in cards_can_choose:
            card, _, _ = player1.find_card(card_id)
            self.assertTrue("buzz" in card and card["buzz"])
        # Choose one.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [cards_can_choose[0]]
        })
        events = engine.grab_events()
        # Events - move card, shuffle, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": cards_can_choose[0],
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, self.player1, {})
        actions = reset_mainstep(self)

    def test_hBP01_101_watson_item(self):
        p1deck = generate_deck_with([], {"hBP01-101": 3,"hBP01-102": 3  }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.backstage = []
        test_card = put_card_in_play(self, player1, "hBP01-101", player1.backstage)
        item = add_card_to_archive(self, player1, "hBP01-102")

        engine.handle_game_message(self.player1, GameAction.MainStepCollab, {
            "card_id": test_card["game_card_id"],
        })
        events = engine.grab_events()
        # Events - collab, choose item
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "from_zone": "archive",
            "to_zone": "hand"
        })
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 1)
        self.assertEqual(cards_can_choose[0], item["game_card_id"])

        # Choose none.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": []
        })
        events = engine.grab_events()
        # Events - main step
        self.assertEqual(len(events), 2)
        actions = reset_mainstep(self)

if __name__ == '__main__':
    unittest.main()
