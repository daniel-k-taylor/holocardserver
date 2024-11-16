import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_006(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-006": 1, # 1st Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_006_nekokaburi(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nekokaburi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nekokaburi", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hsd03_006_shaa_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    _, p2_center_card_id = unpack_game_id(p2.center[0])
    back_ids = ids_from_cards(p2.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": back_ids })
    ])
  
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": back_ids[:1] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": back_ids[0] }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])


  def test_hsd03_006_shaa_effect_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    _, p2_center_card_id = unpack_game_id(p2.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])


  def test_hsd03_006_shaa_effect_no_back_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }), # no choice since no target
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])


  def test_hsd03_006_shaa_effect_no_center_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    # Move center to collab
    p2.collab = p2.center
    p2.center = []
    _, p2_collab_card_id = unpack_game_id(p2.collab[0])
    back_ids = ids_from_cards(p2.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_collab_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": back_ids[:1] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": back_ids }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": back_ids[0] }),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_collab_card_id }),
      *end_turn_events(new_center=True)
    ])
    

  def test_hsd03_006_shaa_effect_downed_back_life_lost(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])
    p2_back_card["damage"] = p2_back_card["hp"] - 10 # shaa damage + effect
    back_ids = ids_from_cards(p2.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_back_card_id] })

    # Events
    events = engine.grab_events()

    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": back_ids }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": p2_back_card_id, "life_lost": 1, "life_loss_prevented": False }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": {
        p2.life[0]["game_card_id"]: p2_center_card_id
      }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "life", "to_holomem_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])


  def test_hsd03_006_shaa_effect_only_one_back(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2.backstage = p2.backstage[:1]
    back_ids = ids_from_cards(p2.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": back_ids[0] }),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])


  # baton pass
  def test_hsd03_006_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
  
  
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


  def test_hsd03_006_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-006"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 140)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars", "#Song"])