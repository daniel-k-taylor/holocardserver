import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_091(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-091": 2, # support Mascot
      "hBP02-008": 1, # debut Fubuki
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hbp02_091_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup center attached with Mascot
    center_card, center_card_id = unpack_game_id(p1.center[0])
    center_hp = center_card["hp"]
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-091", center_card["attached_support"]))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])
    self.assertEqual(p1.get_card_hp(center_card), center_hp + 20)


  def test_hbp02_091_attached_effect_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the backstage attached with Mascot
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-091", collab_card["attached_support"]))

    # Put a mascot in the archive
    p1.archive = p1.deck[:5]
    p1.deck = p1.deck[5:]
    _, archive_card_id = unpack_game_id(add_card_to_archive(self, p1, "hBP02-091"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [archive_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [archive_card_id] }),

      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand", "card_id": archive_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_091_attached_effect_to_fubuki_do_not_choose(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki in the backstage attached with Mascot
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-091", collab_card["attached_support"]))

    # Put a mascot in the archive
    p1.archive = p1.deck[:5]
    p1.deck = p1.deck[5:]
    _, archive_card_id = unpack_game_id(add_card_to_archive(self, p1, "hBP02-091"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [archive_card_id] }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_091_attached_effect_to_fubuki_no_valid_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki in the backstage attached with Mascot
    p1.collab = []
    p1.backstage = p1.backstage[1:]
    collab_card, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-008", p1.backstage))
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-091", collab_card["attached_support"]))

    # No target in archive
    p1.archive = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_091_attached_effect_not_to_fubuki(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup holomem in the backstage attached with Mascot
    p1.collab = []
    collab_card, collab_card_id = unpack_game_id(p1.backstage[0])
    _, mascot_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-091", collab_card["attached_support"]))

    # Put a mascot in the archive
    p1.archive = p1.deck[:5]
    p1.deck = p1.deck[5:]
    _, archive_card_id = unpack_game_id(add_card_to_archive(self, p1, "hBP02-091"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(collab_card["attached_support"]), [mascot_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    