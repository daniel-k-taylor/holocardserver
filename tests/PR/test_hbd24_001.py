import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBD24_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hBD24-001") # BD Reine oshi
    initialize_game_to_third_turn(self, p1_deck)


  def test_hBD24_001_green_enhance(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have a green holomem in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD01-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")

    # Put another green mem in play to choose against.
    p1.backstage = p1.backstage[:1]
    put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    p1.generate_holopower(2)
    reset_mainstep(self)


    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "greenenhance" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "oshi_player_id": self.player1 }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {})
    ])

    self.assertIn(center_card_id, events[-2]["cards_can_choose"]) # center is a valid target for the effect

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "wherenextwherenext",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "power": 10 }),
      # damage boost from `greenenhance`
      (EventType.EventType_BoostStat, { "amount": 20, "source_card_id": p1.oshi_card["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hBD24_001_birthdaygiftgreen(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(2)
    reset_mainstep(self)

    greens_in_deck = list(card["game_card_id"] for card in p1.deck if "green" in card["colors"])
    prev_hand_count = len(p1.hand)
    prev_deck_count = len(p1.deck)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "birthdaygiftgreen" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "oshi_player_id": self.player1 }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": greens_in_deck })
    ])

    card_chosen = greens_in_deck[0]
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_chosen] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": card_chosen }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.hand), prev_hand_count + 1)
    self.assertEqual(len(p1.deck), prev_deck_count - 1)


  def test_hBD24_001_greenenhance_once_per_turn(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have player1 use `greenenhance`
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD01-009", p1.center))

    # Put another green mem in play to choose against.
    p1.backstage = p1.backstage[:1]
    put_card_in_play(self, p1, "hSD01-009", p1.backstage)

    p1.generate_holopower(6)
    reset_mainstep(self)
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "greenenhance" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    available_actions = engine.grab_events()[-2]["available_actions"]
    available_oshi_skills = list(action["skill_id"] for action in available_actions if action["action_type"] == GameAction.MainStepOshiSkill)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertNotIn("greenenhance", available_oshi_skills) # `greenenhance` is not in the available actions even with sufficient holopower

    # relay turns
    end_turn(self)
    self.assertEqual(engine.active_player_id, self.player2)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_cheer_step_on_card(self, p1.center[0])
    available_actions = events[-2]["available_actions"]
    available_oshi_skills = list(action["skill_id"] for action in available_actions if action["action_type"] == GameAction.MainStepOshiSkill)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertIn("greenenhance", available_oshi_skills) # `greenenhance` can be used again


  def test_hBD24_001_birthdaygiftgreen_once_per_game(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(4)
    reset_mainstep(self)

    greens_in_deck = list(card["game_card_id"] for card in p1.deck if "green" in card["colors"])
    card_chosen = greens_in_deck[0]

    # Use `birthdaygiftgreen`
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "birthdaygiftgreen" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_chosen] })


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    available_actions = engine.grab_events()[-2]["available_actions"]
    available_oshi_skills = list(action["skill_id"] for action in available_actions if action["action_type"] == GameAction.MainStepOshiSkill)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertNotIn("birthdaygiftgreen", available_oshi_skills) # `birthdaygiftgreen` is not in the available actions even with sufficient holopower

    # relay turns
    end_turn(self)
    self.assertEqual(engine.active_player_id, self.player2)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_cheer_step_on_card(self, p1.center[0])
    available_actions = events[-2]["available_actions"]
    available_oshi_skills = list(action["skill_id"] for action in available_actions if action["action_type"] == GameAction.MainStepOshiSkill)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertNotIn("birthdaygiftgreen", available_oshi_skills) # `birthdaygiftgreen` still cannot be used


  def test_hBD24_001_greenenhance_used_without_green_holomem_on_stage(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to remove all green holomem on the stage
    p1.backstage = []
    p1.collab = []
    center_card = p1.center[0]

    p1.generate_holopower(2)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    self.assertNotIn("green", center_card["colors"]) # not a green holomem

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "greenenhance" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "oshi_player_id": self.player1 }),
      (EventType.EventType_Decision_MainStep, {}) # No prompt to choose which holomem to boost
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": center_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "power": 30 }),
      # no damage boost from `greenenhance`
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])