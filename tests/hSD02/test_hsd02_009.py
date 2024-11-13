import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_009(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-009": 1, #2nd Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  # arts1
  def test_hsd02_009_theayainayafubumi(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "theayainayafubumi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "theayainayafubumi", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  # arts2 max
  def test_hsd02_009_yodayo_max_choose_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    cards_in_hand = ids_from_cards(p1.hand)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "yodayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": len(cards_in_hand) - 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "yodayo", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cards_in_hand })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": cards_in_hand })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 40 * 3, "special": True }),
      (EventType.EventType_DownedHolomem_Before, {}), # downed immediately because the previous damage alone exceeeded the opp. hp
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  # arts2 just one
  def test_hsd02_009_yodayo_max_choose_one(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    cards_in_hand = ids_from_cards(p1.hand)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "yodayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "yodayo", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cards_in_hand })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [cards_in_hand[0]] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 40, "special": True }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  # arts2 more than 3 in hand
  def test_hsd02_009_yodayo_max_choose_one_with_more_than_3_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Setup to add 3 more cards to hand
    p1.hand += p1.deck[:3]
    p1.deck = p1.deck[3:]
    self.assertEqual(len(p1.hand), 6)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    cards_in_hand = ids_from_cards(p1.hand)
    cards_to_archive = ids_from_cards(p1.hand[:3])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "yodayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": len(cards_to_archive) - 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "yodayo", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cards_in_hand })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": cards_to_archive })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 40 * 3, "special": True }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.archive), cards_to_archive)
    self.assertEqual(len(p1.hand), 3)


  # arts2 no cards in hand
  def test_hsd02_009_yodayo_no_cards_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Setup to have no cards in hand
    p1.hand = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "yodayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "yodayo", "power": 40 }),
      (EventType.EventType_DamageDealt, { "damage": 40 }), # no effect triggered since nothing to discard
      *end_turn_events()
    ])


  # arts2 pass
  def test_hsd02_009_yodayo_no_cards_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "yodayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 3 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "yodayo", "power": 40 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  # baton pass
  def test_hsd02_009_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    # Setup to have Ayame in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-009", p1.center))

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


  def test_hsd02_009_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-009"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 180)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])