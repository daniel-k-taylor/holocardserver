import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_005(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  
  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-005": 1, # 1st bloom Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd02_005_sleepyyo(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-005", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sleepyyo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "sleepyyo", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hsd02_005_otsunakiri(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-005", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "otsunakiri",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "otsunakiri", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}), # opposing center only has 60 hp
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hsd02_005_batonpass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-005", p1.center))
    _, back_card_id = unpack_game_id(p1.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # no cheers needed for baton pass
    engine.handle_game_message(self.player1, GameAction.MainStepBatonPass, { "card_id": back_card_id, "cheer_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "center", "to_zone": "backstage", "card_id": center_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "backstage", "to_zone": "center", "card_id": back_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_005_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-005"), None)
    self.assertIsNotNone(card)

    # check for hp and tags
    self.assertEqual(card["hp"], 140)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])