import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_021(unittest.TestCase):
  engine: GameEngine
  player1: str

  def setUp(self):
    initialize_game_to_third_turn(self)

  
  # QnA: Q17 is covered by hSD01-013


  def test_hSD01_021_can_be_used_when_you_have_six_other_cards_in_hand(self):
    # QnA: Q16 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have first gravity and six cards in hand
    self.assertEqual(len(p1.hand), 3)
    p1.hand = p1.hand + p1.deck[:3]
    p1.deck = p1.deck[3:]
    self.assertEqual(len(p1.hand), 6)

    add_card_to_hand(self, p1, "hSD01-021")
    self.assertEqual(len(p1.hand), 7) # hand now has 1 debut, 5 1st bloom and first gravity


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    main_step_event = engine.all_events[-1]
    validate_actions(self, main_step_event["available_actions"], [
      GameAction.MainStepBloom for _ in range(5 * (len(p1.backstage) + len(p1.center)))
    ] + [
      GameAction.MainStepCollab for _ in range(len(p1.backstage))
    ] + [
      GameAction.MainStepPlaySupport, # first gravity can be activated with 6 cards in hand excluding itself
      GameAction.MainStepBatonPass,
      GameAction.MainStepBeginPerformance,
      GameAction.MainStepEndTurn
    ])
