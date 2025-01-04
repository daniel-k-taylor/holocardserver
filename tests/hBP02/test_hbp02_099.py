import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_099(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-099": 2, # support Fan
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_099_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki in the center attached with Fan
    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP02-008", p1.center)
    center_hp = center_card["hp"]
    _, fan_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-099", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [fan_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 10)


  def test_hbp02_099_effect_attached_multiple(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the center attached with Fan
    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP02-008", p1.center)
    center_hp = center_card["hp"]
    _, fan_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-099", center_card["attached_support"]))
    _, fan_2_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-099", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [fan_card_id, fan_2_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 10 * 2)


  def test_hbp02_099_only_attached_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Add Fan to hand
    _, fan_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-099"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertTrue(any(card_id == fan_card_id for card_id in ids_from_cards(p1.hand)))
    
    actions = reset_mainstep(self)
    self.assertFalse(any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == fan_card_id for action in actions))
