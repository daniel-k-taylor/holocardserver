import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_012(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-012": 2, # 1st Fubuki
      "hBP02-089": 2, # support Mascot
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_012_pleaseuseyourstrength_with_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseuseyourstrength",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "pleaseuseyourstrength", "power": 50 }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 70 }),
      *end_turn_events()
    ])

    
  def test_hbp02_012_pleaseuseyourstrength_with_effect_and_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2")
    put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"])

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseuseyourstrength",
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
      (EventType.EventType_PerformArt, { "art_id": "pleaseuseyourstrength", "power": 50 }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 70 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
      (EventType.EventType_PerformArt, { "art_id": "konkonkitsune", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])

  def test_hbp02_012_pleaseuseyourstrength_with_effect_two_012(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r2") # any color
    put_card_in_play(self, p1, "hBP02-089", collab_card["attached_support"])

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseuseyourstrength",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseuseyourstrength",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "pleaseuseyourstrength", "power": 50 }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 70 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
      (EventType.EventType_PerformArt, { "art_id": "pleaseuseyourstrength", "power": 50 }),
      (EventType.EventType_BoostStat, { "amount": 20, "source_card_id": center_card_id }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_BoostStat, { "amount": 20, "source_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 90 }),
      *end_turn_events()
    ])


  def test_hbp02_012_pleaseuseyourstrength_with_effect_no_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseuseyourstrength",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "pleaseuseyourstrength", "power": 50 }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])


  def test_hbp02_012_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki to bloom
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"]))
    bloom_card, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-012"))

    target_card, target_card_id = unpack_game_id(p1.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [mascot_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [target_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [mascot_card_id] }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),

      (EventType.EventType_MoveCard, { "from_zone": bloom_card_id, "to_zone": "holomem", "zone_card_id": target_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(bloom_card["attached_support"]), 0)
    self.assertCountEqual(ids_from_cards(target_card["attached_support"]), [mascot_card_id])


  def test_hbp02_012_bloom_effect_no_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki to bloom
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-012"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(len(center_card["attached_support"]), 0)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_012_bloom_effect_exclude_holomem_that_has_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki to bloom
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"]))
    bloom_card, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-012"))

    excluded_card = p1.backstage[0]
    _, excluded_mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-089", excluded_card["attached_support"]))
    valid_target_ids = ids_from_cards(p1.backstage[1:])
    target_card, target_card_id = unpack_game_id(p1.backstage[1])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [mascot_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [target_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [mascot_card_id, excluded_mascot_card_id] }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_MoveCard, { "from_zone": bloom_card_id, "to_zone": "holomem", "zone_card_id": target_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(bloom_card["attached_support"]), 0)
    self.assertCountEqual(ids_from_cards(target_card["attached_support"]), [mascot_card_id])
    self.assertCountEqual(ids_from_cards(excluded_card["attached_support"]), [excluded_mascot_card_id])


  def test_hbp02_012_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-012", p1.center))
  
  
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


  def test_hbp02_012_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-012"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 100)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen1", "#Gamers", "#AnimalEars", "#Art"])