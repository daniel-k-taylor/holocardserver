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


if __name__ == '__main__':
    unittest.main()
