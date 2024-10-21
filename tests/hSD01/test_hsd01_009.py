import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_009(unittest.TestCase):
  engine: GameEngine
  player1: str
    
  
  def setUp(self):
    initialize_game_to_third_turn(self)
  

  def test_hSD01_009_collab_effect_works_even_with_empty_cheer_deck(self):
    # QnA: Q7 (2024.09.21)
    
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.backstage = p1.backstage[1:5]
    collab_card = put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    p1.cheer_deck = [] # empty cheer deck

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_Choice, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 1, "rigged": False }),
      (EventType.EventType_Choice_SendCollabBack, {})
    ]) # events skipped moving cheer from cheer deck

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_MainStep, {})
    ])

  def test_hSD01_009_collab_effect_moves_cheer_from_cheer_deck(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.backstage = p1.backstage[1:5]
    collab_card = put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_Choice, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 1, "rigged": False }),
      (EventType.EventType_Decision_SendCheer, {}) # triggered since we have a card in the cheer deck
    ])


  def test_hSD01_009_azki_will_stay_the_same_orientation_when_sent_back_from_collab_effect(self):
    # QnA: Q8 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.backstage = p1.backstage[1:5]
    collab_card = put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    p1.cheer_deck = [] # empty cheer deck

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_Choice, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 1, "rigged": False }),
      (EventType.EventType_Choice_SendCollabBack, {})
    ]) # events skipped moving cheer from cheer deck

    self.assertFalse(collab_card["resting"]) # check that it is not resting and will be checked again after returning to backstage

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "collab", "to_zone": "backstage" }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.backstage), 5)
    self.assertFalse(collab_card["resting"]) # the orientation did not change


  def test_hSD01_009_cannot_collab_after_collab_send_back(self):
    # QnA: Q9 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.backstage = p1.backstage[1:5]
    collab_card = put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    p1.cheer_deck = [] # empty cheer deck

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_Choice, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 1, "rigged": False }),
      (EventType.EventType_Choice_SendCollabBack, {})
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "collab", "to_zone": "backstage" }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.backstage), 5)
    # no collab as available action
    self.assertFalse(any(action["action_type"] == GameAction.MainStepCollab for action in events[-2]["available_actions"]))