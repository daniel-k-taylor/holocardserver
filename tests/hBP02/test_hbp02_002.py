import unittest
from app.gameengine import GameEngine, GameAction, is_card_holomem
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_002(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hBP02-002", {
      "hBP02-018": 2, # debut card
      "hBP02-023": 1, # collab card
      "hBP02-029": 1,
      "hBP01-053": 1, # lofi
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_002_oshi_skill_effect_halu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(2)
    
    # Setup a green holomem in the center, and set a not green holomem in the backstage
    p1.center = []
    p1.backstage = []
    p1.archive = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-018", p1.center))
    g1 = spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    r1 = spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    _, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-029", p1.backstage))
    g2 = spawn_cheer_on_card(self, p1, center_card_id, "green", "g2")
    b1 = spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")

    topcheer_id = p1.cheer_deck[0]["game_card_id"]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "halu" })
    # archive a cheer from green holomem
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [g1["game_card_id"]]
    })
    # reveal a cheer from cheer deck and attach it to the backstage holomem
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [topcheer_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [backstage_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_OshiSkillActivation, { "skill_id": "halu" }),
        (EventType.EventType_Decision_ChooseCards, {
            "from_zone": "holomem",
            "to_zone": "archive",
            "amount_min": 1,
            "amount_max": 1,
        }),
        (EventType.EventType_MoveCard, { 
            "moving_player_id": self.player1,
            "from_zone": center_card_id,
            "to_zone": "archive",
            "card_id": g1["game_card_id"],
        }),
        (EventType.EventType_Decision_ChooseCards, { 
            "from_zone": "cheer_deck",
            "to_zone": "holomem" }),
        (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
        (EventType.EventType_MoveCard, {
            "moving_player_id": self.player1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "zone_card_id": backstage_card_id,
            "card_id": topcheer_id,
        }),
        (EventType.EventType_Decision_MainStep, {})
    ])

  def test_hbp02_002_oshi_skill_effect_acolorfulfeast_is_idgen2(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    p1.generate_holopower(2)

    # Setup a IDGen2 holomem in the center, and set a not IDGen2 holomem in the backstage
    p1.center = []    
    p1.collab = []
    p1.backstage = []
    p1.archive = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-018", p1.center))
    g1 = spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    r1 = spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    r2 = spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    _, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-018", p1.backstage))
    g2 = spawn_cheer_on_card(self, p1, backstage_card_id, "green", "g2")
    b1 = spawn_cheer_on_card(self, p1, backstage_card_id, "blue", "b1")

    # give p2 center high hp
    p2.center[0]["hp"] = 300

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "acolorfulfeast" })

    # Oshi Skill Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_OshiSkillActivation, { "skill_id": "acolorfulfeast" }),
        (EventType.EventType_AddTurnEffect, { "effect_player_id": self.player1, }),
        (EventType.EventType_AddTurnEffect, { "effect_player_id": self.player1, }),
        (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "peruhatelian",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
    })

    # Perfromance Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_PerformArt, { "art_id": "peruhatelian", "power": 30 }),
        (EventType.EventType_BoostStat, { 
                "stat": "power",
                "amount": 40 }),
        (EventType.EventType_DamageDealt, { "damage": 70 }),
        *end_turn_events()
    ])

  def test_hbp02_002_oshi_skill_effect_acolorfulfeast_is_not_idgen2(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    p1.generate_holopower(2)

    # Setup a IDGen2 holomem in the center, and set a not IDGen2 holomem in the backstage
    p1.center = []    
    p1.collab = []
    p1.backstage = []
    p1.archive = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP01-053", p1.center))
    g1 = spawn_cheer_on_card(self, p1, center_card_id, "green", "g1")
    r1 = spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    r2 = spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    _, backstage_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-029", p1.backstage))
    g2 = spawn_cheer_on_card(self, p1, backstage_card_id, "green", "g2")
    b1 = spawn_cheer_on_card(self, p1, backstage_card_id, "blue", "b1")

    # give p2 center high hp
    p2.center[0]["hp"] = 300

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "acolorfulfeast" })

    # Oshi Skill Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
        (EventType.EventType_OshiSkillActivation, { "skill_id": "acolorfulfeast" }),
        (EventType.EventType_AddTurnEffect, { "effect_player_id": self.player1, }),
        (EventType.EventType_AddTurnEffect, { "effect_player_id": self.player1, }),
        (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
        "art_id": "yourbelovedalien",
        "performer_id": center_card_id,
        "target_id": p2.center[0]["game_card_id"]
    })

    # Perfromance Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
        (EventType.EventType_PerformArt, { "art_id": "yourbelovedalien", "power": 50 }),
        (EventType.EventType_DamageDealt, { "damage": 50 }),
        *end_turn_events()
    ])