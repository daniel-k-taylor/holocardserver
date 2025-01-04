import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_090(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-090": 1, # support Mascot
    })
    p2_deck = generate_deck_with("", {
      "hBP02-090": 1, # support Mascot
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_090_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Attach Mascot to center
    center_card = p1.center[0]
    center_hp = center_card["hp"]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-090", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 20)


  def test_hbp02_090_attached_effect_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup p2 center with damaged Fubuki attached with Mascot
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-008", p2.center))
    p2_center_card["damage"] = p2_center_card["hp"] - 10
    spawn_cheer_on_card(self, p2, p2_center_card_id, "white", "w1")
    _, p2_mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-090", p2_center_card["attached_support"]))

    _, p2_target_id = unpack_game_id(p2.backstage[0])
    p2_cheer_id = f"{self.player2}_w1"


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(p2_center_card["attached_support"]), [p2_mascot_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": {
        p2_cheer_id: p2_target_id
      }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_Decision_SendCheer, { "from_options": [p2_cheer_id] }),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": p2_center_card_id, "to_holomem_id": p2_target_id, "attached_id": p2_cheer_id }),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  def test_hbp02_090_attached_effect_to_fubuki_no_cheers(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup p2 center with damaged Fubuki attached with Mascot
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-008", p2.center))
    p2_center_card["damage"] = p2_center_card["hp"] - 10
    _, p2_mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-090", p2_center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(p2_center_card["attached_support"]), [p2_mascot_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_090_attached_effect_to_fubuki_only_one_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup p2 center with damaged Fubuki attached with Mascot
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-008", p2.center))
    p2_center_card["damage"] = p2_center_card["hp"] - 10
    spawn_cheer_on_card(self, p2, p2_center_card_id, "white", "w1")
    _, p2_mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-090", p2_center_card["attached_support"]))

    # Only one target option for p2
    p2.collab = []
    p2.backstage = p2.backstage[:1]

    _, p2_target_id = unpack_game_id(p2.backstage[0])
    p2_cheer_id = f"{self.player2}_w1"


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(p2_center_card["attached_support"]), [p2_mascot_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": p2_center_card_id, "to_holomem_id": p2_target_id, "attached_id": p2_cheer_id }),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_090_attached_effect_not_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup p2 center attached with Mascot
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_center_card["damage"] = p2_center_card["hp"] - 10
    spawn_cheer_on_card(self, p2, p2_center_card_id, "white", "w1")
    _, p2_mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-090", p2_center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(p2_center_card["attached_support"]), [p2_mascot_card_id])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun" }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])