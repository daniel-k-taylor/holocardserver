import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_002(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-002": 1, # debut Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_002_mogumoguokayu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "mogumoguokayu",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "mogumoguokayu", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hsd03_002_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
  
  
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
  
    # no cheers to use baton pass
    self.assertEqual(len(center_card["attached_cheer"]), 0)
  
    # Events
    actions = reset_mainstep(self)
    self.assertIsNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))
  
    # with sufficient cheers
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    actions = reset_mainstep(self)
    self.assertIsNotNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))



  def test_hsd03_002_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-002"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 100)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])

    # check for card having no card count limit
    self.assertTrue(card_db.validate_deck(
        "hSD01-001",
        {
          "hSD03-002": 50, # all debut Okayu
        },
        {
          "hY04-001": 20, # blue cheers
        }
      ))