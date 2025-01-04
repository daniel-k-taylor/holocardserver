import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_095(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-095": 2, # mascot
      "hBP02-028": 1, # debut Marine
      "hBP02-030": 1, # 1st Marine
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_095_effect_additional_damage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup mascot attached to center
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-095", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

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
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hbp02_095_attached_to_marine_center_blooms(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup debut Marine attached with Mascot in center and 1st Marine in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-028", p1.center))
    put_card_in_play(self, p1, "hBP02-095", center_card["attached_support"])
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-030"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    
  def test_hbp02_095_attached_to_marine_not_center_blooms(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup debut Marine attached with Mascot in collab and 1st Marine in hand
    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-028", p1.collab))
    put_card_in_play(self, p1, "hBP02-095", collab_card["attached_support"])
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-030"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_095_not_attached_to_marine_center_blooms(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Sora center attached with Mascot and 1st SoraZ in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    put_card_in_play(self, p1, "hBP02-095", center_card["attached_support"])
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD01-013"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_095_only_one_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup debut Marine attached with Mascot in center and another Mascot in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-028", p1.center))
    _, attached_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-095", center_card["attached_support"]))
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-095"))

    valid_target_ids = ids_from_cards(p1.backstage)
    chosen_card, chosen_card_id = unpack_game_id(p1.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": chosen_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [attached_card_id])
    self.assertCountEqual(ids_from_cards(chosen_card["attached_support"]), [mascot_card_id])
    self.assertTrue(center_card_id not in valid_target_ids)