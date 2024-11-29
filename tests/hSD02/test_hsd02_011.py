import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_011(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-011": 2, # spot Mio
      "hSD02-012": 4, # support AyaFubuMi
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd02_011_themiinayafubumi(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Mio in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "themiinayafubumi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "themiinayafubumi", "power": 10 }),
      (EventType.EventType_DamageDealt, { "damage": 10 }),
      *end_turn_events()
    ])


  def test_hsd02_011_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Mio in the backstage
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.backstage))

    # Gather all debuts in the stage
    debut_cards = ids_from_cards((card for card in p1.get_holomem_on_stage() if card["card_type"] == "holomem_debut"))
    card_to_archive = p1.hand[0]["game_card_id"]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_archive] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_Decision_SendCheer, { "from_zone": "cheer_deck", "to_zone": "holomem", "to_options": debut_cards })
    ])

    cheer_card_id = p1.cheer_deck[0]["game_card_id"]
    debut_card_id = debut_cards[-1]
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, { 
      "placements": { cheer_card_id: debut_card_id }
     })
    
    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "cheer_deck", "to_holomem_id": debut_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd02_011_collab_no_cards_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Mio in the backstage
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.backstage))

    # Empty hand
    p1.hand = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_MainStep, {}) # no effect since no cards to archive
    ])


  def test_hsd02_011_collab_no_cards_in_cheer_deck(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Mio in the backstage
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.backstage))

    # Gather all debuts in the stage
    debut_cards = ids_from_cards((card for card in p1.get_holomem_on_stage() if card["card_type"] == "holomem_debut"))
    card_to_archive = p1.hand[0]["game_card_id"]

    # Empty cheer deck
    p1.cheer_deck = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_archive] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_Decision_MainStep, {}) # archived a card but no effect since no cheer to distribute
    ])


  def test_hsd02_011_collab_no_debut_cards(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Mio center and the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD02-011", p1.center)

    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.backstage))

    # Empty backstage except Mio
    p1.backstage = p1.backstage[-1:]
    self.assertCountEqual(ids_from_cards(p1.backstage), [collab_card_id])

    card_to_archive = p1.hand[0]["game_card_id"]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_archive] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, {}),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_Decision_MainStep, {}) # no effect since no targets
    ])    


  def test_hsd02_011_collab_only_holomem_can_be_archived(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have Mio in the backstage
    p1.backstage = []
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.backstage))
    _, center_card_id = unpack_game_id(p1.center[0])

    # Hand is all support cards except one
    p1.hand = p1.hand[:1]
    _, hand_card_id = unpack_game_id(p1.hand[0])
    add_card_to_hand(self, p1, "hSD02-012")
    add_card_to_hand(self, p1, "hSD02-012")
    add_card_to_hand(self, p1, "hSD02-012")
    add_card_to_hand(self, p1, "hSD02-012")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [hand_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [hand_card_id] }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": hand_card_id }),
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": "cheer_deck", "to_holomem_id": center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.archive), [hand_card_id])


  def test_hsd02_011_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Fubuki in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-011", p1.center))
    
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
    

  def test_hsd02_011_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-011"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 50)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars", "#Cooking"])