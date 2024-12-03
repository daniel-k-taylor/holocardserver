import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_038(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-038": 1, # 1st Chloe
      "hBP02-035": 1, # debut Chloe
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_038_thisiswhereienjoyit(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-038", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thisiswhereienjoyit",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thisiswhereienjoyit", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])

    
  def test_hbp02_038_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup debut Chloe in center and 1st Chloe in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    bloom_card, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-038"))

    cheer_ids = ids_from_cards(p1.cheer_deck[:3])
    chosen_cheer_id = cheer_ids[0]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_cheer_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": cheer_ids[1:] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cheer_ids }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p1.center + p1.backstage) }),

      (EventType.EventType_MoveCard, { "from_zone": "cheer_deck", "to_zone": "holomem", "zone_card_id": bloom_card_id, "card_id": chosen_cheer_id }),
      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "cheer_deck", "to_zone": "cheer_deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "cheer_deck", "to_zone": "cheer_deck" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(bloom_card["attached_cheer"]), [chosen_cheer_id])


  def test_hbp02_038_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-038", p1.center))
  
  
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


  def test_hbp02_038_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-038"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 110)
    self.assertCountEqual(card["tags"], ["#JP", "#SecretSocietyholoX", "#Sea"])