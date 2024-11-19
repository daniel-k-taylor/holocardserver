import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_013(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-013": 2, # mascot Okanyan
      "hSD03-002": 1, # debut Okayu
      "hSD03-003": 1, # collab Okayu
      "hSD03-006": 1, # 1st Okayu
    })
    p2_deck = generate_deck_with("", {
      "hSD03-013": 1, # mascot Okanyan
      "hSD03-002": 1, # debut Okayu
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  # reduce damage
  def test_hsd03_013_reduce_damage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player2 center attached with Okanyan
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    _, p2_mascot_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD03-013", p2_center_card["attached_support"]))

    _, center_card_id = unpack_game_id(p1.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 10, "stat": "damage_prevented", "source_card_id": p2_mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  # reduce damage not in center or collab
  def test_hsd03_013_reduce_damage_only_if_center_or_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have collab Okayu in the backstage and Okayu in the center
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup to have player2 backstage attached with Okanyan
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])
    put_card_in_play(self, p2, "hSD03-013", p2_back_card["attached_support"])

    # only one backstage to remove choices
    p2.backstage = p2.backstage[:1]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd03_013_substitute_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have 1st Okayu in the center attached with Okanyan
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-013", center_card["attached_support"]))

    p2.backstage = p2.backstage[:1]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 }) # archive Okanyan instead

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": mascot_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_cheer"]), [f"{self.player1}_b1", f"{self.player1}_w1"])
    self.assertCountEqual(ids_from_cards(p1.archive), [mascot_card_id])


  def test_hsd03_013_do_not_use_substitute_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have 1st Okayu in the center attached with Okanyan
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-006", p1.center))
    _, cheer_card_id = unpack_game_id(spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1"))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-013", center_card["attached_support"]))

    p2.backstage = p2.backstage[:1]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shaa",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 }) # do not archive Okanyan instead

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shaa", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": cheer_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertCountEqual(ids_from_cards(p1.archive), [cheer_card_id])


  def test_hsd03_013_only_one_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have center attached with Okanyan and one in hand
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    _, attached_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-013", center_card["attached_support"]))
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-013"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": attached_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertCountEqual(ids_from_cards(p1.archive), [attached_card_id])