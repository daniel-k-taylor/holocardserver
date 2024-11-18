import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_010(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-010": 1, # spot Fubuki
      "hSD02-014": 1, # Poyoyo
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd02_010_thefubuinayafubumi(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Fubuki in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-010", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "thefubuinayafubumi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "thefubuinayafubumi", "power": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 20 }),
      *end_turn_events()
    ])


  def test_hsd02_010_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have Fubuki in backstage and Poyoyo in archive
    p1.collab = []
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-010", p1.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-014", p1.archive))

    self.assertCountEqual(ids_from_cards(p1.archive), [mascot_card_id])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": ids_from_cards(p1.archive) })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [mascot_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand", "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  #collab no mascot
  def test_hsd02_010_collab_no_mascot_in_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Fubuki in backstage
    p1.collab = []
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-010", p1.backstage))

    self.assertEqual(len(p1.archive), 0)

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  #batonpass
  def test_hsd02_010_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Fubuki in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-010", p1.center))
    
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


  def test_hsd02_010_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-010"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 80)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen1", "#Gamers", "#AnimalEars", "#Art"])