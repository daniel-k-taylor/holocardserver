import unittest
from app.gameengine import GameEngine, GameAction, is_card_holomem
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_004(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("hBP02-004", {
      "hBP02-035": 1, # debut Chloe
      "hBP02-096": 1, # support card
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_004_oshi_skill_effect_archive_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(1)
    
    # Setup Chloe in the center
    p1.center = []
    put_card_in_play(self, p1, "hBP02-035", p1.center)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "poepoepoe" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "poepoepoe" }),
      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(p1.archive), 1 + 3)


  def test_hbp02_004_oshi_skill_effect_order_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(1)

    # Setup Chloe in the center
    p1.center = []
    put_card_in_play(self, p1, "hBP02-035", p1.center)

    # top three cards
    top_three_ids = ids_from_cards(p1.deck[:3])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "poepoepoe" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": top_three_ids })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "poepoepoe" }),
      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_OrderCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(ids_from_cards(p1.deck[:3]), top_three_ids)


  def test_hbp02_004_oshi_skill_cannot_activate_if_center_is_not_chloe(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    p1.generate_holopower(1)

    center_card = p1.center[0]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertNotIn("sakamata_chloe", center_card["card_names"])

    actions = reset_mainstep(self)
    self.assertFalse(any([action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "poepoepoe"]))
  

  def test_hbp02_004_oshi_skill_once_per_turn(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(2)
    
    # Setup Chloe in the center
    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP02-035", p1.center)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertGreaterEqual(len(p1.holopower), 1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "poepoepoe" })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    actions = engine.grab_events()[-2]["available_actions"]
    self.assertFalse(any([action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "poepoepoe" for action in actions]))

    # cycle through turns
    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, center_card)
    actions = reset_mainstep(self)

    self.assertEqual(engine.active_player_id, self.player1)
    self.assertGreaterEqual(len(p1.holopower), 1)
    self.assertTrue(any([action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "poepoepoe" for action in actions]))


  def test_hbp02_004_oshi_sp_skill_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    p1.generate_holopower(3)
    reset_mainstep(self)

    # Setup Archive to have cards
    p1.archive = p1.deck[:5] + p1.deck[-1:] # put a support card in the archive
    p1.deck = p1.deck[5:-1]

    hand_count = len(p1.hand)
    archive_count = len(p1.archive) + 3
    archive_holomem_count = len([card for card in (p1.archive + p1.holopower[:3]) if is_card_holomem(card)])
    deck_count = len(p1.deck)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "liferesetbutton" })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "liferesetbutton" }),
      *[(EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "deck" }) for _ in range(hand_count)],
      (EventType.EventType_ShuffleDeck, {}),
      *[(EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "deck" }) for _ in range(archive_holomem_count)],
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Draw, { "hand_count": hand_count, "deck_count": deck_count + archive_holomem_count }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(p1.hand), hand_count)
    self.assertEqual(len(p1.archive), archive_count - archive_holomem_count)
    self.assertEqual(len(p1.deck), deck_count + archive_holomem_count)
  

  def test_hbp02_004_oshi_sp_skill_once_per_game(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(6)
    reset_mainstep(self)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertGreaterEqual(len(p1.holopower), 3)

    engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, { "skill_id": "liferesetbutton" })

    actions = engine.grab_events()[-2]["available_actions"]
    self.assertFalse(any([action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "liferesetbutton" for action in actions]))

    # cycle through turns
    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])
    actions = reset_mainstep(self)

    self.assertEqual(engine.active_player_id, self.player1)
    self.assertGreaterEqual(len(p1.holopower), 3)
    self.assertFalse(any([action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == "liferesetbutton" for action in actions]))
