import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_017(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-017": 1, # buzz Noel
      "hBP02-014": 5, # debut Noel
    })
    p2_deck = generate_deck_with("", {
      "hBP02-017": 1, # buzz Noel
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_017_afluffymeatheadedknight(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz noel in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "afluffymeatheadedknight",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "afluffymeatheadedknight", "power": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])

    
  def test_hbp02_017_thirdgenerationpower(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz noel in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thirdgenerationpower",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thirdgenerationpower", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_017_collab_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Noel in backstage and debut Noel in center
    p1.center = []
    put_card_in_play(self, p1, "hBP02-014", p1.center)
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.backstage))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r2") # any color

    # collab
    do_collab_get_events(self, p1, collab_card_id)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thirdgenerationpower",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thirdgenerationpower", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_017_collab_effect_no_gen3(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Noel in backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.backstage))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r2") # any color

    # collab
    do_collab_get_events(self, p1, collab_card_id)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thirdgenerationpower",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thirdgenerationpower", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_017_collab_effect_center_and_one_back(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Noel in backstage and debut Noel in center and back
    p1.center = []
    put_card_in_play(self, p1, "hBP02-014", p1.center)
    p1.backstage = p1.backstage[:-2]
    put_card_in_play(self, p1, "hBP02-014", p1.backstage)
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.backstage))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r2") # any color

    # collab
    do_collab_get_events(self, p1, collab_card_id)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thirdgenerationpower",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thirdgenerationpower", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 20 * 2 }),
      (EventType.EventType_DamageDealt, { "damage": 60 + 20 * 2 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_017_collab_effect_center_and_full_back(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Noel in backstage and debut Noel in center
    p1.center = []
    put_card_in_play(self, p1, "hBP02-014", p1.center)
    p1.backstage = []
    put_card_in_play(self, p1, "hBP02-014", p1.backstage)
    put_card_in_play(self, p1, "hBP02-014", p1.backstage)
    put_card_in_play(self, p1, "hBP02-014", p1.backstage)
    put_card_in_play(self, p1, "hBP02-014", p1.backstage)
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.backstage))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1") # any color
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r2") # any color

    # collab
    do_collab_get_events(self, p1, collab_card_id)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thirdgenerationpower",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thirdgenerationpower", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 20 * 4 }),
      (EventType.EventType_DamageDealt, { "damage": 60 + 20 * 4 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_017_buzz_downed_life(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have p2 have a damaged buzz noel in the center
    p2.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-017", p2.center))
    center_card["damage"] = center_card["hp"] - 10


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
      (EventType.EventType_DownedHolomem, { "life_lost": 2, "target_player": self.player2 }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  def test_hbp02_017_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-017", p1.center))
  
  
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


  def test_hbp02_017_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-017"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 260)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen3", "#Alcohol"])