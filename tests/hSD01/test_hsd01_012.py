import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_012(unittest.TestCase):
  engine: GameEngine
  player1: str


  def setUp(self):
    initialize_game_to_third_turn(self)


  def test_hSD01_012_collab_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to put hSD01-012 on backstage to collab
    p1.backstage = p1.backstage[1:]
    collab_card = put_card_in_play(self, p1, "hSD01-012", p1.backstage)
    collab_card_id = collab_card["game_card_id"]

    # Spawn a green cheer to any holomem, then archive all
    spawn_cheer_on_card(self, p1, collab_card_id, "green", "g1")
    spawn_cheer_on_card(self, p1, collab_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, collab_card_id, "blue", "b1")
    spawn_cheer_on_card(self, p1, collab_card_id, "white", "w1")
    p1.archive_attached_cards(p1.get_cheer_ids_on_holomems())

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      # two existing white cheer + 4 of each color
      (EventType.EventType_MoveAttachedCard, { "to_holomem_id": "archive" }) for i in range(6)
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      # decision to send cheer is triggered
      (EventType.EventType_Decision_SendCheer, { "from_zone": "archive", "to_zone": "holomem" })
    ])

    # 2 existing white cards + 1 white and 1 green, proving the color restriction of the effect works
    self.assertEqual(len(events[-2]["from_options"]), 4)


  def test_hSD01_012_collab_effect_fizzles_out_when_no_target_in_archive(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to put hSD01-012 on backstage to collab
    p1.backstage = p1.backstage[1:]
    collab_card = put_card_in_play(self, p1, "hSD01-012", p1.backstage)
    collab_card_id = collab_card["game_card_id"]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_MainStep, {}) # skip straight back to main step
    ])