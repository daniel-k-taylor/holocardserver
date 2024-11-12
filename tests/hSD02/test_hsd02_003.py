import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


# overall


class Test_hSD02_003(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-003": 1, # debut collab Ayame
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD02_003_shiranui(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-003", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # art uses any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "shiranui",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "shiranui", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD02_003_collab(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-003", p1.backstage))

    # Setup to have player2 have a holomem in the collab zone
    p2_collab_card, p2_collab_card_id = unpack_game_id(p2.backstage[0])
    p2.collab.append(p2_collab_card)
    p2.backstage = p2.backstage[1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 10, "special": True, "target_id": p2_collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
  

  def test_hSD02_003_collab_no_target(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Ayame in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-003", p1.backstage))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }), # nothing happens
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD02_003_overall_check(self):
    # check for hp and tags
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-003"), None)
    self.assertIsNotNone(card)

    card["hp"] = 70
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])