import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_007(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-007": 2, # 1st bloom Ayame U
      "hSD02-002": 1, # debut Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_006_dontmisstheshiningme(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-007", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "dontmisstheshiningme",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "dontmisstheshiningme", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_007_bloom_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Ayame in center and 1st Ayame in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-007"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    cards_to_choose = ids_from_cards(p1.deck[:2])
    card_to_hand, card_to_archive = cards_to_choose

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cards_to_choose }) # bloom effect
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_hand] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": card_to_hand }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_007_bloom_effect_sidebloom(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have 1st Ayame in center and 1st Ayame in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-007", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-007"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_MainStep, {}) # no effect
    ])


  def test_hSD02_007_baton_pass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have 1st Ayame in center and 1st Ayame in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-007", p1.center))


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


  def test_hSD02_007_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-007"), None)
    self.assertIsNotNone(card)

    # check tags and hp
    self.assertEqual(card["hp"], 120)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])
