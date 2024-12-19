import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_093(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-093": 1, # support Mascot
      "hSD03-003": 2, # debut Okayu
    })
    p2_deck = generate_deck_with("", {
      "hBP02-093": 1, # support Mascot
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_093_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup center attached with Mascot
    center_card = p1.center[0]
    center_hp = center_card["hp"]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-093", center_card["attached_support"]))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 20)


  def test_hbp02_093_attached_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Okayu in the center and backstage ready to collab
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup p2 fubuki in the backstage attached with Mascot
    p2.backstage = []
    target_card, target_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-008", p2.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-093", target_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(target_card["attached_support"]), [mascot_card_id])
    
    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "target_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_BoostStat, { "amount": "all", "stat": "damage_prevented", "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 0, "target_id": target_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_093_attached_to_fubuki_not_back(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup p2 Fubuki in center attached with Mascot
    p2.center = []
    target_card, target_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-008", p2.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-093", target_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(target_card["attached_support"]), [mascot_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": target_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_093_attached_not_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Okayu in the center and backstage ready to collab
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup p2 backstage holomem attached with Mascot
    p2.backstage = p2.backstage[:1]
    target_card, target_card_id = unpack_game_id(p2.backstage[0])
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-093", target_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(target_card["attached_support"]), [mascot_card_id])
    
    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "target_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 10, "target_id": target_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])