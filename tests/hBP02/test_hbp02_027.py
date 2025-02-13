import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_027(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-027": 2, # 1st buzz Mio
            "hBP02-084": 1, # support mikkorone24
        })
        p2_deck = generate_deck_with("", {
            "hBP02-027": 1, # 1st buzz Mio
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_027_tarottonomichibiki_holomem(self): 
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have Mio in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-027", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

        # Setup holomem in topdeck
        supportcard = add_card_to_hand(self, p1, "hBP02-027", False)
        p1.deck.insert(0, supportcard)
        p1.hand.remove(supportcard)

        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        self.assertIn(supportcard["card_type"], ["holomem_bloom","holomem_spot","holomem_debut"])
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "tarottonomichibiki",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - hit 60 and archive holomem +20
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "tarottonomichibiki", "power": 60 }),
            (EventType.EventType_Decision_Choice, {})
        ])

        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { 
            "choice_index": 0 
        })
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_RevealCards, { 
                "effect_player_id": self.player1,
                "source": "topdeck"
            }),
            (EventType.EventType_BoostStat, { "amount": 20 }),
            (EventType.EventType_MoveCard, {
                "moving_player_id": self.player1,
                "from_zone": "deck",
                "to_zone": "archive",
                "card_id": supportcard["game_card_id"]
            }),
            (EventType.EventType_DamageDealt, { "damage": 80 }),
            *end_turn_events()
        ])

    def test_hbp02_027_tarottonomichibiki_support(self): 
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        # Setup to have Mio in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-027", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

        # Setup support in topdeck
        supportcard = add_card_to_hand(self, p1, "hBP02-084", False)
        p1.deck.insert(0, supportcard)
        p1.hand.remove(supportcard)

        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)
        self.assertEqual(supportcard["card_type"], "support")
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "tarottonomichibiki",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        events = engine.grab_events()
        # Events - hit 60 and archive support +50
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "tarottonomichibiki", "power": 60 }),
            (EventType.EventType_Decision_Choice, {})
        ])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { 
            "choice_index": 0 
        })
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_RevealCards, { 
                "effect_player_id": self.player1,
                "source": "topdeck"
            }),
            (EventType.EventType_BoostStat, { "amount": 50 }),
            (EventType.EventType_MoveCard, {
                "moving_player_id": self.player1,
                "from_zone": "deck",
                "to_zone": "archive",
                "card_id": supportcard["game_card_id"]
            }),
            (EventType.EventType_DamageDealt, { "damage": 110 }),
            *end_turn_events()
        ])

    def test_hbp02_027_baton_pass(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)

        # Setup to have Mio in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-027", p1.center))


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
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        actions = reset_mainstep(self)
        self.assertIsNotNone(
        next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))

    def test_hbp02_027_buzz_downed_health(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        
        # Setup to have player2 have Mio damaged in the center
        p2.center = []
        p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-027", p2.center))
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
        (EventType.EventType_DownedHolomem, { "life_lost": 2, "target_id": p2_center_card_id }),
        (EventType.EventType_Decision_SendCheer, {})
        ])

    def test_hbp02_027_overall_check(self):
        p1: PlayerState = self.engine.get_player(self.player1)
        card = next((card for card in p1.deck if card["card_id"] == "hBP02-027"), None)
        self.assertIsNotNone(card)

        # check hp and tags
        self.assertEqual(card["hp"], 240)
        self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars", "#Cooking"])    