import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_012(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def test_hsd03_012_reveal_first_three_valid_targets(self):
    p1_deck = generate_deck_with("", {
      "hSD03-012": 1, # support Durobo Construction
      "hSD03-002": 1, # debut Okayu
      "hBP01-056": 1, # debut Lui
      "hSD02-011": 1, # spot Mio
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Add 2 support to hand
    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-012"))

    # Make sure hand size is less than 6
    p1.hand = p1.hand[-1:]

    # Move the three valid cards in front
    correct_names = p1.deck[-3:]
    correct_names_ids = ids_from_cards(correct_names)
    p1.deck = correct_names + p1.deck[:-3]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": correct_names_ids })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards([p1.deck[4]]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": correct_names_ids }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": support_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    
    
  def test_hsd03_012_reveal_second_three_valid_targets(self):
    p1_deck = generate_deck_with("", {
      "hSD03-012": 1, # support Durobo Construction
      "hSD02-010": 1, # spot Fubuki
      "hSD03-011": 1, # spot Laplus
      "hSD03-010": 1, # spot Korone
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Add 2 support to hand
    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-012"))

    # Make sure hand size is less than 6
    p1.hand = p1.hand[-1:]

    # Move the three valid cards in front
    correct_names = p1.deck[-3:]
    correct_names_ids = ids_from_cards(correct_names)
    p1.deck = correct_names + p1.deck[:-3]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": correct_names_ids })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards([p1.deck[4]]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": correct_names_ids }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": support_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd03_012_no_targets(self):
    p1_deck = generate_deck_with("", {
      "hSD03-012": 2, # support Durobo Construction
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Add 2 support to hand
    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-012"))

    # Make sure hand size is less than 6
    p1.hand = p1.hand[-1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[:4]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": support_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  # limited
  def test_hsd03_012_limited(self):
    p1_deck = generate_deck_with("", {
      "hSD03-012": 2, # support Durobo Construction
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Add 2 support to hand
    _, support_1_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-012"))
    _, support_2_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-012"))

    # Make sure hand size is less than 6
    p1.hand = p1.hand[-2:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLessEqual(len(p1.hand), 7)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_1_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards(p1.deck[:4]) })

    # actions
    actions = reset_mainstep(self)
    self.assertIsNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == support_2_card_id), None))