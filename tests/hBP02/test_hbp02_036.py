import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_036(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-036": 2, # debut Chloe
      "hBP01-061": 3, # 2nd Lui
      "hBP01-067": 1, # 2nd Kiara
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_036_areality(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-036", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "areality",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "areality", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hbp02_036_collab_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Chloe in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-036", p1.backstage))

    # Setup 2 2nd Lui in top 3 after collab
    p1.deck = p1.deck[-4:] + p1.deck[:-4]
    top_three_ids = ids_from_cards(p1.deck[1:4])
    chosen_card_id = top_three_ids[0]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": top_three_ids[1:] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": top_three_ids[:-1] }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": chosen_card_id }),
      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_036_collab_effect_2nd_bloom_but_not_holox(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Chloe in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-036", p1.backstage))

    # Setup 2 Kiara in top 3 after collab
    p1.deck = p1.deck[-2:] + p1.deck[:-2]
    top_three_ids = ids_from_cards(p1.deck[1:4])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": top_three_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    
  #collab effect not 2nd bloom, holox
  def test_hbp02_036_collab_effect_holox_but_not_2nd_bloom(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Chloe in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-036", p1.backstage))

    # Setup 2 Kiara in top 3 after collab
    p1.deck = p1.deck[-5:][:2][::-1] + p1.deck[:-5]
    top_three_ids = ids_from_cards(p1.deck[1:4])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": top_three_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    
  def test_hbp02_036_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-036", p1.center))
  
  
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


  def test_hbp02_036_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-036"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 60)
    self.assertCountEqual(card["tags"], ["#JP", "#SecretSocietyholoX", "#Sea"])