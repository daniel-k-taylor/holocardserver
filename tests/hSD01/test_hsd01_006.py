import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_006(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  def setUp(self):
    initialize_game_to_third_turn(self)

  def test_hSD01_006_sorazsympathy_works_with_soraz(self):
    # QnA: Q4 (2024.09.21)
    # QnA: Q5 (2024.09.21)

    # Setup to put sora 1st buzz to center with soraz
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-006", p1.center)
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "white", "w1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g2")

    p1.backstage = []
    collab_card = put_card_in_play(self, p1, "hSD01-013", p1.backstage)

    downed_holomem = p2.center[0] # holomem to be downed after the attack

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazsympathy",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    center_art = 60
    art_boost = 50

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": art_boost, "source_card_id": p1.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": center_art + art_boost }), # damage boost applies
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

  
  def test_hSD01_006_sorazsympathy_works_with_azki_cards(self):
    # Setup to put sora 1st buzz to center with an azki card
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-006", p1.center)
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "white", "w1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g2")

    p1.backstage = []
    collab_card = put_card_in_play(self, p1, "hSD01-008", p1.backstage)

    downed_holomem = p2.center[0] # holomem to be downed after the attack

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazsympathy",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    center_art = 60
    art_boost = 50

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": art_boost, "source_card_id": p1.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": center_art + art_boost }), # damage boost applies
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

  def test_hSD01_006_sorazsympathy_does_not_work_with_other_names(self):
    # Setup to put sora 1st buzz to center
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-006", p1.center)
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "white", "w1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g2")

    downed_holomem = p2.center[0] # holomem to be downed after the attack

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    collab_card = p1.backstage[0]

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sorazsympathy",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    center_art = 60

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_DamageDealt, { "damage": center_art }), # no damage boost
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])