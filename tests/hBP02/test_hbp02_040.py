import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_040(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-040": 2, # 2nd Chloe
      "hBP02-076": 1, # support item
      "hBP02-035": 1, # debut Chloe
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_040_holoxslots(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Give p2 center high hp
    p2.center[0]["hp"] = 500


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2.center[0]["game_card_id"] }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }), # color advantage
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 3 }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": center_card_id }),
      (EventType.EventType_Decision_SendCheer, {}),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "life", "to_holomem_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 100 + 50 + 20 * 3 }),
      *end_turn_events()
    ])

    self.assertEqual(len(p1.archive), 3)
  

  def test_hbp02_040_holoxslots_not_same_holomem_bloom(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Put debut Chloe up front so that there are different bloom levels
    p1.deck = p1.deck[-1:] + p1.deck[:-1]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 3 }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 100 + 50 + 20 * 3 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_040_holoxslots_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }), # color advantage
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_DamageDealt, { "damage": 100 + 50 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_040_holoxslots_not_all_holomem(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Setup support item in top three
    p1.deck = p1.deck[-2:] + p1.deck[:-2]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }), # color advantage
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 2 }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 100 + 50 + 20 * 2 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_040_gift_only_triggers_own_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in the center and collab
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    p1.collab = []
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "blue", "b3")
    spawn_cheer_on_card(self, p1, collab_card_id, "blue", "b3")
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2") # any color

    # Give p2 center high hp
    p2.center[0]["hp"] = 999


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2.center[0]["game_card_id"] }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }), # color advantage
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 3 }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": center_card_id }),
      (EventType.EventType_Decision_SendCheer, {}),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "life", "to_holomem_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 100 + 50 + 20 * 3 }),
      (EventType.EventType_Decision_PerformanceStep, {})
    ])

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2.center[0]["game_card_id"] }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }), # color advantage
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 3 }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": collab_card_id }),
      (EventType.EventType_Decision_SendCheer, {}),

      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "life", "to_holomem_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 100 + 50 + 20 * 3 }),
      *end_turn_events()
    ])

    self.assertEqual(len(p1.archive), 6)
    self.assertEqual(len(p2.life), 3)
    
    
  def test_hbp02_040_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-040", p1.center))
  
  
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


  def test_hbp02_040_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-040"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 190)
    self.assertCountEqual(card["tags"], ["#JP", "#SecretSocietyholoX", "#Sea"])