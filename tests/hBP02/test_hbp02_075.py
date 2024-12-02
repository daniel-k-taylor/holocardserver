import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_075(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-075": 2, # item card
      "hBP02-061": 2, # debut Ina
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_075_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have gravity in hand and 2 ina on top of deck
    p1.hand = p1.hand[:3] # 3 cards in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-075"))
    p1.deck = p1.deck[-2:] + p1.deck[:-2]

    art_card_ids = ids_from_cards(p1.deck[:2])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": item_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": art_card_ids })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[2:4]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": item_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": art_card_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.hand[-2:]), art_card_ids)


  def test_hbp02_075_effect_no_art(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have gravity in hand
    p1.hand = p1.hand[:3] # 3 cards in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-075"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": item_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[:4]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": item_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(p1.hand), 3)


  def test_hbp02_075_more_than_6_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have gravity in hand
    p1.hand = p1.hand[:3] # 3 cards in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-075"))

    # More than 6 in hand
    p1.hand += p1.deck[:6]
    p1.deck = p1.deck[6:]

    actions = reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertGreater(len(p1.hand), 7)
    can_activate_event = any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == item_card_id for action in actions)
    self.assertFalse(can_activate_event)


  def test_hbp02_075_one_limited_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have gravity cards in hand
    p1.hand = p1.hand[:3] # 3 cards in hand
    _, item_1_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-075"))
    _, item_2_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-075"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": item_1_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[:4]) })

    # Events
    actions = engine.grab_events()[-2]["available_actions"]
    can_activate_event = any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == item_2_card_id for action in actions)
    self.assertFalse(can_activate_event)