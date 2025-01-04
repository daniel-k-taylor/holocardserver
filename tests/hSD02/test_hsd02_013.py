import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_013(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-013": 2, # support asura & rakshasa
      "hSD02-002": 1, # debut Ayame
      "hSD02-005": 1, # 1st Ayame
      "hSD02-009": 1, # 2nd ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd02_013_boost_arts(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have tool card in hand
    _, tool_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-013"))

    _, center_card_id = unpack_game_id(p1.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": tool_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

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
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hsd02_013_1st_ayame_bonus_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have 1st ayame in the center and attached with the tool
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-005", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    _, tool_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sleepyyo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "sleepyyo", "power": 20 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }), # extra boost from effect
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hsd02_013_2nd_ayame_boost_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have 2nd ayame in the center and attached with the tool
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")

    _, tool_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "theayainayafubumi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "theayainayafubumi", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }), # extra boost from effect
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hsd02_013_debut_ayame_no_boost_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have 2nd ayame in the center and attached with the tool
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")

    _, tool_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konnakiri",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konnakiri", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "source_card_id": tool_card_id }), # no boost
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hsd02_013_only_one_tool(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have one tool attached and another in hand
    center_card, center_card_id = unpack_game_id(p1.center[0])
    _, attached_tool_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-013", center_card["attached_support"]))
    _, tool_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-013"))

    valid_target_ids = ids_from_cards(p1.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": tool_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [attached_tool_card_id])
    self.assertTrue(center_card_id not in valid_target_ids)
    