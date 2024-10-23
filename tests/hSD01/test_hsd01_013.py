import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EffectType
from tests.helpers import *


class Test_hSD01_013(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", { "hBP01-124": 4, "hSD01-021": 1 })
    initialize_game_to_third_turn(self, p1_deck)


  # QnA: Q5 covered by hSD01-006
  # QnA: Q10 covered by hSD01-011

  def test_hSD01_013_brighterfuture_will_work_even_with_empty_deck(self):
    # QnA: Q11 (2024.09.21)
    
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have soraz in the center and have empty deck and cheer deck
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-013", p1.center)
    center_card_id = center_card["game_card_id"]

    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2")

    p1.deck = []
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, { 
      "art_id": "brighterfuture",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, {}),
      (EventType.EventType_Decision_Choice, {})
    ])

    # Override random chance
    self.random_override.random_values = [2]

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 2 }),
      (EventType.EventType_Draw, { "drawn_card_ids": [] }), # no cards drawn, game continues
      (EventType.EventType_DamageDealt, { "damage": 50 })
    ] + end_turn_events())


  def test_hSD01_013_brighterfuture_will_work_even_with_empty_cheer_deck(self):
    # QnA: Q11 (2024.09.21)
    
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have soraz in the center and have empty deck and cheer deck
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-013", p1.center)
    center_card_id = center_card["game_card_id"]

    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2")
    
    p1.cheer_deck = []

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, { 
      "art_id": "brighterfuture",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, {}),
      (EventType.EventType_Decision_Choice, {})
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, { "die_result": 1 }),
      # skipped the effect since cheer deck is empty
      (EventType.EventType_DamageDealt, { "damage": 50 }),
    ] + end_turn_events())
    

  
  def test_hSD01_013_BOTH_of_koyori_collab_effect_will_trigger_with_soraz(self):
    # QnA: Q13 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have koyori collaborate with soraz in the center
    p1.center = []
    put_card_in_play(self, p1, "hSD01-013", p1.center)

    p1.backstage.pop()
    collab_card = put_card_in_play(self, p1, "hSD01-015", p1.backstage)
    collab_card_id = collab_card["game_card_id"]

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Draw, {}), # koyori-sora effect
      (EventType.EventType_MoveAttachedCard, {}), # koyori-azki effect
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD01_013_first_gravity_can_be_used_to_on_soraz(self):
    # QnA: Q17 (2024.09.21)

    engine = self.engine
    
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have soraz on top of the deck, and first gravity in hand
    target_card = add_card_to_hand(self, p1, "hSD01-013")
    target_card_id = target_card["game_card_id"]
    p1.hand.pop()
    p1.deck.insert(0, target_card)

    support_card = add_card_to_hand(self, p1, "hSD01-021")
    support_card_id = support_card["game_card_id"]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseCards, { "from_zone": "deck", "to_zone": "hand" })
    ])
    # soraz can be chosen by first gravity
    self.assertTrue(target_card_id in events[-2]["cards_can_choose"])


  def test_hSD01_013_pioneer_fan_will_be_archived_when_soraz_blooms_into_sora(self):
    # QnA: Q116 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have soraz in center, equipped with pioneer, and a card to bloom into
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD01-013", p1.center)
    center_card_id = center_card["game_card_id"]

    fan_card = add_card_to_hand(self, p1, "hBP01-124")
    fan_card_id = fan_card["game_card_id"]

    bloom_card = add_card_to_hand(self, p1, "hSD01-006")
    bloom_card_id = bloom_card["game_card_id"]

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": fan_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {})
    ])
    
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem" }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(center_card["attached_support"]), 1)

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      # fan card is removed because card now no longer is a valid card
      (EventType.EventType_MoveCard, { "from_zone": bloom_card_id, "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])