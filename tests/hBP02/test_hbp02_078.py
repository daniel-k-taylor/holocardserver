import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_078(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-078": 2, # support event
      "hBP01-009": 1, # debut Kanata
      "hBP01-044": 1, # debut Azki
      "hBP02-035": 2, # debut Chloe
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_078_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Event card in hand
    _, event_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))

    # Put kanaken cards on top of the deck
    p1.deck = p1.deck[-4:] + p1.deck[:-4]
    kanaken_card_ids = ids_from_cards(p1.deck[:4])

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": event_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": kanaken_card_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": kanaken_card_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_078_effect_choose_no_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Event card in hand
    _, event_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))

    # Put kanaken cards on top of the deck
    p1.deck = p1.deck[-4:] + p1.deck[:-4]
    kanaken_card_ids = ids_from_cards(p1.deck[:4])

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": event_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": kanaken_card_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": kanaken_card_ids }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_078_limited(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Event cards in hand
    _, event_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))
    _, duplicate_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))

    # Put kanaken cards on top of the deck
    p1.deck = p1.deck[-4:] + p1.deck[:-4]
    kanaken_card_ids = ids_from_cards(p1.deck[:4])

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    actions = reset_mainstep(self)
    self.assertEqual(len([action for action in actions \
                          if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] in [event_card_id, duplicate_card_id]]), 2)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": event_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": kanaken_card_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": kanaken_card_ids }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    actions = events[-2]["available_actions"]
    self.assertEqual(len([action for action in actions \
                          if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] in [event_card_id, duplicate_card_id]]), 0)


  def test_hbp02_078_less_than_7_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Event card in hand
    _, event_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))

    # Increase hand size
    p1.hand += p1.deck[:10]
    p1.deck = p1.deck[10:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    self.assertFalse(any([action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == event_card_id for action in actions]))

    
  def test_hbp02_078_no_valid_targets(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Event card in hand
    _, event_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-078"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": event_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[:4]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])