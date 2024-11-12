import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_002(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-002": 10, # debut Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_002_konnakiri(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konnakiri",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konnakiri", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_002_batonpass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    # Setup to have debut Ayame in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, back_card_id = unpack_game_id(p1.backstage[0])

    self.assertEqual(len(center_card["attached_cheer"]), 0) # card has no baton pass cost


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBatonPass, { "card_id": back_card_id, "cheer_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "center", "to_zone": "backstage", "card_id": center_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "backstage", "to_zone": "center", "card_id": back_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
  
  
  def test_hSD02_002_overall_check(self):
    # check for card having no card count limit
    result = card_db.validate_deck(
        "hSD01-001",
        {
          "hSD02-002": 50, # all debut Ayame
        },
        {
          "hY03-001": 20, # red cheers
        }
      )

    self.assertTrue(result)

    # check for hp and tags
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-002"), None)
    self.assertIsNotNone(card)

    self.assertEqual(card["hp"], 90)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])
    
  