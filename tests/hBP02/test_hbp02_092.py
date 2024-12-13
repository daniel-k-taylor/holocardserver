import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_092(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-092": 2, # support Mascot
      "hBP02-008": 2, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_092_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup center attached with Mascot
    center_card = p1.center[0]
    center_hp = center_card["hp"]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 20)


  def test_hbp02_092_attached_effect_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center attached with the Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))

    cheer_ids = ids_from_cards([
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w1"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w2"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w3")
    ])
    archived_cheer_ids = cheer_ids[:2]

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepAttachedAction, { "effect_id": "fubuzilla", "support_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": archived_cheer_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AttachedActionActivation, { "effect_id": "fubuzilla" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cheer_ids }),

      (EventType.EventType_MoveCard, { "from_zone": center_card_id, "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": center_card_id, "to_zone": "archive" }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 50, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      *end_turn_events()
    ])

    
  def test_hbp02_092_attached_effect_to_fubuki_multiple_cheers_from_different_sources(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center attached with the Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))

    cheer_ids = ids_from_cards([
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w1"),
      spawn_cheer_on_card(self, p1, p1.backstage[0]["game_card_id"], "red", "r1"),
      spawn_cheer_on_card(self, p1, p1.backstage[1]["game_card_id"], "red", "r2")
    ])
    archived_cheer_ids = cheer_ids[1:]

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepAttachedAction, { "effect_id": "fubuzilla", "support_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": archived_cheer_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AttachedActionActivation, { "effect_id": "fubuzilla" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cheer_ids }),

      (EventType.EventType_MoveCard, { "from_zone": p1.backstage[0]["game_card_id"], "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": p1.backstage[1]["game_card_id"], "to_zone": "archive" }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 50, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      *end_turn_events()
    ])
    self.assertEqual(len(p1.backstage[0]["attached_cheer"]), 0)
    self.assertEqual(len(p1.backstage[1]["attached_cheer"]), 0)


  def test_hbp02_092_attached_effect_to_fubuki_once_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the center attached with the Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))

    cheer_ids = ids_from_cards([
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w1"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w2"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w3"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w4"),
    ])
    archived_cheer_ids = cheer_ids[:2]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepAttachedAction, { "effect_id": "fubuzilla", "support_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": archived_cheer_ids })

    engine.grab_events()
    self.assertEqual(len(center_card["attached_cheer"]), 2)

    actions = reset_mainstep(self)
    self.assertFalse(
      any(action["action_type"] == GameAction.MainStepAttachedAction and action["effect_id"] == "fubuzilla" and action["support_id"] == mascot_card_id \
          for action in actions))


  #attached effect to fubuki not enough cheers to distribute
  def test_hbp02_092_attached_effect_to_fubuki_not_enough_cheers_to_distribute(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the center attached with the Mascot
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])

    actions = reset_mainstep(self)
    self.assertFalse(
      any(action["action_type"] == GameAction.MainStepAttachedAction and action["effect_id"] == "fubuzilla" and action["support_id"] == mascot_card_id \
          for action in actions))


  def test_hbp02_092_attached_effect_to_fubuki_only_activated_support_card_gets_boost(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center attached with the Mascot and collab
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))

    p2.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.collab))
    put_card_in_play(self, p1, "hBP02-092", collab_card["attached_support"])

    cheer_ids = ids_from_cards([
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w1"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w2"),
      spawn_cheer_on_card(self, p1, center_card_id, "white", "w3"),
      spawn_cheer_on_card(self, p1, collab_card_id, "white", "w4")
    ])
    archived_cheer_ids = cheer_ids[:2]

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])

    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepAttachedAction, { "effect_id": "fubuzilla", "support_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": archived_cheer_ids })

    engine.grab_events()

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konkonkitsune",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30, "performer_id": center_card_id }),
      (EventType.EventType_BoostStat, { "amount": 50, "source_card_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      (EventType.EventType_Decision_PerformanceStep, {}),

      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30, "performer_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])

    
  def test_hbp02_092_attached_effect_not_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the center attached with the Mascot
    center_card = p1.center[0]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-092", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertGreaterEqual(len(center_card["attached_cheer"]), 2)

    actions = reset_mainstep(self)
    self.assertFalse(
      any(action["action_type"] == GameAction.MainStepAttachedAction and action["effect_id"] == "fubuzilla" and action["support_id"] == mascot_card_id \
          for action in actions))
    