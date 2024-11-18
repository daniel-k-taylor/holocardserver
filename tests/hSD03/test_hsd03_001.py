import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


def check_if_available(actions: list, action_type: str, skill_id: str) -> bool:
  return any(action["action_type"] == action_type and action["skill_id"] == skill_id for action in actions)


class Test_hSD03_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hSD03-001", { # oshi Okayu
      "hSD03-002": 1, # debut Okayu
      "hSD03-003": 2, # collab Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_001_bluemic(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup to have debut okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = use_oshi_action(self, "bluemic")

    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "mogumoguokayu",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "mogumoguokayu", "power": 30 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      *end_turn_events()
    ])


  def test_hsd03_001_bluemic_center_not_blue(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)
    reset_mainstep(self)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    use_oshi_action(self, "bluemic")

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


  def test_hsd03_001_bluemic_collab_is_blue(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup to have debut okayu in the center
    p1.collab = []
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1") # any color

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    use_oshi_action(self, "bluemic")

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "mogumoguokayu",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "mogumoguokayu", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_Decision_PerformanceStep, {})
    ])


  def test_hsd03_001_bluemic_opt(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(10)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertTrue(check_if_available(reset_mainstep(self), GameAction.MainStepOshiSkill, "bluemic"))

    use_oshi_action(self, "bluemic")
    
    # cannot use again for this turn
    self.assertFalse(check_if_available(reset_mainstep(self), GameAction.MainStepOshiSkill, "bluemic"))

    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    self.assertEqual(engine.active_player_id, self.player1)
    
    # can be used again
    self.assertTrue(check_if_available(reset_mainstep(self), GameAction.MainStepOshiSkill, "bluemic"))


  def test_hsd03_001_backshot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Okayu in the cente and collab Okayu in backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)

    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    _, chosen_card_id = unpack_game_id(p2.backstage[0])

    _, p2_center_card_id = unpack_game_id(p2.center[0])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2_center_card_id  }
    })


    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": chosen_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, {}),
      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": chosen_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "life_lost": 1 }),
      (EventType.EventType_Decision_SendCheer, {}),
      (EventType.EventType_MoveAttachedCard, {}),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  # oshi2 once per game
  def test_hsd03_001_backshot_opg(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup to have debut Okayu in the cente and collab Okayu in backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)

    p1.backstage = p1.backstage[:-2]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))
    _, collab_2_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    _, chosen_card_id = unpack_game_id(p2.backstage[0])
    _, chosen_2_card_id = unpack_game_id(p2.backstage[1])

    _, p2_center_card_id = unpack_game_id(p2.center[0])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { p2.life[0]["game_card_id"]: p2_center_card_id  }
    })
    
    # backshot used
    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    self.assertEqual(engine.active_player_id, self.player1)

    self.assertGreaterEqual(len(p1.holopower), 1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_2_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_2_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_2_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      # no trigger for backshot even if there is enough holopower to use it
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": chosen_2_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])