import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_004(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-010": 1, # spot Fubuki
      "hSD03-004": 2, # debut collab Okayu U
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_004_studentcat(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Okayu in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "studentcat",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "studentcat", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hsd03_004_collab_effect_top_deck_debut(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    # Move remaining okayu to top of deck
    # Move two since collab will move one to holopower
    p1.deck = p1.deck[-2:] + p1.deck[:-2]
    top_deck, top_deck_id = unpack_game_id(p1.deck[1])
    top_cheer_id = p1.cheer_deck[0]["game_card_id"]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(top_deck["card_type"], "holomem_debut")

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RevealCards, { "card_ids": [top_deck_id] }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "cheer_deck", "to_holomem_id": collab_card_id, "attached_id": top_cheer_id }),
      (EventType.EventType_Decision_OrderCards, {})
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": [top_deck_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck", "card_id": top_deck_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # cheer was attached and previous top deck is in the bottom
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [top_cheer_id])
    self.assertEqual(p1.deck[-1]["game_card_id"], top_deck_id)


  def test_hsd03_004_collab_effect_top_deck_spot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    # Move remaining okayu to top of deck
    # Move three since collab will move one to holopower and fubuki spot is 2nd to last
    p1.deck = p1.deck[-3:] + p1.deck[:-3]
    top_deck, top_deck_id = unpack_game_id(p1.deck[1])
    top_cheer_id = p1.cheer_deck[0]["game_card_id"]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(top_deck["card_type"], "holomem_spot")

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": [top_deck_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RevealCards, { "card_ids": [top_deck_id] }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "cheer_deck", "to_holomem_id": collab_card_id, "attached_id": top_cheer_id }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck", "card_id": top_deck_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # cheer was attached and previous top deck is in the bottom
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [top_cheer_id])
    self.assertEqual(p1.deck[-1]["game_card_id"], top_deck_id)


  def test_hsd03_004_collab_effect_top_deck_invalid(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    # Move remaining okayu to top of deck
    # Move five since collab will move one to holopower and a non-debut/spot is fifth from last
    p1.deck = p1.deck[-5:] + p1.deck[:-5]
    top_deck, top_deck_id = unpack_game_id(p1.deck[1])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertNotIn(top_deck["card_type"], ["holomem_spot", "holomem_debut"])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": [top_deck_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RevealCards, { "card_ids": [top_deck_id] }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck", "card_id": top_deck_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # no cheer was attached and previous top deck is in the bottom
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [])
    self.assertEqual(p1.deck[-1]["game_card_id"], top_deck_id)


  def test_hsd03_004_collab_effect_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_MainStep, {}) # effect was skipped
    ])

    # no cheer was attached
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [])


  def test_hsd03_004_collab_effect_no_cheer_left(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    # Move remaining okayu to top of deck
    # Move three since collab will move one to holopower and fubuki spot is 2nd to last
    p1.deck = p1.deck[-3:] + p1.deck[:-3]
    top_deck, top_deck_id = unpack_game_id(p1.deck[1])

    p1.cheer_deck = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(top_deck["card_type"], "holomem_spot")

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_OrderCards, { "card_ids": [top_deck_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RevealCards, { "card_ids": [top_deck_id] }),
      (EventType.EventType_Decision_OrderCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "deck", "card_id": top_deck_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # no cheer was attached and previous top deck is in the bottom
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [])
    self.assertEqual(p1.deck[-1]["game_card_id"], top_deck_id)


  def test_hsd03_004_collab_effect_no_card_in_deck_left(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # setup to have okayu in the backstage
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.backstage))

    # No remaining cards in the deck
    p1.deck = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # no cheer was attached
    self.assertCountEqual(ids_from_cards(collab_card["attached_cheer"]), [])
    self.assertEqual(len(p1.deck), 0)


  def test_hsd03_004_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-004", p1.center))
  
  
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


  def test_hsd03_004_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-004"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 80)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])