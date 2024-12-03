import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_003(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hBP02-003", {
      "hBP02-028": 1, # debut Marine
      "hBP02-030": 4, # 1st Marine
      "hBP02-033": 1, # 2nd Marine
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_003_oshi_skill(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(3)

    # Setup debut Marine in center and 1st and 2nd Marines in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-028", p1.center))
    _, bloom_first_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-030"))
    _, bloom_second_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_first_card_id, "target_id": center_card_id })
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "ahoy" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_second_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_first_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "ahoy" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [bloom_second_card_id] }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": [bloom_first_card_id] }),

      (EventType.EventType_Bloom, { "bloom_card_id": bloom_second_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.center[0]["stacked_cards"]), [center_card_id, bloom_first_card_id])


  def test_hbp02_003_oshi_skill_multiple_targets(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(3)

    # Setup 1st Marines in each locations and mark them as already bloomed this turn
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.collab))
    p1.backstage = p1.backstage[1:]
    back_card, back_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.backstage))
    for card in [center_card, collab_card, back_card]:
      card["bloomed_this_turn"] = True
    
    # 1st and 2nd Marine in hand
    _, bloom_first_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-030"))
    _, bloom_second_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "ahoy" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_first_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [collab_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "ahoy" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [bloom_first_card_id, bloom_second_card_id] }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": [center_card_id, collab_card_id, back_card_id] }),

      (EventType.EventType_Bloom, { "bloom_card_id": bloom_first_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p1.collab[0]["game_card_id"], bloom_first_card_id)
    self.assertCountEqual(ids_from_cards(p1.collab[0]["stacked_cards"]), [collab_card_id])


  def test_hbp02_003_oshi_skill_no_valid_bloom_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(3)

    # Setup 1st Marines in center and mark it as already bloomed this turn
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    center_card["bloomed_this_turn"] = True


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "ahoy" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "ahoy" }),

      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p1.center[0]["game_card_id"], center_card_id)
    self.assertEqual(len(center_card["stacked_cards"]), 0)


  def test_hbp02_003_oshi_skill_choose_to_not_bloom(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(3)

    # Setup 1st Marines in center and mark it as already bloomed this turn
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    center_card["bloomed_this_turn"] = True

    # 1st Marine in hand
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-030"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "ahoy" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "ahoy" }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [bloom_card_id] }),

      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p1.center[0]["game_card_id"], center_card_id)
    self.assertEqual(len(center_card["stacked_cards"]), 0)


  def test_hbp02_003_once_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    p1.generate_holopower(6)
    reset_mainstep(self)
    
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "ahoy" })

    """Test"""
    # Cannot use oshi skill after it was used even with sufficient holopower
    self.assertEqual(engine.active_player_id, self.player1)
    actions = reset_mainstep(self)
    self.assertGreaterEqual(len(p1.holopower), 3)
    self.assertFalse(any(action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "ahoy" for action in actions))

    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    # You can use the skill again
    self.assertEqual(engine.active_player_id, self.player1)
    actions = reset_mainstep(self)
    self.assertGreaterEqual(len(p1.holopower), 3)
    self.assertTrue(any(action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "ahoy" for action in actions))

  
  def test_hbp02_003_oshi_sp_skill(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup 1st Marine with stacked holomem under
    p1.center = []
    center_card, _ = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    center_card["stacked_cards"] = p1.backstage[:]
    p1.backstage = []

    # Setup collab for p2
    p2.collab = p2.backstage[:1]
    p2.backstage = p2.backstage[1:]
    _, p2_center_card_id = unpack_game_id(p2.center[0])
    _, p2_collab_card_id = unpack_game_id(p2.collab[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": [p2_center_card_id, p2_collab_card_id] }),

      (EventType.EventType_DamageDealt, { "damage": 50 * len(center_card["stacked_cards"]), "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_003_oshi_sp_skill_no_center(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup 1st Marine with stacked holomem under
    p1.center = []
    center_card, _ = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    center_card["stacked_cards"] = p1.backstage[:]
    p1.backstage = []

    # Setup collab for p2 and no center
    p2.collab = p2.backstage[:1]
    p2.backstage = p2.backstage[1:]
    _, p2_collab_card_id = unpack_game_id(p2.collab[0])
    p2.center = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),

      (EventType.EventType_DamageDealt, { "damage": 50 * len(center_card["stacked_cards"]), "special": True, "target_id": p2_collab_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  def test_hbp02_003_oshi_sp_skill_no_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup 1st Marine with stacked holomem under
    p1.center = []
    center_card, _ = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    center_card["stacked_cards"] = p1.backstage[:]
    p1.backstage = []
    
    _, p2_center_card_id = unpack_game_id(p2.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),

      (EventType.EventType_DamageDealt, { "damage": 50 * len(center_card["stacked_cards"]), "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  def test_hbp02_003_oshi_sp_skill_no_stacks(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)

    # Setup debut Marine in center without stacks
    p1.center = []
    put_card_in_play(self, p1, "hBP02-028", p1.center)
    
    _, p2_center_card_id = unpack_game_id(p2.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),

      (EventType.EventType_DamageDealt, { "damage": 0, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_003_oshi_sp_skill_center_not_marine(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(2)
    reset_mainstep(self)
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_003_oshi_sp_skill_marine_in_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(2)
    reset_mainstep(self)
    
    # Setup debut Marine in collab without stacks
    p1.collab = []
    put_card_in_play(self, p1, "hBP02-028", p1.collab)
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "shukkou" }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_003_oshi_sp_skill_once_per_game(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    p1.generate_holopower(4)
    reset_mainstep(self)
    
    # Setup debut Marine in collab without stacks
    p1.collab = []
    put_card_in_play(self, p1, "hBP02-028", p1.collab)
    
    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "shukkou" })

    """Test"""
    # Cannot use sp oshi skill after it was used even with sufficient holopower
    self.assertEqual(engine.active_player_id, self.player1)
    actions = reset_mainstep(self)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertFalse(any(action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "shukkou" for action in actions))

    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])

    # Cannot use even after cycling turns
    self.assertEqual(engine.active_player_id, self.player1)
    actions = reset_mainstep(self)
    self.assertGreaterEqual(len(p1.holopower), 2)
    self.assertFalse(any(action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "shukkou" for action in actions))


