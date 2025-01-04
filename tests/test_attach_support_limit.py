import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_Attach_Support_Limit(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP01-116": 4, # support Mascot
      "hBP01-012": 1, # 1st Kanata
      "hBP01-009": 1, # debut Kanata
    })
    initialize_game_to_third_turn(self, p1_deck)
  
  
  def test_attach_support_limit_attach_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Add Mascot to hand
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP01-116"))

    center_card, center_card_id = unpack_game_id(p1.center[0])
    valid_target_ids = ids_from_cards(p1.get_holomem_on_stage())


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    self.assertTrue(any([action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == mascot_card_id for action in actions]))
    self.assertFalse(any([card.get("sub_type") == "mascot" for card in center_card["attached_support"]]))

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])


  def test_attach_support_limit_holomem_on_stage_all_are_attached_with_mascots(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup holomem to be attached with mascots
    center_card = p1.center[0]
    put_card_in_play(self, p1, "hBP01-116", center_card["attached_support"])
    back_card = p1.backstage[0]
    put_card_in_play(self, p1, "hBP01-116", back_card["attached_support"])
    p1.backstage = p1.backstage[:1]

    # Add Mascot to hand
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP01-116"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    self.assertFalse(any([action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == mascot_card_id for action in actions]))


  def test_attach_support_limit_holomem_attached_with_mascot_is_excluded_from_choices(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup holomem in backstage attached with mascot
    back_card = p1.backstage[0]
    put_card_in_play(self, p1, "hBP01-116", back_card["attached_support"])

    # Add Mascot to hand
    _, mascot_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP01-116"))

    center_card, center_card_id = unpack_game_id(p1.center[0])
    valid_target_ids = ids_from_cards(p1.center + p1.backstage[1:])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    self.assertTrue(any([action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == mascot_card_id for action in actions]))

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": mascot_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": mascot_card_id }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "holomem", "zone_card_id": center_card_id, "card_id": mascot_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [mascot_card_id])


  def test_attach_support_limit_attach_mascot_via_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Kanata to bloom
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP01-009", p1.center))
    bloom_card, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP01-012"))

    valid_target_ids = ids_from_cards(p1.deck[-4:])
    chosen_card_id = valid_target_ids[0]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    set_next_die_rolls(self, [3])
    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [bloom_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RollDie, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "holomem", "zone_card_id": bloom_card_id, "card_id": chosen_card_id }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertCountEqual(ids_from_cards(bloom_card["attached_support"]), [chosen_card_id])


  def test_attach_support_limit_attach_mascot_via_effect_but_all_has_mascot(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Kanata to bloom
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP01-009", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP01-012"))

    # Setup stage to have all holomem have mascots attached
    put_card_in_play(self, p1, "hBP01-116", center_card["attached_support"])
    put_card_in_play(self, p1, "hBP01-116", p1.backstage[0]["attached_support"])
    p1.backstage = p1.backstage[:1]

    valid_target_ids = ids_from_cards(p1.deck[-2:])
    chosen_card_id = valid_target_ids[0]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    set_next_die_rolls(self, [3])
    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_RollDie, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": valid_target_ids }),

      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])    
