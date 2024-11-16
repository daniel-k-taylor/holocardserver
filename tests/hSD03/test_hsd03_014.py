import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_014(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-014": 2, # fan Onigirya
      "hSD03-002": 1, # debut Okayu
    })
    initialize_game_to_third_turn(self, p1_deck)


  # bonus hp
  def test_hsd03_014_bonus_hp(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have Okayu in the center attached with Onigirya
    p1.center = []
    center_card = put_card_in_play(self, p1, "hSD03-002", p1.center)
    put_card_in_play(self, p1, "hSD03-014", center_card["attached_support"])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertEqual(p1.get_card_hp(center_card), center_card["hp"] + 10)


  def test_hsd03_014_only_equippable_to_okayu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have Onigirya in hand
    _, fan_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-014"))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Actions
    actions = reset_mainstep(self)
    self.assertIsNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == fan_card_id), None)
    )

    # put okayu to center
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)

    actions = reset_mainstep(self)
    self.assertIsNotNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == fan_card_id), None)
    )


  def test_hsd03_014_multiple_attachment(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup put Okayu in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-002", p1.center))

    # Attach one Onigirya and add another to hand
    _, attached_fan_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-014", center_card["attached_support"]))
    _, fan_card_id = unpack_game_id(add_card_to_hand(self, p1, "hSD03-014"))

    
    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [attached_fan_card_id])

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": fan_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, {}),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": [center_card_id] }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": fan_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [attached_fan_card_id, fan_card_id])