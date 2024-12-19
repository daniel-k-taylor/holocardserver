import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_089(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-089": 1, # support Mascot
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_089_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Attach Mascot to center
    center_card = p1.center[0]
    center_hp = center_card["hp"]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 20)


  def test_hbp02_089_effect_attached_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki in the backstage and attach it with Mascot
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_089_effect_not_attached_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Attache Mascot to backstage holomem
    collab_card, collab_card_id = unpack_game_id(p1.backstage[0])
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])