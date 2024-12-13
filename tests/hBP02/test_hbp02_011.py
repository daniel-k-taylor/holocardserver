import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_011(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-011": 1, # 1st Fubuki
      "hBP02-008": 1, # debut Fubuki
      "hBP02-089": 1, # #ShirakamiCharaceter cards
      "hBP02-090": 1, # #ShirakamiCharaceter cards
      "hBP02-091": 1, # #ShirakamiCharaceter cards
      "hBP02-092": 1, # #ShirakamiCharaceter cards
      "hBP02-093": 1, # #ShirakamiCharaceter cards
      "hBP02-099": 1, # #ShirakamiCharaceter cards
      "hSD02-014": 1, # #ShirakamiCharaceter cards
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_011_damedesuyo(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-011", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "damedesuyo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "damedesuyo", "power": 40 }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hbp02_011_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup for 1st Fubuki to bloom
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-011"))

    # #ShirakamiCharacters IDs
    sc_card_ids = ids_from_cards(p1.deck[-7:])
    chosen_card_id = sc_card_ids[0]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": sc_card_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": chosen_card_id }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_011_bloom_effect_no_valid_targets(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup for 1st Fubuki to bloom
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-011"))

    # Remove #ShirakamiCharacters from the deck
    p1.deck = p1.deck[:-7]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_011_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-011", p1.center))
  
  
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


  def test_hbp02_011_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-011"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 120)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen1", "#Gamers", "#AnimalEars", "#Art"])