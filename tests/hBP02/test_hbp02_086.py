import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_086(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-086": 2, # tool support
      "hBP02-014": 1, # debut Noel
    })
    p2_deck = generate_deck_with("", {
      "hBP02-086": 1, # tool support
      "hBP02-014": 1, # debut Noel
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_086_boost_stat(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to add tool to hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, tool_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-086"))

    # Attach to center
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": tool_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [tool_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 20, "source_card_id": tool_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])
    
    
  def test_hbp02_086_attached_to_alcohol_no_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player2 have debut Noel attached with tool in the center
    p2.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-014", p2.center))
    _, tool_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-086", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [tool_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_086_attached_to_non_alcohol_plus_damage_taken(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player2 center attached with tool in the center
    center_card, center_card_id = unpack_game_id(p2.center[0])
    _, tool_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-086", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [tool_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hbp02_086_one_tool_only(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have 1 Tool attached to center and 1 in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, attached_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-086", center_card["attached_support"]))
    _, tool_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-086"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": tool_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": tool_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": attached_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": tool_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    