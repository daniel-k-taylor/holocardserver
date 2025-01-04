import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_009(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-009": 1, # debut Fubuki
      "hBP02-008": 2, # debut vanilla Fubuki
      "hBP02-089": 2, # support Mascot
      "hBP02-099": 1, # support Fan
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_009_otsukon(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "otsukon",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "otsukon", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hbp02_009_gift_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup vanilla Fubuki in the center and Gift Fubuki in collab. Both with Mascots attached
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-009", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2")
    put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"])

    # give p2 center high hp
    p2_center, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_center["hp"] = 300

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "otsukon",
      "performer_id": collab_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30, "performer_id": center_card_id }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
      (EventType.EventType_PerformArt, { "art_id": "otsukon", "power": 20, "performer_id": collab_card_id }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_009_gift_effect_not_in_collab_position(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup vanilla Fubuki in collab and Gift Fubuki in center position. Both with Mascots attached
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2")
    put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"])

    # give p2 center high hp
    p2_center, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_center["hp"] = 300

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "otsukon",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": collab_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "otsukon", "power": 20, "performer_id": center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30, "performer_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_009_gift_effect_no_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup vanilla Fubuki in the center and Gift Fubuki in collab. Both with Mascots attached
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-009", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2")
    put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"])

    # give p2 center high hp
    p2_center, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_center["hp"] = 300

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "otsukon",
      "performer_id": collab_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30, "performer_id": center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
      (EventType.EventType_PerformArt, { "art_id": "otsukon", "power": 20, "performer_id": collab_card_id }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hbp02_009_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-009", p1.center))
  
  
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


  def test_hbp02_009_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-009"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 80)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen1", "#Gamers", "#AnimalEars", "#Art"])