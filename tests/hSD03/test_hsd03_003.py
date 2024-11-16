import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_003(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-003": 2, # debut collab Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_003_pleaseletmeintoyourhouse(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "pleaseletmeintoyourhouse",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "pleaseletmeintoyourhouse", "power": 10 }),
      (EventType.EventType_DamageDealt, { "damage": 10 }),
      *end_turn_events()
    ])

    
  def test_hsd03_003_collab_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p2.backstage) }),
    ])

    # choose player2's backstage holomem to do damage
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_back_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p2_center_card["damage"], 10)
    self.assertEqual(p2_back_card["damage"], 10)


  def test_hsd03_003_collab_effect_center_not_gamers(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Okayu in the backstage
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_MainStep, {}) # no collab effect
    ])


  def test_hsd03_003_collab_effect_no_center(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Remove player2's center
    p2.center = []
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_back_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p2.backstage) }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p2_back_card["damage"], 10)

    
  def test_hsd03_003_collab_effect_no_back_member(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Remove player2's backstage
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p2_center_card["damage"], 10)


  def test_hsd03_003_collab_effect_center_no_life_lost(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup player2
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_center_card["damage"] = p2_center_card["hp"] - 10
    _, p2_back_card_id = unpack_game_id(p2.backstage[0])
    p2_life = len(p2.life)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_back_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p2.backstage) }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": p2_center_card_id, "life_lost": 0, "life_loss_prevented": True }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(p2.life), p2_life)


  def test_hsd03_003_collab_effect_back_no_life_lost(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup player2
    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])
    p2_back_card["damage"] = p2_back_card["hp"] - 10
    p2_life = len(p2.life)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_back_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": p2_back_card_id, "life_lost": 0, "life_loss_prevented": True }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(len(p2.life), p2_life)


  def test_hsd03_003_collab_effect_only_one_backstage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-003", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.backstage))

    # Setup player2
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_back_card, p2_back_card_id = unpack_game_id(p2.backstage[0])
    p2.backstage = p2.backstage[:1]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_back_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(p2_center_card["damage"], 10)
    self.assertEqual(p2_back_card["damage"], 10)


  def test_hsd03_003_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-003", p1.center))
  
  
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
  


  def test_hsd03_003_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-003"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 70)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])