import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_012(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-012": 2, # ayafubumi gravity
      "hSD02-002": 1, # debut Ayame
      "hSD02-010": 1, # spot Fubuki
      "hSD02-011": 1, # spot Mio
    })
    initialize_game_to_third_turn(self, p1_deck)


  # get all three
  def test_hsd02_012_get_all_names(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have gravity card in hand and deck stacked with the correct names
    correct_names = p1.deck[-3:]
    correct_names_ids = ids_from_cards(correct_names)
    p1.deck = correct_names + p1.deck[:-3]

    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-012"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": correct_names_ids })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": correct_names_ids })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": ids_from_cards([p1.deck[4]]) })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand" }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }), # back to bottom of deck
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive", "card_id": support_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.hand[-3:]), correct_names_ids)


  # get none
  def test_hsd02_012_get_none(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have gravity card in hand
    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-012"))

    shuffled_cards = ids_from_cards(p1.deck[:4])
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": shuffled_cards })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [], "all_card_seen": shuffled_cards }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  # once per turn
  def test_hsd02_012_once_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have two gravity card in hand
    _, support_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-012"))
    _, support_2_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-012"))

    shuffled_cards = ids_from_cards(p1.deck[:4])
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": shuffled_cards })

    # Events
    events = engine.grab_events()
    actions = events[-2]["available_actions"]
    # cannot use the second gravity card
    self.assertIsNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == support_2_card_id), None))


  # less than 6
  def test_hsd02_012_more_than_6_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have gravity card in hand
    add_card_to_hand(self, p1, "hSD02-012")

    # add more cards to hand
    p1.hand += p1.deck[:10]
    p1.deck = p1.deck[10:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    actions = reset_mainstep(self)
    # cannot activate gravity card
    self.assertIsNone(next((action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport), None))