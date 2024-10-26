import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_011(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  def setUp(self):
    initialize_game_to_third_turn(self)
  

  def test_hsd01_011_sorazgravity_works_with_soraz(self):
    # QnA: Q10 (2024.09.21)
    
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to put hSD01-011 to center and collab with SorAZ
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-011", p1.center)
    center_card_id = center_card["game_card_id"]
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g2")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g3")

    p1.backstage = p1.backstage[1:]
    collab_card = put_card_in_play(self, p1, "hSD01-013", p1.backstage)
    collab_card_id = collab_card["game_card_id"]

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazgravity",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1 }),
      # bonus art effect triggered with soraz
      (EventType.EventType_Decision_SendCheer, { "from_zone": "cheer_deck", "to_zone": "holomem" })
    ])


  def test_hsd01_011_sorazgravity_works_with_sora_cards(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to put hSD01-011 to center and collab with a sora card
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-011", p1.center)
    center_card_id = center_card["game_card_id"]
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g2")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g3")

    collab_card_id = p1.backstage[0]["game_card_id"]

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazgravity",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1 }),
      # bonus art effect triggered with soraz
      (EventType.EventType_Decision_SendCheer, { "from_zone": "cheer_deck", "to_zone": "holomem" })
    ])

  def test_hSD01_011_sorazgravity_does_not_work_with_other_names(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to put hSD01-011 to center and collab with a non-sora card
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-011", p1.center)
    center_card_id = center_card["game_card_id"]
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g2")
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g3")

    p1.backstage = [] # empty backstage
    colalb_card = put_card_in_play(self, p1, "hSD01-008", p1.backstage)
    collab_card_id = colalb_card["game_card_id"]

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    downed_holomem = p2.center[0] # holomem to be downed after the attack


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazgravity",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }), # bonus art effect not triggered
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, { "from_zone": "life", "to_zone": "holomem" })
    ])