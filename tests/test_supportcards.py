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

class TestSupportCards(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_support_hSD01_016(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-016"""
        # Add 2 of these to hand so we can also test limited.
        add_card_to_hand(self, player1, "hSD01-016")
        add_card_to_hand(self, player1, "hSD01-016")
        playfirst = player1.hand[-1]["game_card_id"]
        playsecond = player1.hand[-2]["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 5)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": playfirst,
        })
        events = self.engine.grab_events()
        # Events - play card, draw 3, discard playing card, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": playfirst,
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": playfirst,
        })
        validate_event(self, events[6], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.hand), 7)
        self.assertTrue(player1.used_limited_this_turn)
        self.assertEqual(player1.archive[0]["game_card_id"], playfirst)

        # Check that there is no action to play support because we already played a limited.
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport not in [action["action_type"] for action in actions])

        # End turn twice and we can play again.
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        end_turn(self)
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

    def test_support_hSD01_017(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-017"""
        player1.hand = []
        # Check that you can't play it if it is the only card in hand.
        add_card_to_hand(self, player1, "hSD01-017")
        playfirst = player1.hand[-1]["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 1)
        self.assertTrue(GameAction.MainStepPlaySupport not in [action["action_type"] for action in actions])

        # But you can play it with 2 cards total.
        extracard = add_card_to_hand(self, player1, "hSD01-006")
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 2)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": playfirst,
        })
        events = self.engine.grab_events()
        # Events - play card, move last card to deck, shuffle, draw 5, discard playing card, main step
        self.assertEqual(len(events), 12)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": playfirst,
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "deck",
            "card_id": extracard["game_card_id"],
        })
        validate_event(self, events[4], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1
        })
        validate_event(self, events[6], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": playfirst,
        })
        validate_event(self, events[10], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.hand), 5)
        self.assertTrue(player1.used_limited_this_turn)
        self.assertEqual(player1.archive[0]["game_card_id"], playfirst)


    def test_support_hSD01_018(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-018"""
        play1 = add_card_to_hand(self, player1, "hSD01-018")["game_card_id"]
        play2 = add_card_to_hand(self, player1, "hSD01-018")["game_card_id"]
        play3 = add_card_to_hand(self, player1, "hSD01-018")["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 6)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play1,
        })
        events = self.engine.grab_events()
        # Events - play card, order remaining
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play1,
            "limited": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 0, # Since we know we're getting 0 cards
            "amount_max": 0,
            "reveal_chosen": True,
            "remaining_cards_action": "order_on_bottom",
        })
        available_to_choose = events[2]["cards_can_choose"]
        all_cards_seen = events[2]["all_card_seen"]
        self.assertEqual(len(available_to_choose), 0) # Nothing! Still need to decision?
        self.assertEqual(len(all_cards_seen), 5)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
              "card_ids": []
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player1,
            "card_ids": all_cards_seen,
            "from_zone": "deck",
            "to_zone": "deck",
            "bottom": True,
        })
        cards_in_order = []
        cards_in_order.append(all_cards_seen.pop(2))
        cards_in_order.append(all_cards_seen.pop(3))
        cards_in_order.append(all_cards_seen.pop(0))
        cards_in_order.append(all_cards_seen.pop(1))
        cards_in_order.append(all_cards_seen.pop(0))
        engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, {
              "card_ids": cards_in_order
        })
        events = self.engine.grab_events()
        # Events - 5 move cards, discard support, main step
        self.assertEqual(len(events), 14)
        self.assertEqual(player1.deck[-5]["game_card_id"], cards_in_order[0])
        self.assertEqual(player1.deck[-4]["game_card_id"], cards_in_order[1])
        self.assertEqual(player1.deck[-3]["game_card_id"], cards_in_order[2])
        self.assertEqual(player1.deck[-2]["game_card_id"], cards_in_order[3])
        self.assertEqual(player1.deck[-1]["game_card_id"], cards_in_order[4])
        validate_event(self, events[10], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play1,
        })
        validate_event(self, events[12], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})

        # Now, put 2 we can actually choose on top.
        choice1 = add_card_to_hand(self, player1, "hSD01-019")["game_card_id"]
        choice2 = add_card_to_hand(self, player1, "hSD01-019")["game_card_id"]
        player1.move_card(choice1, "deck")
        player1.move_card(choice2, "deck")
        reset_mainstep(self)

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play2,
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4)
        # Events - play card, order remaining
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play2,
            "limited": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "order_on_bottom",
        })
        available_to_choose = events[2]["cards_can_choose"]
        all_cards_seen = events[2]["all_card_seen"]
        self.assertEqual(len(available_to_choose), 2)
        self.assertEqual(len(all_cards_seen), 5)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
              "card_ids": [choice2]
        })
        events = self.engine.grab_events()
        # This time we draw the 1 card we chose.
        self.assertEqual(len(events), 4)
        # Even player 2 can see.
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": choice2,
        })
        validate_event(self, events[2], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "deck",
            "bottom": True,
        })
        cards_in_order = []
        all_cards_seen.remove(choice2)
        cards_in_order.append(all_cards_seen.pop(2))
        cards_in_order.append(all_cards_seen.pop(0))
        cards_in_order.append(all_cards_seen.pop(1))
        cards_in_order.append(all_cards_seen.pop(0))
        engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, {
              "card_ids": cards_in_order
        })
        events = self.engine.grab_events()
        # Events - 4 move cards, discard support, main step
        self.assertEqual(len(events), 12)
        self.assertEqual(player1.deck[-4]["game_card_id"], cards_in_order[0])
        self.assertEqual(player1.deck[-3]["game_card_id"], cards_in_order[1])
        self.assertEqual(player1.deck[-2]["game_card_id"], cards_in_order[2])
        self.assertEqual(player1.deck[-1]["game_card_id"], cards_in_order[3])
        validate_event(self, events[8], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play2,
        })
        validate_event(self, events[10], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})


    def test_support_hSD01_019(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-019"""
        play1 = add_card_to_hand(self, player1, "hSD01-019")["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 4)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

        # Play the card.
        cheer_id = player1.center[0]["attached_cheer"][0]["game_card_id"]
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play1,
            "cheer_to_archive_from_play": [cheer_id],
        })
        events = self.engine.grab_events()
        # Events - play card, arhive a cheer, choose from all of deck bloom (no buzz)
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play1,
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": player1.center[0]["game_card_id"],
            "to_holomem_id": "archive",
            "attached_id": cheer_id,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        available_to_choose = events[4]["cards_can_choose"]
        all_cards_seen = events[4]["all_card_seen"]
        # Count all bloom cards (not buzz) in the deck.
        count = 0
        for card in player1.deck:
            if card["card_type"] == "holomem_bloom" and not ("buzz" in card and card["buzz"]) and card["bloom_level"] in [1,2]:
                count += 1
        self.assertEqual(count, len(available_to_choose))
        self.assertEqual(len(all_cards_seen), len(player1.deck))
        chosen_card = available_to_choose[3]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
              "card_ids": [chosen_card]
        })
        # Draw the card, shuffle deck, discard play card, main step
        events = self.engine.grab_events()
        self.assertEqual(len(events), 8)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": chosen_card,
        })
        validate_event(self, events[2], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play1,
        })
        validate_event(self, events[6], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})

        # Now, put 2 we can actually choose on top.
        choice1 = add_card_to_hand(self, player1, "hSD01-019")["game_card_id"]
        choice2 = add_card_to_hand(self, player1, "hSD01-019")["game_card_id"]
        player1.move_card(choice1, "deck")
        player1.move_card(choice2, "deck")
        reset_mainstep(self)


    def test_support_hSD01_020(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-020"""
        play1 = add_card_to_hand(self, player1, "hSD01-020")["game_card_id"]
        play2 = add_card_to_hand(self, player1, "hSD01-020")["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 5)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])
        set_next_die_rolls(self, [6, 6])

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play1,
        })
        events = self.engine.grab_events()
        # Events - play card, roll die, discard, main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play1,
            "limited": False,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play1,
        })
        validate_event(self, events[6], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})

        # That failed because there was no cheer in the archive.
        # Dump some cheer.
        for _ in range(6):
            player1.move_card(player1.cheer_deck[0]["game_card_id"], "archive")
        events = self.engine.grab_events()

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play2,
        })
        events = self.engine.grab_events()
        # Events - play card, roll die, choose cheer from archive
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play2,
            "limited": False,
        })
        validate_event(self, events[2], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": False,
        })
        validate_event(self, events[4], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "archive",
            "to_zone": "holomem",
        })

        # Choose one and a mem.
        chosen_cheer = player1.archive[2]["game_card_id"]
        placements = {
            chosen_cheer: player1.backstage[0]["game_card_id"]
        }
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # Events - move cheer, discard, main step
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "archive",
            "to_holomem_id": player1.backstage[0]["game_card_id"],
            "attached_id": chosen_cheer,
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play2,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})


    def test_support_hSD01_021(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test hSD01-021"""
        play1 = add_card_to_hand(self, player1, "hSD01-021")["game_card_id"]
        play2 = add_card_to_hand(self, player1, "hSD01-021")["game_card_id"]
        junk1 = add_card_to_hand(self, player1, "hSD01-014")["game_card_id"]
        junk2 = add_card_to_hand(self, player1, "hSD01-014")["game_card_id"]
        junk3 = add_card_to_hand(self, player1, "hSD01-015")["game_card_id"]
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 8)
        self.assertTrue(GameAction.MainStepPlaySupport not in [action["action_type"] for action in actions])

        # Get rid of a junk card then we can play it.
        player1.move_card(junk1, "archive")
        actions = reset_mainstep(self)
        self.assertEqual(len(player1.hand), 7)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])

        # Play the card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play1,
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4)
        # Events - play card, choose sora/az
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play1,
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 0,
            "amount_max": 3,
            "reveal_chosen": True,
            "remaining_cards_action": "order_on_bottom",
        })
        available_to_choose = events[2]["cards_can_choose"]
        all_cards_seen = events[2]["all_card_seen"]
        self.assertEqual(len(available_to_choose), 3) # 3 sora/az and 1 irys
        self.assertEqual(len(all_cards_seen), 4)

        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
              "card_ids": available_to_choose
        })
        events = self.engine.grab_events()
        # Draw those 3
        self.assertEqual(len(events), 8)
        # Even player 2 can see.
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[0],
        })
        validate_event(self, events[3], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[1],
        })
        validate_event(self, events[5], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[2],
        })
        validate_event(self, events[6], EventType.EventType_Decision_OrderCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "deck",
            "bottom": True,
        })
        cards_in_order = events[6]["card_ids"]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, {
              "card_ids": cards_in_order
        })
        events = self.engine.grab_events()
        # Events - 1 move cards, discard support, main step
        self.assertEqual(len(events), 6)
        self.assertEqual(player1.deck[-1]["game_card_id"], cards_in_order[0])
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play1,
        })
        validate_event(self, events[4], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.hand), 9)

        # Now test for if we draw all 4 and there are none to return.
        # So put 4 sora/az back on the deck. Have plenty of 004/005/006 in hand.
        cards_named_sora = []
        for card in player1.hand:
            if "holomem_names" in card and "tokino_sora" in card["holomem_names"]:
                cards_named_sora.append(card["game_card_id"])
                if len(cards_named_sora) == 4:
                    break
        self.assertEqual(len(cards_named_sora), 4)
        for card_id in cards_named_sora:
            player1.move_card(card_id, "deck")

        self.assertEqual(len(player1.hand), 5)
        player1.used_limited_this_turn = False
        reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])


        # Play the 2nd card.
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
            "card_id": play2,
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4)
        # Events - play card, choose sora/az
        validate_event(self, events[0], EventType.EventType_PlaySupportCard, self.player1, {
            "player_id": self.player1,
            "card_id": play2,
            "limited": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "amount_min": 0,
            "amount_max": 4,
            "reveal_chosen": True,
            "remaining_cards_action": "order_on_bottom",
        })
        available_to_choose = events[2]["cards_can_choose"]
        all_cards_seen = events[2]["all_card_seen"]
        self.assertEqual(len(available_to_choose), 4) # all 4 this time.
        self.assertEqual(len(all_cards_seen), 4)

        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
              "card_ids": available_to_choose
        })
        events = self.engine.grab_events()
        # Draw those 4, no cards to order so discard + main step
        self.assertEqual(len(events), 12)
        # Even player 2 can see.
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[0],
        })
        validate_event(self, events[3], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[1],
        })
        validate_event(self, events[5], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[2],
        })
        validate_event(self, events[7], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "hand",
            "card_id": available_to_choose[3],
        })
        validate_event(self, events[8], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "floating",
            "to_zone": "archive",
            "card_id": play2,
        })
        validate_event(self, events[10], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.hand), 8)

if __name__ == '__main__':
    unittest.main()
