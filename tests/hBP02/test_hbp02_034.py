import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_034(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str


    def setUp(self):
        p1_deck = generate_deck_with("", {
        "hBP02-034": 1, #1st buzz ayame(AK)
        "hSD02-014": 1, #mascot
        "hSD02-013": 1  #tool
        })
        p2_deck = generate_deck_with("", {
        "hBP02-034": 1, #1st buzz ayame(AK)
        "hSD02-014": 1, #mascot
        "hSD02-013": 1  #tool
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_034_imgrass(self):
        engine = self.engine

        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup to have Ayame in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "imgrass",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })

        # Event
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "imgrass", "power": 50 }),
            (EventType.EventType_DamageDealt, { "damage": 50 }),
            *end_turn_events()
        ])

    def test_hbp02_034_organicshot_with_effect_no_mascot_no_tool(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup to have Ayame in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
        
        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "organicshot",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
        })

        # Event
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "organicshot", "power": 80 }),
            (EventType.EventType_DamageDealt, { "damage": 80 }),            
            *end_turn_events()
        ])

    def test_hbp02_034_organicshot_with_effect_one_mascot_no_tool(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup to have Ayame in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
        put_card_in_play(self, p1, "hSD02-014", center_card["attached_support"]) # mascot
        
        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "organicshot",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
        })

        # Event
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "organicshot", "power": 80 }),
            (EventType.EventType_BoostStat, { "amount": 30 }),
            (EventType.EventType_DamageDealt, { "damage": 110 }),
            *end_turn_events()
        ])

    def test_hbp02_034_organicshot_with_effect_no_mascot_one_tool(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup to have Ayame in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
        put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]) # tool
        
        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "organicshot",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
        })

        # Event
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "organicshot", "power": 80 }),
            (EventType.EventType_BoostStat, { "amount": 10 }),
            (EventType.EventType_BoostStat, { "amount": 10 }),
            (EventType.EventType_BoostStat, { "amount": 30 }),
            (EventType.EventType_DamageDealt, { "damage": 130 }),
            *end_turn_events()
        ])

    def test_hbp02_034_organicshot_with_effect_one_mascot_one_tool(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup to have Ayame in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
        put_card_in_play(self, p1, "hSD02-014", center_card["attached_support"]) # mascot
        put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]) # tool
        
        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "organicshot",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
        })

        # Event
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "organicshot", "power": 80 }),
            (EventType.EventType_BoostStat, { "amount": 10 }),
            (EventType.EventType_BoostStat, { "amount": 10 }),
            (EventType.EventType_BoostStat, { "amount": 30 }),
            (EventType.EventType_DamageDealt, { "damage": 130 }),
            *end_turn_events()
        ])

    def test_hbp02_034_baton_pass(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)

        # Setup to have Ayame in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-034", p1.center))


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

    def test_hbp02_034_buzz_downed_health(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        
        # Setup to have player2 have Ayame damaged in the center
        p2.center = []
        p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-034", p2.center))
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

    def test_hbp02_034_overall_check(self):
        p1: PlayerState = self.engine.get_player(self.player1)
        card = next((card for card in p1.deck if card["card_id"] == "hBP02-034"), None)
        self.assertIsNotNone(card)

        # check hp and tags
        self.assertEqual(card["hp"], 250)
        self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])    