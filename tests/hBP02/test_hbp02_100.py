import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_100(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-100": 4, # fan
      "hBP02-014": 1, # debut Noel
    })
    p2_deck = generate_deck_with("", {
      "hBP02-100": 4, # fan
      "hBP02-014": 1, # debut Noel
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_100_reduce_damage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup for player2 to have Noel attached with fans
    p2.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-014", p2.center))
    _, fan_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-100", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented", "source_card_id": fan_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hbp02_100_can_only_be_attached_to_noel(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to add Fan to hand
    _, fan_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-100"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    can_attach = any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == fan_card_id for action in actions)
    self.assertFalse(can_attach)

    # Setup one Noel to center
    p1.center = []
    put_card_in_play(self, p1, "hBP02-014", p1.center)

    actions = reset_mainstep(self)
    can_attach = any(action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == fan_card_id for action in actions)
    self.assertTrue(can_attach)


  def test_hbp02_100_effect_stacks(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have three fan on player2's noel center
    center_card, center_card_id = unpack_game_id(p2.center[0])
    put_card_in_play(self, p1, "hBP02-100", center_card["attached_support"])
    put_card_in_play(self, p1, "hBP02-100", center_card["attached_support"])
    put_card_in_play(self, p1, "hBP02-100", center_card["attached_support"])
    put_card_in_play(self, p1, "hBP02-100", center_card["attached_support"])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" , "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented" }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented" }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented" }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented" }),
      (EventType.EventType_DamageDealt, { "damage": 0 }),
      *end_turn_events()
    ])