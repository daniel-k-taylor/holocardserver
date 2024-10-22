import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_019(unittest.TestCase):
  engine: GameEngine
  player1: str


  def setUp(self):
    initialize_game_to_third_turn(self)


  def test_hSD01_019_can_only_archive_cheers_on_stage_not_on_cheer_deck(self):
    # QnA: Q15 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have amazing pc on hand without cheers on stage
    add_card_to_hand(self, p1, "hSD01-019")

    p1.archive_attached_cards(p1.get_cheer_ids_on_holomems())

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    reset_mainstep(self)
    main_step_event = engine.all_events[-1]
    validate_actions(self, main_step_event["available_actions"], [
      GameAction.MainStepBloom for _ in range(2 * (len(p1.backstage) + len(p1.center)))
    ] + [
      GameAction.MainStepCollab for _ in range(len(p1.backstage))
    ] + [
      GameAction.MainStepBeginPerformance,
      GameAction.MainStepEndTurn
    ]) # no action available to activate amazing pc since no cheer on stage