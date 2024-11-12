import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hSD02-001", { # oshi Ayame
      "hSD02-002": 3, # debut Ayame
    }) 
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_001_redmic(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")

    p1.generate_holopower(2)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = use_oshi_action(self, "redmic")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "redmic" }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

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
      (EventType.EventType_BoostStat, { "amount": 20, "source_card_id": p1.oshi_card["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])


  def test_hSD02_001_redmic_center_is_not_red(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    _, center_card_id = unpack_game_id(p1.center[0]) # debut Sora
    
    p1.generate_holopower(2)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = use_oshi_action(self, "redmic")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "redmic" }),
      (EventType.EventType_AddTurnEffect, {}),
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
      (EventType.EventType_DamageDealt, { "damage": 30 }), # no boost
      *end_turn_events()
    ])


  def test_hSD02_001_redmic_collab_is_red(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Ayame in the collab spot
    p1.collab = []
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1")
    
    p1.generate_holopower(2)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = use_oshi_action(self, "redmic")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "redmic" }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "konnakiri",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "konnakiri", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }), # no boost
      (EventType.EventType_Decision_PerformanceStep, {})
    ])


  def test_hSD02_001_redmic_collab_is_not_red(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Sora in the collab spot
    _, collab_card_id = unpack_game_id(p1.backstage[0])
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "r1")
    
    p1.generate_holopower(2)
    reset_mainstep(self)

    do_collab_get_events(self, p1, collab_card_id)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = use_oshi_action(self, "redmic")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "redmic" }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }), # no boost
      (EventType.EventType_Decision_PerformanceStep, {})
    ])


  def test_hSD02_001_redmic_collab_is_not_red(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player1 use redmic then pass turn
    p1.generate_holopower(4)
    reset_mainstep(self)

    # check that redmic is not part of the available actions after using redmic
    events = use_oshi_action(self, "redmic")
    actions = events[-2]["available_actions"]
    self.assertIsNone(next(
      (action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "redmic"),
      None))

    end_turn(self)

    # player2 passes turn
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # check that redmic is useable again
    events = do_cheer_step_on_card(self, p1.center[0])
    actions = events[-2]["available_actions"]
    self.assertIsNotNone(next(
      (action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "redmic"),
      None))


  def test_hSD02_002_comeonagain(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to put all debut Ayame and a non red card to archive
    add_card_to_archive(self, p1, "hSD02-002", False)
    add_card_to_archive(self, p1, "hSD02-002", False)
    add_card_to_archive(self, p1, "hSD02-002", False)
    add_card_to_archive(self, p1, "hSD01-009", False)

    self.assertEqual(len(p1.archive), 4)

    p1.generate_holopower(1)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    red_cards_in_archive = ids_from_cards(list(card for card in p1.archive if "red" in card["colors"]))
    self.assertEqual(len(red_cards_in_archive), 3)
    red_card_chosen = red_cards_in_archive[0]

    # Events
    events = use_oshi_action(self, "comeonagain")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "comeonagain" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": red_cards_in_archive })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [red_card_chosen] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand", "card_id": red_card_chosen }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertIn(red_card_chosen, ids_from_cards(p1.hand)) # chosen card moved to hand


  def test_hSD02_002_comeonagain_no_red_in_archive(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to put a non red card to archive
    p1.generate_holopower(1)
    add_card_to_archive(self, p1, "hSD01-009")

    self.assertEqual(len(p1.archive), 1)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "comeonagain" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "comeonagain" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }), # no cards to choose from
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_002_comeonagain_no_cards_in_archive(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    self.assertEqual(len(p1.archive), 0)

    p1.generate_holopower(1)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "comeonagain" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "comeonagain" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }), # no cards to choose from
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_002_comeonagain_once_per_game(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player1 use comeonagain and pass turn
    p1.generate_holopower(2)
    reset_mainstep(self)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "comeonagain" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    actions = events[-2]["available_actions"]
    self.assertIsNone(next(
      (action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "comeonagain"),
      None))

    end_turn(self)

    # player2 passes turn
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # check that comeonagain cannot be used even with enough holopower
    self.assertGreaterEqual(len(p1.holopower), 1)
    events = do_cheer_step_on_card(self, p1.center[0])
    actions = events[-2]["available_actions"]
    self.assertIsNone(next(
      (action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "comeonagain"),
      None))