import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  def setUp(self):
    p1_deck = generate_deck_with("hSD01-001") # Sora Oshi
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd01_001_replacement_with_no_cheers_on_stage(self):
    # QnA: Q1 (2024.09.21)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    p1.generate_holopower(1)
    p1.archive_attached_cards(p1.get_cheer_ids_on_holomems())

    # Events    
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_GenerateHolopower, { "generating_player_id": self.player1 }),
      (EventType.EventType_MoveAttachedCard, {}),
      (EventType.EventType_MoveAttachedCard, {})
    ])

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "replacement" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD01_001_soyouretheenemy_can_target_resting_holomem(self):
    # QnA: Q203 (2024.10.04)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup for p2 to use soyouretheenemy on p1's resting holomem
    target_card_id = "player1_2"
    do_collab_get_events(self, p1, target_card_id)
    end_turn(self) # p1 end turn
    
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self) # p2 end turn

    do_cheer_step_on_card(self, p1.center[0])
    reset_mainstep(self)

    self.assertEqual(p1.backstage[-1]["game_card_id"], target_card_id)
    self.assertTrue(p1.backstage[-1]["resting"])
    end_turn(self) # p1 end turn
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player2)
    p2.generate_holopower(2)

    do_cheer_step_on_card(self, p2.center[0])
    reset_mainstep(self)    
    engine.handle_game_message(self.player2, GameAction.MainStepOshiSkill, { "skill_id": "soyouretheenemy" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player2, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_Decision_SwapHolomemToCenter, {})
    ])

    # check that target_card_id is in the choices
    self.assertEqual(events[-1]["event_player_id"], self.player2)
    self.assertIn(target_card_id, events[-1]["cards_can_choose"])
    
    
  def test_hSD01_001_resolve_as_much_as_possible_for_soyouretheenemy(self):
    # QnA: Q204 (2024.10.04)
    # First part can fizzle out (swap holomem). But the +damage still applies.
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup for p2 to use soyouretheenemy on an empty backstage
    p1.backstage = []
    end_turn(self) # p1 end turn

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player2)
    do_cheer_step_on_card(self, p2.center[0])
    p2.generate_holopower(2)

    reset_mainstep(self)
    engine.handle_game_message(self.player2, GameAction.MainStepOshiSkill, { "skill_id": "soyouretheenemy" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player2, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])