import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_007(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-007": 1, # 1st bloom Okayu
      "hSD03-002": 3, # debut Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  # arts
  def test_hsd03_007_sendingmyownsongwithallmymight(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-007", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "sendingmyownsongwithallmymight",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "sendingmyownsongwithallmymight", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hsd03_007_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Okayu in the center and 1st Okayu in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-007"))

    # Add cheer to archive
    p1.archive = p1.cheer_deck[:1]
    p1.cheer_deck = p1.cheer_deck[1:]
    _, cheer_card_id = unpack_game_id(p1.archive[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": bloom_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd03_007_bloom_effect_multiple_gamers(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have debut Okayu in the center, collab and backstage and 1st Okayu in hand
    p1.center = []
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.collab))
    back_card, back_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.backstage))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-007"))
    
    # Add cheer to archive
    p1.archive = p1.cheer_deck[:1]
    p1.cheer_deck = p1.cheer_deck[1:]
    _, cheer_card_id = unpack_game_id(p1.archive[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { cheer_card_id: back_card_id }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_Decision_SendCheer, { "to_options": [bloom_card_id, collab_card_id, back_card_id] }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": back_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(back_card["attached_cheer"]), [cheer_card_id])


  def test_hsd03_007_bloom_effect_multiple_cheers(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have debut Okayu in the center and 1st Okayu in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    bloom_card, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-007"))

    # Add multiple cheers to archive (5 cheers, 5 non-cheers)
    cheer_cards = p1.cheer_deck[:5]
    _, cheer_card_id = unpack_game_id(cheer_cards[0])
    p1.archive = p1.deck[:5] + cheer_cards
    p1.cheer_deck = p1.cheer_deck[5:]
    p1.deck = p1.deck[:5]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { cheer_card_id: bloom_card_id }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_Decision_SendCheer, { "from_options": ids_from_cards(cheer_cards), "to_options": [bloom_card_id] }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "archive", "to_holomem_id": bloom_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(bloom_card["attached_cheer"]), [cheer_card_id])


  def test_hsd03_007_bloom_effect_no_cheers(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have debut Okayu in the center and 1st Okayu in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-007"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(len(p1.archive), 0)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, {}),
      (EventType.EventType_Decision_MainStep, {}) # no effect since no cheers to move
    ])


  def test_hsd03_007_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-007", p1.center))
  
  
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


  def test_hsd03_007_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-007"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 110)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])