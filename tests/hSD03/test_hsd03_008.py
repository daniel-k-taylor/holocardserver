import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_008(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-008": 2, # buzz Okayu
      "hSD03-010": 1, # spot Korone
    })
    p2_deck = generate_deck_with("", {
      "hSD03-008": 1
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hsd03_008_themostnoblenekomataokayu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "themostnoblenekomataokayu",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "themostnoblenekomataokayu", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hsd03_008_gift(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and Korone in collab
    p1.center = []
    p1.collab = []
    put_card_in_play(self, p1, "hSD03-008", p1.center)
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "orayo",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "orayo", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])


  def test_hsd03_008_gift_okayu_not_center(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Korone in the center and Okayu in collab
    p1.center = []
    p1.collab = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    put_card_in_play(self, p1, "hSD03-008", p1.collab)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "orayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "orayo", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hsd03_008_collab_not_valid_name(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and not a valid name in collab
    p1.center = []
    put_card_in_play(self, p1, "hSD03-008", p1.center)
    collab_card, collab_card_id = unpack_game_id(p1.backstage[0])
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1") # any color
    p1.collab = [collab_card]
    p1.backstage = p1.backstage[1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hsd03_008_downed_life(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have player2 hava a damaged Okayu in the center
    p2.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD03-008", p2.center))
    center_card["damage"] = center_card["hp"] - 1


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
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "life_lost": 2 }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  # baton pass
  def test_hsd03_008_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-008", p1.center))
  
  
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
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    actions = reset_mainstep(self)
    self.assertIsNotNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))


  def test_hsd03_008_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-008"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 240)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])