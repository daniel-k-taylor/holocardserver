import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_063(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-063": 1, # 1st Ina
      "hBP02-061": 2, # debut Ina
      "hBP01-100": 1, # spot Calli
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_063_areyouallreadytowah(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup 1st Ina to center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-063", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "areyouallreadytowah",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "areyouallreadytowah", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_063_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup debut Ina to center and 1st Ina to hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-061", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-063"))

    # Debut Ina and spot Calli in the backstage
    p1.backstage = p1.backstage[:-2]
    put_card_in_play(self, p1, "hBP02-061", p1.backstage)
    put_card_in_play(self, p1, "hBP01-100", p1.backstage)

    chosen_card, chosen_card_id = unpack_game_id(p1.backstage[-2])
    chosen_card["damage"] = 30
    myth_card_ids = [bloom_card_id] + ids_from_cards(p1.backstage[-2:])

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": myth_card_ids }),

      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 10  }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_063_bloom_effect_no_other_myth(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup debut Ina to center and 1st Ina to hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-061", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-063"))

    center_card["damage"] = 20

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),

      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 0  }), # select the only choice immediately
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_063_bloom_effect_no_damage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup debut Ina to center and 1st Ina to hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-061", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-063"))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_MainStep, {}) # no effect
    ])


  def test_hbp02_063_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-063", p1.center))
  
  
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


  def test_hbp02_063_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-063"), None)
    self.assertIsNotNone(card)