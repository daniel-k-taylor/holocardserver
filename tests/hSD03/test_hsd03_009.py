import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_009(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-009": 1, # 2nd Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_009_mogmog(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    # Green holomem in player2's center
    p2.center = []
    _, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.center))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "mogmog",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "mogmog", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      *end_turn_events()
    ])


  def test_hsd03_009_mogmog_bonus(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")

    # Center is white

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "mogmog",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "mogmog", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 110 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hsd03_009_okayu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    # Green holomem in player2's center
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.center))

    back_chosen, back_chosen_id = unpack_game_id(p2.backstage[0])
    backstage_ids = ids_from_cards(p2.backstage)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [back_chosen_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": backstage_ids }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": back_chosen_id }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 100, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])

    self.assertEqual(p2_center_card["damage"], 130)
    self.assertEqual(back_chosen["damage"], 30)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 2) # 2 blue cheers
    

  def test_hsd03_009_okayu_no_center(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    # Green holomem in player2's collab and no center
    p2.center = []
    p2.collab = []
    p2_collab_card, p2_collab_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.collab))

    back_chosen, back_chosen_id = unpack_game_id(p2.backstage[0])
    backstage_ids = ids_from_cards(p2.backstage)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_collab_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [back_chosen_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": backstage_ids }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": back_chosen_id }),
      (EventType.EventType_DamageDealt, { "damage": 100, "special": False, "target_id": p2_collab_card_id }),
      *end_turn_events(new_center=True)
    ])

    self.assertEqual(p2_collab_card["damage"], 100)
    self.assertEqual(back_chosen["damage"], 30)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 2) # 2 blue cheers


  def test_hsd03_009_okayu_no_backstage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    # Green holomem in player2's center and no backstage
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.center))

    p2.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 100, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])

    self.assertEqual(p2_center_card["damage"], 130)
    self.assertEqual(len(p2.backstage), 0)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 2) # 2 blue cheers


  def test_hsd03_009_okayu_only_one_backstage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    # Green holomem in player2's center and only one backstage
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.center))

    back_chosen, back_chosen_id = unpack_game_id(p2.backstage[0])
    p2.backstage = p2.backstage[:1]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": back_chosen_id }),
      (EventType.EventType_DamageDealt, { "damage": 30, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 100, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])

    self.assertEqual(p2_center_card["damage"], 130)
    self.assertEqual(back_chosen["damage"], 30)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 2) # 2 blue cheers


  def test_hsd03_009_okayu_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    # Green holomem in player2's center
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD01-010", p2.center))

    back_chosen, _ = unpack_game_id(p2.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_DamageDealt, { "damage": 100, "special": False, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])

    self.assertEqual(p2_center_card["damage"], 100)
    self.assertEqual(back_chosen["damage"], 0)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 0) # 0 blue cheers


  def test_hsd03_009_okayu_bonus(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color

    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    back_chosen, _ = unpack_game_id(p2.backstage[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "okayu",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "okayu", "power": 100 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_DamageDealt, { "damage": 150, "special": False, "target_id": p2_center_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertEqual(p2_center_card["damage"], 150)
    self.assertEqual(back_chosen["damage"], 0)
    self.assertEqual(len([card for card in p1.archive if card["card_type"] == "cheer" and "blue" in card["colors"]]), 0) # 0 blue cheers
    

  def test_hsd03_009_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-009", p1.center))
  
  
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


  def test_hsd03_009_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-009"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 190)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])