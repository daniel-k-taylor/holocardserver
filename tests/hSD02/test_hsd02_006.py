import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_006(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-006": 1, # 1st bloom Ayame
      "hSD02-002": 1, # debut Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  # arts
  def test_hSD02_006_celebratetogether(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-006", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "celebratetogether",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "celebratetogether", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_006_bloom_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Ayame in the enter and 1st bloom Ayame in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-006"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    _, archived_card_id = unpack_game_id(p1.hand[0])
    
    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": ids_from_cards(p1.hand) })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [archived_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": archived_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 20, "special": True, "target_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])
  

  def test_hSD02_006_bloom_effect_choose_target(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have debut Ayame in the enter and 1st bloom Ayame in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-006"))

    # Setup to put a holomem in collab zone for player2
    p2_collab_card, p2_collab_card_id = unpack_game_id(p2.backstage[0])
    p2.collab.append(p2_collab_card)
    p2.backstage = p2.backstage[1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    _, archived_card_id = unpack_game_id(p1.hand[0])
    
    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": ids_from_cards(p1.hand) })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [archived_card_id] })
    # target the collab card instead of center
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_collab_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": archived_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p2.center + p2.collab) }),
      (EventType.EventType_DamageDealt, { "damage": 20, "special": True, "target_id": p2_collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_006_bloom_effect_pass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Ayame in the enter and 1st bloom Ayame in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-006"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_MainStep, {}) # Passed from using the effect
    ])


  def test_hSD02_006_bloom_effect_no_cards_in_hand(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Ayame in the enter and 1st bloom Ayame in hand with no other cards
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-002", p1.center))
    p1.hand = []
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD02-006"))

    self.assertCountEqual(ids_from_cards(p1.hand), [bloom_card_id])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_MainStep, {}) # no choice offered since no cards to archive
    ])


  def test_hSD02_005_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-006"), None)
    self.assertIsNotNone(card)

    # check tags and hp
    self.assertEqual(card["hp"], 140)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])