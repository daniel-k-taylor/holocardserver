import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_020(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  
  def setUp(self):
    p1_deck = generate_deck_with("", { "hBP01-015": 1 })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hSD01_020_failed_dice_roll_still_activates_mumei_damage_boost(self):
    # QnA: Q50 (2024.09.21)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have mumei in the center and holofan circle in hand
    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP01-015", p1.center)
    center_card_id = center_card["game_card_id"]
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    
    support_card = add_card_to_hand(self, p1, "hSD01-020")
    support_card_id = support_card["game_card_id"]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": support_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_RollDie, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}) # dice roll failed as expected
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "ohhi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    center_art = 10
    art_boost = 20

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": art_boost }), # art boost was still triggered
      (EventType.EventType_DamageDealt, { "damage": center_art + art_boost })
    ] + end_turn_events())