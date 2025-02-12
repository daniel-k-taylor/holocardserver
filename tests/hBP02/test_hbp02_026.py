import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_026(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-026": 2, # 1st Mio
            "hBP02-024": 3 # debut Mio
        }, 
        {
            "hY04-001": 10, # blue cheer
            "hY03-001": 10, # red cheer
        })
        p2_deck = generate_deck_with("", {
            "hBP02-026": 2, # 1st Mio
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_026_kondoshimomimamottetene(self):
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have Mio in the center and backstage
        p1.center = []
        p1.backstage = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-026", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "kondoshimomimamottetene",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "kondoshimomimamottetene", "power": 20 }),
            (EventType.EventType_DamageDealt, { "damage": 20 }),
            *end_turn_events()
        ])

    def test_hbp02_026_bloomm_choose_cheer_matching_holomem_tagged(self):
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have debut Mio in the center and backstage, one 1st Mio on hand
        p1.center = []
        p1.backstage = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-024", p1.center))
        _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-026"))

        p1.backstage = p1.backstage[:1]
        _, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-024", p1.backstage))

        # Setup one green cheer in cheer_deck
        p1center = p1.center[0]
        p1center["attached_cheer"] = []
        g1 = spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "green", "g1")        
        p1.cheer_deck.append(g1)

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        reset_mainstep(self)
        engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
            "card_id": bloom_card_id,
            "target_id": center_card_id
        })
        events = engine.grab_events()
        # Events - bloom, choose cheer
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_Bloom, {}),
            (EventType.EventType_Decision_ChooseCards, { 
                "from_zone": "cheer_deck",
                "to_zone": "holomem" })
        ])
        cards_can_choose = events[2]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 1)
        self.assertEqual(cards_can_choose[0], g1["game_card_id"])
        # Only 1 cheer, so choose it.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [g1["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - Ask where to place.
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_Decision_ChooseHolomemForEffect, {})
        ])
        cards_can_choose = events[0]["cards_can_choose"]
        # Only Gamers are options
        self.assertEqual(len(cards_can_choose), 2)
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_card_id]
        })
        events = engine.grab_events()
        # Events - move cheer, main step
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_MoveCard, {
                "moving_player_id": self.player1,
                "from_zone": "cheer_deck",
                "to_zone": "holomem",
                "zone_card_id": backstage_card_id,
                "card_id": g1["game_card_id"],
            }),
            (EventType.EventType_Decision_MainStep, {})
        ])
        reset_mainstep(self)

    def test_hbp02_026_baton_pass(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)

        # Setup to have Mio in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-026", p1.center))


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

    def test_hbp02_026_downed_health(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        
        # Setup to have player2 have Mio damaged in the center
        p2.center = []
        p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-026", p2.center))
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

    def test_hbp02_026_overall_check(self):
        p1: PlayerState = self.engine.get_player(self.player1)
        card = next((card for card in p1.deck if card["card_id"] == "hBP02-026"), None)
        self.assertIsNotNone(card)

        # check hp and tags
        self.assertEqual(card["hp"], 100)
        self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars", "#Cooking"])    