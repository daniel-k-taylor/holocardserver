import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_005(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-014": 2, # Poyoyo
      "hSD02-002": 1, # debut Ayame
      "hSD02-005": 1, # 1st bloom Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_014_bonus_hp(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Poyoyo in hand
    center_card, center_card_id = unpack_game_id(p1.center[0]) 
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-014"))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

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

    self.assertEqual(center_card["hp"], 60)
    self.assertEqual(p1.get_card_hp(center_card), 60 + 20)


  def test_hsd02_005_sp_effect_on_ayame(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Ayame in the center and 1st Ayame in hand.
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-005"))

    # Attach Poyoyo
    put_card_in_play(self, p1, "hSD02-014", center_card["attached_support"])
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_Draw, {}), # Poyoyo effect
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd02_005_sp_effect_on_other_holomem(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have a 1st Sora in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD01-013"))

    # Attach Poyoyo to center
    put_card_in_play(self, p1, "hSD02-014", center_card["attached_support"])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_Decision_MainStep, {}) # No draw effect from Poyoyo
    ])


  def test_hsd02_014_only_one_mascot_name(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to attach 1 Poyoyo and 1 in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, attached_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-014", center_card["attached_support"]))
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-014"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(len(center_card["attached_support"]), 1)
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [attached_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": attached_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # previous Poyoyo sent to archive, new one attached
    self.assertEqual(len(p1.archive), 1)
    self.assertCountEqual(ids_from_cards(p1.archive), [attached_card_id])
    self.assertEqual(len(center_card["attached_support"]), 1)
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])