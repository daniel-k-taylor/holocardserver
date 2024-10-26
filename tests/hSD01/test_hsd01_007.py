import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

import json
def jsonimport(data):
  print(json.dumps(data, indent=4))


class Test_hSD01_007(unittest.TestCase):
  engine: GameEngine
  player1: str

  def setUp(self):
    initialize_game_to_third_turn(self)


  def test_hSD01_007_collab_effect_can_return_the_same_card(self):
    # QnA: Q6 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    p1.backstage = []
    collab_card = put_card_in_play(self, p1, "hSD01-007", p1.backstage)

    # Events
    events = do_collab_get_events(self, p1, collab_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, { "from_zone": "holopower" })
    ])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    moved_card_id = p1.holopower[0]["game_card_id"]

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [moved_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "hand" }),
      (EventType.EventType_Decision_ChooseCards, { "from_zone": "hand" })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [moved_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "holopower" }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.holopower), 1)
    self.assertAlmostEqual(p1.holopower[0]["game_card_id"], moved_card_id) # card returned to the same place