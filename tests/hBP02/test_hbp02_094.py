import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hBP02_094(unittest.TestCase):
    engine: GameEngine
    player1: str
    player2: str

    def setUp(self):
        p1_deck = generate_deck_with("", {
            "hBP02-020": 1, # reine
            "hBP01-053": 1, # iofifteen
            "hBP02-094": 3, # Tatang
        })
        initialize_game_to_third_turn(self, p1_deck)

    def test_hbp02_094_attach_effect_reine_hp(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Tatang in hand
        _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-094"))
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-020", p1.center))

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        # Attach to center
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [ center_card_id ] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
            (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
            (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id }),
            (EventType.EventType_Decision_MainStep, {})
        ])

        # check hp
        self.assertEqual(center_card["hp"], 160)
        self.assertEqual(p1.get_card_hp(center_card), 160 + 30)

    def test_hbp02_094_attach_effect_other_hp(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Tatang in hand
        _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-094"))
        center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP01-053", p1.center))

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        # Attach to center
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [ center_card_id ] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
            (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
            (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id }),
            (EventType.EventType_Decision_MainStep, {})
        ])

        # check hp
        self.assertEqual(center_card["hp"], 170)
        self.assertEqual(p1.get_card_hp(center_card), 170)

    def test_hbp02_094_attach_effect_reine_attack(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Tatang in hand
        _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-094"))
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-020", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1") # green color
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color

        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        # Attach to center
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [ center_card_id ] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
            (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
            (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id }),
            (EventType.EventType_Decision_MainStep, {})
        ])

        # Attack
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "royalhalusleepover",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "royalhalusleepover", "power": 50 }),
            (EventType.EventType_BoostStat, { "stat": "power", "amount": 10, }),
            (EventType.EventType_DamageDealt, { "damage": 60 }),
            (EventType.EventType_Decision_PerformanceStep, {}),
        ])


    def test_hbp02_094_attach_effect_other_attack(self):
        engine = self.engine
    
        p1: PlayerState = engine.get_player(self.player1)
        p2: PlayerState = engine.get_player(self.player2)

        # Setup Tatang in hand
        _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-094"))
        _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP01-053", p1.center))
        spawn_cheer_on_card(self, p1, center_card_id, "green", "g1") # green color
        spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color

        # give p2 center high hp
        p2.center[0]["hp"] = 200

        """Test"""
        self.assertEqual(engine.active_player_id, self.player1)

        # Attach to center
        engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [ center_card_id ] })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
            (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
            (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id }),
            (EventType.EventType_Decision_MainStep, {})
        ])

        # Attack
        begin_performance(self)
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "art_id": "yourbelovedalien",
            "performer_id": center_card_id,
            "target_id": p2.center[0]["game_card_id"]
        })

        # Events
        events = engine.grab_events()
        validate_consecutive_events(self, self.player1, events, [
            (EventType.EventType_PerformArt, { "art_id": "yourbelovedalien", "power": 50 }),
            (EventType.EventType_BoostStat, { "stat": "power", "amount": 10, }),
            (EventType.EventType_DamageDealt, { "damage": 60 }),
            (EventType.EventType_Decision_PerformanceStep, {}),
        ])