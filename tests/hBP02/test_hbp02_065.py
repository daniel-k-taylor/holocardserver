import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_065(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-065": 1, # debut Nerissa
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_065_fn_name(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
  # art1 red cheer
  # baton pass


  def test_hbp02_065_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-065"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 90)
    self.assertCountEqual(card["tags"], ["#EN", "#Advent", "#Song", "#Bird"])

    # check for no card limit
    self.assertTrue(card_db.validate_deck("hSD01-001", { "hBP02-065": 50 }, { "hY03-001": 20 }))