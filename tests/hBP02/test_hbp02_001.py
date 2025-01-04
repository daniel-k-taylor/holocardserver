import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

def skill_is_available(action: dict, skill_id: str) -> bool:
  return action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == skill_id


class Test_hBP02_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def attach_mascots_to_holomem(self, player: PlayerState, holomems: list[dict], mascot_ids: list[str]):
    for mascot_id, holomem in zip(mascot_ids, holomems):
      put_card_in_play(self, player, mascot_id, holomem["attached_support"])
  
  def setUp(self):
    p1_deck = generate_deck_with("hBP02-001", { # Fubuki oshi
      "hBP02-061": 1, # debut Ina
      "hBP02-090": 2, # support Mascot
      "hBP02-089": 4, # support Mascot
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_001_oshi_skill(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(2)
    reset_mainstep(self)

    valid_target_ids = ids_from_cards(p1.deck[-6:])
    chosen_card_id = valid_target_ids[0]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "mascotcreation" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "mascotcreation" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": chosen_card_id }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_001_oshi_skill_no_mascots_in_deck(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(2)
    reset_mainstep(self)

    # remove valid targets in the deck
    p1.deck = p1.deck[:-6]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "mascotcreation" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "mascotcreation" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_001_oshi_skill_once_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(4)
    reset_mainstep(self)

    # remove valid targets in the deck
    p1.deck = p1.deck[:-6]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "mascotcreation" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    self.assertGreaterEqual(len(p1.holopower), 2)
    actions = reset_mainstep(self)
    self.assertFalse(any([skill_is_available(action, "mascotcreation") for action in actions]))

    # cycle through turns
    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    self.assertEqual(engine.active_player_id, self.player1)
    self.assertGreaterEqual(len(p1.holopower), 2)
    actions = reset_mainstep(self)
    self.assertTrue(any([skill_is_available(action, "mascotcreation") for action in actions]))


  def test_hbp02_001_sp_oshi_skill_two_mascots__1_die_roll(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # attach mascots to backstage
    self.attach_mascots_to_holomem(p1, p1.backstage, ["hBP02-089", "hBP02-089"])

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    set_next_die_rolls(self, [1])
    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "fubukingdom" }),
      (EventType.EventType_RollDie, {}),
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": p1.oshi_card["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_four_mascots__2_die_rolls(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # attach mascots to backstage
    self.attach_mascots_to_holomem(p1, p1.backstage, ["hBP02-089", "hBP02-089", "hBP02-089", "hBP02-089"])

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    set_next_die_rolls(self, [6, 3])
    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "fubukingdom" }),
      (EventType.EventType_RollDie, { "die_result": 6 }), # first one misses
      (EventType.EventType_RollDie, { "die_result": 3 }), # second is good
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": p1.oshi_card["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_six_mascots__3_die_rolls(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # attach mascots to backstage
    self.attach_mascots_to_holomem(p1, p1.center + p1.backstage, [
      "hBP02-089", "hBP02-089", "hBP02-089", "hBP02-089", "hBP02-090", "hBP02-090"
    ])

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    set_next_die_rolls(self, [6, 3, 5])
    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "fubukingdom" }),
      (EventType.EventType_RollDie, { "die_result": 6 }), # first one misses
      (EventType.EventType_RollDie, { "die_result": 3 }), # second is good
      (EventType.EventType_RollDie, { "die_result": 5 }), # third is good, too
      (EventType.EventType_LifeDamageDealt, { "life_lost": 1, "target_player": self.player2, "source_card_id": p1.oshi_card["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_1_mascot__0_die_roll(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # attach mascots to backstage
    self.attach_mascots_to_holomem(p1, p1.backstage, [ "hBP02-089" ])

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "fubukingdom" }),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_holomem_that_kills_not_white(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup Ina to attack
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-061", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "wah",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "wah", "power": 10 }),
      (EventType.EventType_DamageDealt, { "damage": 10 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_sp_oshi_skill_not_enough_holopower(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertLess(len(p1.holopower), 2)

    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_001_once_per_game(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(4)

    # attach mascots to backstage
    self.attach_mascots_to_holomem(p1, p1.backstage, [ "hBP02-089" ])

    # give p2 center low hp
    p2.center[0]["hp"] = 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self) 
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2.backstage[0]["game_card_id"] }
    })
    engine.handle_game_message(self.player2, GameAction.ChooseNewCenter, { "new_center_card_id": p2.backstage[0]["game_card_id"] })

    # cycle through turns
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    self.assertEqual(engine.active_player_id, self.player1)
    self.assertGreaterEqual(len(p1.holopower), 2)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])