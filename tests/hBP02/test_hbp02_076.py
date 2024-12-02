import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_076(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-076": 1, # item support
      "hBP02-014": 1, # debut Noel
      "hBP02-015": 1, # 1st Noel
      "hBP02-017": 1, # buzz Noel
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_076_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup support item and debut Noel in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-076"))
    _, debut_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-014"))

    _, bloom_card_id = unpack_game_id(p1.deck[-2])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": item_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [debut_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "deck", "card_id": debut_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [bloom_card_id] }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": bloom_card_id }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": item_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_076_effect_no_debut_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup support item in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-076"))

    # Remove debuts in hand
    p1.hand = p1.hand[1:]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertFalse(any(card["card_type"].endswith("debut") for card in p1.hand))

    actions = reset_mainstep(self)
    self.assertFalse(any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == item_card_id for action in actions))


  def test_hbp02_076_effect_no_bloom_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup support item and debut and 1st Noel in hand
    _, item_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-076"))
    _, debut_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-014"))
    add_card_to_hand(self, p1, "hBP02-015")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": item_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [debut_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "deck", "card_id": debut_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": item_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])