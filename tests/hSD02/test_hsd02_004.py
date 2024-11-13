import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_003(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-004": 2, # debut collab Ayame U
      "hSD02-014": 1, # Poyoyo
      "hBP01-118": 1, # Ankimo
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_004_deliciousdangos(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "deliciousdangos",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "deliciousdangos", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_004_collab_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame both in the center and backstage
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.backstage))

    # Attach Poyoyo to collab Ayame
    put_card_in_play(self, p1, "hSD02-014", collab_card["attached_support"])
    reset_mainstep(self)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "deliciousdangos",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "deliciousdangos", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])


  def test_hSD02_004_collab_effect_without_poyoyo_attached(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame both in the center and backstage
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.backstage))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_MainStep, {}) # No Ayame boost
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "deliciousdangos",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "deliciousdangos", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_004_collab_effect_with_different_mascot(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame both in the center and backstage
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.backstage))

    # Attach Ankimo to collab Ayame
    put_card_in_play(self, p1, "hBP01-118", collab_card["attached_support"])
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_MainStep, {}) # No Ayame boost
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "deliciousdangos",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "deliciousdangos", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_004_baton_pass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Ayame in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-004", p1.center))
    _, back_card_id = unpack_game_id(p1.backstage[0])

    self.assertEqual(len(center_card["attached_support"]), 0)


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


  def test_hSD02_004_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-004"), None)
    self.assertIsNotNone(card)

    # check for hp and tags
    card["hp"] = 60
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])