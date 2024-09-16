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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, pick_choice, use_oshi_action

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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        events = reset_performancestep(self)



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
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        from_options = events[4]["cards_can_choose"]
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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": True,
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
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player1,
            "bloom_card_id": bloom_card["game_card_id"],
            "target_card_id": test_card["game_card_id"],
            "bloom_from_zone": "hand",
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 30,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
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
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 50,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
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
        to_options = events[4]["to_options"]
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
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": test_card["game_card_id"],
            "holopower_generated": 1,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "damage": 50,
            "died": True,
            "game_over": True,
            "target_player": self.player2,
            "special": False,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[4], EventType.EventType_GameOver, self.player1, {
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
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
            "power": 100,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 100,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
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
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "jetblackwings",
            "target_id": p2center["game_card_id"],
            "power": 100,
        })
        validate_event(self, events[2], EventType.EventType_DamageDealt, self.player1, {
            "target_id": p2center["game_card_id"],
            "damage": 100,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 2,
            "life_loss_prevented": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 2,
            "amount_max": 2,
            "from_zone": "life",
            "to_zone": "holomem",
        })


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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
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
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
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
        self.assertEqual(len(events), 20)
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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
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
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 2,
            "life_loss_prevented": False,
        })
        validate_event(self, events[18], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 2,
            "amount_max": 2,
            "from_zone": "life",
            "to_zone": "holomem",
        })
        from_options = events[18]["from_options"]
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
        self.assertEqual(len(events), 4)
        self.assertEqual(p1center["damage"], 60)
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
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
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": False,
            "life_lost": 0,
            "life_loss_prevented": False,
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
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 60
        })
        validate_event(self, events[4], EventType.EventType_DamageDealt, self.player1, {
            "damage": 110,
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
            "died": False,
            "game_over": False,
            "target_player": self.player1,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": False,
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
        self.assertEqual(len(events), 8)
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
        self.assertEqual(len(events), 10)
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
        self.assertEqual(len(events), 18)
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
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": False,
            "life_lost": 1,
            "life_loss_prevented": False,
        })
        validate_event(self, events[16], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
            "to_zone": "holomem",
        })

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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": False,
        })
        actions = reset_mainstep(self)

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
            "died": False,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": True,
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
        self.assertEqual(len(events), 18)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": sniped["game_card_id"],
            "damage": 10,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        validate_event(self, events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.center[0]["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        do_cheer_step_on_card(self, player2.center[0])
        actions = reset_mainstep(self)
        self.assertEqual(player2.archive[0]["game_card_id"], sniped["game_card_id"])


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
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": sniped["game_card_id"],
            "damage": 20,
            "died": True,
            "game_over": False,
            "target_player": self.player2,
            "special": True,
            "life_lost": 0,
            "life_loss_prevented": True,
        })
        actions = reset_mainstep(self)


if __name__ == '__main__':
    unittest.main()
