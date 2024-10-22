import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_017(unittest.TestCase):
  engine: GameEngine
  player1: str

  def setUp(self):
    initialize_game_to_third_turn(self)

  
  def test_hSD01_017_need_at_least_one_card_other_than_manechan_to_activate(self):
    # QnA: Q14 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have mane-chan on hand with no other cards
    p1.hand = []
    add_card_to_hand(self, p1, "hSD01-017")

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    self.assertEqual(len(p1.hand), 1)

    main_step_event = engine.all_events[-2]
    self.assertEqual(main_step_event["active_player"], self.player1)

    validate_actions(self, main_step_event["available_actions"], [
      GameAction.MainStepBloom for _ in range((len(p1.backstage) + len(p1.center)) * 2)
    ] + [
      GameAction.MainStepCollab for _ in range(len(p1.backstage))
    ] + [
      GameAction.MainStepBatonPass,
      GameAction.MainStepBeginPerformance,
      GameAction.MainStepEndTurn
    ]) # no available action to use mane-chan
