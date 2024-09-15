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
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, use_oshi_action

class Test_hbp01_003(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hbp01_003_oshi_survivalpower(self):
        p1deck = generate_deck_with("hBP01-003", {"hBP01-114": 4 }, [])
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

        # Grab a green card to put out.
        green_card = add_card_to_hand(self, player1, "hSD01-008")

        events = use_oshi_action(self, "survivalpower")
        # No green target holomem in play, so expect this to just do nothing.
        # Spend 2 holopower, oshi activation, choose cards step
        self.assertEqual(len(events), 8)
        validate_event(self, events[6], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        cards_can_choose = events[6]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 4) # 4 axes
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": cards_can_choose[:1]
        })
        events = engine.grab_events()
        # Events - shuffle, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_ShuffleDeck, self.player1, {
            "shuffling_player_id": self.player1
        })
        axes_in_deck = [card for card in player1.deck if card["card_id"] == "hBP01-114"]
        self.assertEqual(len(axes_in_deck), 4)


        # Reset that we used the skill and try again with a green card in play.
        player1.effects_used_this_turn = []
        player1.center = [green_card]
        actions = reset_mainstep(self)

        events = use_oshi_action(self, "survivalpower")
        # Spend 2 holopower, oshi activation, choose cards step
        self.assertEqual(len(events), 8)
        validate_event(self, events[6], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "deck",
            "to_zone": "holomem",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "shuffle",
        })
        cards_can_choose = events[6]["cards_can_choose"]
        chosen_axe = cards_can_choose[0]
        self.assertEqual(len(cards_can_choose), 4) # 4 axes
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": cards_can_choose[:1]
        })
        events = engine.grab_events()
        # Events - choose holomem
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[0]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 1)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": cards_can_choose[:1]
        })
        events = engine.grab_events()
        # Events - attach to mem, shuffle, main step
        self.assertEqual(len(events), 6)
        self.assertEqual(player1.center[0]["attached_support"][0]["game_card_id"], chosen_axe)
        actions = reset_mainstep(self)


    def test_hbp01_003_oshi_songoftheearth(self):
        p1deck = generate_deck_with("hBP01-003", {"hBP01-114": 4 }, [])
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

        player1.center[0]["damage"] = 50
        events = use_oshi_action(self, "songoftheearth")
        # No green target holomem in play, so expect this to just do nothing.
        # Spend 2 holopower, oshi activation, main step
        self.assertEqual(len(events), 8)
        self.assertEqual(player1.center[0]["damage"], 50)
        actions = reset_mainstep(self)

        # Reset and try again.
        player1.effects_used_this_game = []
        player1.center = []
        green_card = put_card_in_play(self, player1, "hSD01-008", player1.center)
        green_card["damage"] = 50

        events = use_oshi_action(self, "songoftheearth")
        # Spend 2 holopower, oshi activation, restore hp, main step
        self.assertEqual(len(events), 10)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "songoftheearth",
        })
        validate_event(self, events[6], EventType.EventType_RestoreHP, self.player1, {
            "target_player_id": self.player1,
            "card_id": green_card["game_card_id"],
            "healed_amount": 50,
            "new_damage": 0,
        })
        actions = reset_mainstep(self)






if __name__ == '__main__':
    unittest.main()
