import unittest
from app.gameengine import GameEngine, GameAction, is_card_holomem
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_039(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-039": 2, # 1st Chloe
      "hBP02-076": 3, # support card
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_039_holoxslots(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Add a Support card in the top three
    p1.deck = p1.deck[-1:] + p1.deck[:-1]
    support_card, support_card_id = unpack_game_id(p1.deck[0])
    self.assertEqual(support_card["card_type"], "support")

    # top three
    len_holomem_in_top_three = len([card for card in p1.deck[:3] if is_card_holomem(card)])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [support_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),
      
      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * len_holomem_in_top_three }),
      (EventType.EventType_Decision_ChooseCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": support_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 20 + 20 * len_holomem_in_top_three }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertEqual(len(p1.archive), 2)
    
  
  def test_hbp02_039_holoxslots_pass_reveal(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hbp02_039_holoxslots_no_holomem_revealed(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Add a Support card in the top three
    p1.deck = p1.deck[-3:] + p1.deck[:-3]
    _, support_card_id = unpack_game_id(p1.deck[0])
    self.assertTrue(any(card["card_type"] == "support" for card in p1.deck[:3]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [support_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_Decision_ChooseCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": support_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hbp02_039_holoxslots_pass_from_moving_support_to_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Add a Support card in the top three
    p1.deck = p1.deck[-1:] + p1.deck[:-1]
    support_card, _ = unpack_game_id(p1.deck[0])
    self.assertEqual(support_card["card_type"], "support")

    # top three
    len_holomem_in_top_three = len([card for card in p1.deck[:3] if is_card_holomem(card)])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),
      
      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * len_holomem_in_top_three }),
      (EventType.EventType_Decision_ChooseCards, {}),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 20 + 20 * len_holomem_in_top_three }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertEqual(len(p1.archive), 3)


  def test_hbp02_039_gift_once_per_turn_per_card(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Chloe in center and collab
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    p1.collab = []
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.collab))
    spawn_cheer_on_card(self, p1, collab_card_id, "blue", "b2")
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w2") # any color

    # Add a support card per three cards on top of the deck
    support_cards = p1.deck[-2:]
    support_1_card_id, support_2_card_id = ids_from_cards(support_cards)
    p1.deck = (support_cards[:1] + p1.deck[:2]) + (support_cards[1:] + p1.deck[2:4]) + p1.deck[4:-2]
    self.assertCountEqual([is_card_holomem(card) for card in p1.deck[:3]], [False, True, True])
    self.assertCountEqual([is_card_holomem(card) for card in p1.deck[3:6]], [False, True, True])

    # Make p2's center have a high HP
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [support_1_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 2 }),
      (EventType.EventType_Decision_ChooseCards, {}),
      
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": support_1_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 20 + 20 * 2 }),
      (EventType.EventType_Decision_PerformanceStep, {})
    ])

    # collab card
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "holoxslots",
      "performer_id": collab_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [support_2_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "holoxslots", "power": 20 }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_RevealCards, {}),
      (EventType.EventType_BoostStat, { "amount": 20 * 2 }),
      (EventType.EventType_Decision_ChooseCards, {}),
      
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": support_2_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive" }),
      (EventType.EventType_DamageDealt, { "damage": 20 + 20 * 2 }),
      *end_turn_events()
    ])
    
    
  def test_hbp02_039_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-039", p1.center))
  
  
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


  def test_hbp02_039_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-039"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 130)
    self.assertCountEqual(card["tags"], ["#JP", "#SecretSocietyholoX", "#Sea"])