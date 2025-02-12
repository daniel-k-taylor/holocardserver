import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_025(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-025": 2, # 1st Mio
        })
        p2_deck = generate_deck_with("", {
            "hBP02-025": 2, # 1st Mio
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_025_ohamionn(self):
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have Mio in the center and backstage
        p1.center = []
        p1.backstage = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-025", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "ohamionn",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "ohamionn", "power": 30 }),
            (EventType.EventType_DamageDealt, { "damage": 30 }),
            *end_turn_events()
        ])

    def test_hbp02_025_otsumionn(self):
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have Mio in the center and backstage
        p1.center = []
        p1.backstage = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-025", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "otsumionn",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "otsumionn", "power": 50 }),
            (EventType.EventType_DamageDealt, { "damage": 50 }),
            *end_turn_events()
        ])

    def test_hbp02_025_baton_pass(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)

        # Setup to have Mio in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-025", p1.center))


        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        # no cheers to use baton pass
        self.assertEqual(len(center_card["attached_cheer"]), 0)

        # Events
        actions = reset_mainstep(self)
        self.assertIsNone(
        next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))

        # with sufficient cheers
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        actions = reset_mainstep(self)
        self.assertIsNotNone(
        next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))

    def test_hbp02_025_downed_health(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        
        # Setup to have player2 have Mio damaged in the center
        p2.center = []
        p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-025", p2.center))
        p2_center_card["damage"] = p2_center_card["hp"] - 10

        _, center_card_id = unpack_game_id(p1.center[0])


        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "nunnun",
        "performer_id": center_card_id,
        "target_id": p2_center_card_id
        })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_PerformArt, {}),
        (EventType.EventType_DamageDealt, {}),
        (EventType.EventType_DownedHolomem_Before, {}),
        (EventType.EventType_DownedHolomem, { "life_lost": 1, "target_id": p2_center_card_id }),
        (EventType.EventType_Decision_SendCheer, {})
        ])

    def test_hbp02_025_overall_check(self):
        p1: PlayerState = self.engine.get_player(self.player1)
        card = next((card for card in p1.deck if card["card_id"] == "hBP02-025"), None)
        self.assertIsNotNone(card)

        # check hp and tags
        self.assertEqual(card["hp"], 160)
        self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars", "#Cooking"])    