import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_096(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-096": 2, # mascot
      "hBP02-035": 2, # debut Chloe
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_096_increase_damage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Mascot in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])

    self.assertEqual(len(center_card["attached_cheer"]), 2)


  def test_hbp02_096_attached_to_chloe_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup debut Chloe attached with Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))

    # Cheer in p1's archive
    p1.archive = p1.cheer_deck[:1]
    p1.cheer_deck = p1.cheer_deck[1:]

    # p2's center set to near death
    p2.center[0]["damage"] = p2.center[0]["hp"] - 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "bakkubakun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "bakkubakun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": center_card_id }),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_096_attached_to_chloe_effect_no_down(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup debut Chloe attached with Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))

    # Cheer in p1's archive
    p1.archive = p1.cheer_deck[:1]
    p1.cheer_deck = p1.cheer_deck[1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "bakkubakun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "bakkubakun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])
        
    self.assertEqual(len(center_card["attached_cheer"]), 1)


  def test_hbp02_096_attached_to_chloe_effect_no_cheer_in_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup debut Chloe attached with Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))

    # no cheer in p1's archive
    p1.archive = []

    # p2's center set to near death
    p2.center[0]["damage"] = p2.center[0]["hp"] - 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "bakkubakun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "bakkubakun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_096_attached_to_chloe_effect_multiple_holox_holomem(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup debut Chloe attached with Mascot and in collab
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))
    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.collab))

    # Cheer in p1's archive
    p1.archive = p1.cheer_deck[:1]
    p1.cheer_deck = p1.cheer_deck[1:]

    # p2's center set to near death
    p2.center[0]["damage"] = p2.center[0]["hp"] - 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "bakkubakun",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p1.archive[0]["game_card_id"]: collab_card_id }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "bakkubakun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_Decision_SendCheer, {}),
      
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": collab_card_id }),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertEqual(len(collab_card["attached_cheer"]), 1)
    self.assertEqual(len(p1.archive), 0)


  def test_hbp02_096_only_one_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup debut Chloe attached with Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-035", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, attached_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-096", center_card["attached_support"]))

    # Mascot in hand
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-096"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": attached_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(center_card["attached_support"]), 1)