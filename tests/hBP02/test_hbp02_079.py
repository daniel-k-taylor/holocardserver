import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_079(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-020": 1,
            "hBP02-079": 3,
        })
        p2_deck = generate_deck_with("", {
            "hBP02-020": 2,
            "hBP02-079": 3,
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_079_activate_magic_prevent_life_loss(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup add bakuhatsunomahou to hand
        p1.center = []
        _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-079"))
        _, _ = unpack_game_id(put_card_in_play(self, p1, "hBP02-020", p1.center))

        # give p2 center low hp
        p2.center = []
        p2.collab = []
        opponent_center_card, opponent_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-020", p2.center))
        _, _ = unpack_game_id(put_card_in_play(self, p2, "hBP02-020", p2.collab))
        opponent_center_card["damage"] = opponent_center_card["hp"] - 10

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [opponent_center_card_id] })
        

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": support_card_id }),
            (EventType.EventType_Decision_ChooseHolomemForEffect, {"effect_player_id": self.player1}),
            (EventType.EventType_DamageDealt, { "damage": 20 }),
            (EventType.EventType_DownedHolomem_Before, {}),
            (EventType.EventType_DownedHolomem, {
                "game_over": False,
                "target_player": self.player2,
                "life_lost": 0,
                "life_loss_prevented": True,
            }),
            (EventType.EventType_MoveCard, {}),
            (EventType.EventType_Decision_MainStep, {}),
        ])

    def test_hbp02_079_activated_magic_tag_cannot_activate_magic_again(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup add bakuhatsunomahou to hand
        p1.center = []
        _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-079"))
        add_card_to_hand(self, p1, "hBP02-079")
        _, _ = unpack_game_id(put_card_in_play(self, p1, "hBP02-020", p1.center))

        # give p2 center high hp
        p2.center[0]["hp"] = 100

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
        

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": support_card_id }),
            (EventType.EventType_DamageDealt, { "damage": 20 }),
            (EventType.EventType_MoveCard, {}),
            (EventType.EventType_Decision_MainStep, {}),
        ])

        # Check that there is no action to play support because we already played a magic.
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport not in [action["action_type"] for action in actions])

        # End turn twice and we can play again.
        end_turn(self)
        do_cheer_step_on_card(self, p2.center[0])
        end_turn(self)
        do_cheer_step_on_card(self, p1.center[0])
        actions = reset_mainstep(self)
        self.assertTrue(GameAction.MainStepPlaySupport in [action["action_type"] for action in actions])