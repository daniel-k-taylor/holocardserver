import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

class Test_hSD01_002(unittest.TestCase):
  engine: GameEngine
  player1: str

  def setUp(self):
    initialize_game_to_third_turn(self)
  

  def test_hSD01_002_micintherighthand_with_no_cheer_on_stage(self):
    # QnA: Q2 (2024.09.21)
    # weird question since this oshi skill targets the archive, not the stage.
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    p1.generate_holopower(3)
    p1.center[0]["attached_cheer"] = [] # empty out cheers on stage
    self.assertEqual(len(p1.get_cheer_ids_on_holomems()), 0)

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "micintherighthand" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD01_002_micintherighthand_with_no_cheer_on_archive(self):
    # QnA: Q2 (2024.09.21)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    p1.generate_holopower(3)
    self.assertEqual(len(p1.archive), 0)

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "micintherighthand" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])