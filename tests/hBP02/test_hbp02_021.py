import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_021(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-021": 3,
        })
        p2_deck = generate_deck_with("", {
            "hBP02-021": 3,
        })
        initialize_game_to_third_turn(self, p1_deck, p2_deck)

    def test_hbp02_021_overall_check(self):
        p1: PlayerState = self.engine.get_player(self.player1)
        card = next((card for card in p1.deck if card["card_id"] == "hBP02-021"), None)
        self.assertIsNotNone(card)

        # check hp and tags
        self.assertEqual(card["hp"], 120)
        self.assertCountEqual(card["tags"], ["#ID", "#IDGen2", "#Bird", "#Art"])

    def test_hbp02_021_dakaramiteteneutatteodorimasu(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Reine in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
        valid_target_ids = ids_from_cards(p1.get_holomem_on_stage())

        # Add multiple cheers to archive (5 cheers, 5 non-cheers)
        cheer_cards = p1.cheer_deck[:5]
        _, cheer_card_id = unpack_game_id(cheer_cards[0])
        p1.archive = p1.deck[:5] + cheer_cards
        p1.cheer_deck = p1.cheer_deck[5:]
        p1.deck = p1.deck[:5]

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "dakaramiteteneutatteodorimasu",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": { cheer_card_id: center_card_id }
        })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "dakaramiteteneutatteodorimasu", "power": 20 }),
            (EventType.EventType_Decision_SendCheer, { "from_options": ids_from_cards(cheer_cards), "to_options": valid_target_ids }),
            (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": center_card_id, "attached_id": cheer_card_id }),
            (EventType.EventType_DamageDealt, { "damage": 20 }),
            *end_turn_events()
        ])

    def test_hbp02_021_dakaramiteteneutatteodorimasu_no_cheer_in_archive(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Reine in the center
        p1.center = []
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color

        p1.archive = []

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "dakaramiteteneutatteodorimasu",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "dakaramiteteneutatteodorimasu", "power": 20 }),
            (EventType.EventType_DamageDealt, { "damage": 20 }),
            *end_turn_events()
        ])

    def test_hbp02_021_baton_pass(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)

        # Setup to have card in the center
        p1.center = []
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.center))

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

    def test_hbp02_021_downed_health(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)
        
        # Setup to have player2 have card damaged in the center
        p2.center = []
        p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-021", p2.center))
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

    def test_hbp02_021_bloom_effect(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        
        # Setup to have 1st reine in the center and 1st reine in hand
        p1.center = []
        p1.backstage = []
        _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-021"))
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1") # any color
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color        
        backstage_card, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.backstage))
        spawn_cheer_on_card(self, p1, backstage_card_id, "green", "g2") # any color
        spawn_cheer_on_card(self, p1, backstage_card_id, "purple", "p1") # any color

        backstage_card["damage"] = 60       

        

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

        valid_target_ids = ids_from_cards(p1.get_holomem_on_stage())

        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [backstage_card_id] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
        (EventType.EventType_Decision_Choice, {}),
        (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),
        (EventType.EventType_RestoreHP, { "healed_amount": 50, "new_damage": 10  }),
        (EventType.EventType_Decision_MainStep, {})
        ])

    def test_hbp02_021_bloom_effect_no_cheer(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        
        # Setup to have 1st reine in the center and 1st reine in hand
        p1.center = []
        p1.backstage = []
        _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-021"))
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.center))
        backstage_card, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-021", p1.backstage))

        backstage_card["damage"] = 60       

        

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

        valid_target_ids = ids_from_cards(p1.get_holomem_on_stage())

        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [backstage_card_id] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
        (EventType.EventType_Decision_Choice, {}),
        (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),
        (EventType.EventType_Decision_MainStep, {})
        ])