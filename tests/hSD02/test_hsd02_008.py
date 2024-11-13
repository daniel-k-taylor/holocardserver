import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD02_008(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD02-008": 1, #1st buzz ayame
    })
    p2_deck = generate_deck_with("", {
      "hSD02-008": 1, #1st buzz ayame
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hsd02_008_fancybirthday(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "fancybirthday",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "fancybirthday", "power": 40 }),
      (EventType.EventType_DamageDealt, { "damage": 40 }),
      *end_turn_events()
    ])


  def test_hsd02_008_whatsinthepresent(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    _, p2_center_card_id = unpack_game_id(p2.center[0])
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    cards_in_hand = ids_from_cards(p1.hand)
    card_to_archive = cards_in_hand[0]

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "whatsinthepresent",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "whatsinthepresent", "power": 50 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cards_in_hand })
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_archive] })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 50, "target_id": p2_center_card_id }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertCountEqual(ids_from_cards(p1.archive), [card_to_archive])


  def test_hsd02_008_whatsinthepresent_choose_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Setup to have player2 have a holomem in the collab spot
    p2_center_card, p2_center_card_id = unpack_game_id(p2.center[0])
    p2_collab_card, p2_collab_card_id = unpack_game_id(p2.backstage[0])
    p2.collab.append(p2_collab_card)
    p2.backstage = p2.backstage[1:]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    _, card_to_archive = unpack_game_id(p1.hand[0])
    effect_targets = ids_from_cards(p2.center + p2.collab)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "whatsinthepresent",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    events = engine.grab_events()

    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_to_archive] })
    # target the collab holomem instead of the center
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_collab_card_id] })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive", "card_id": card_to_archive }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": effect_targets }),
      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2_collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 50, "target_id": p2_center_card_id }),
      *end_turn_events()
    ])

    self.assertCountEqual(ids_from_cards(p1.archive), [card_to_archive])
    self.assertEqual(p2_center_card["damage"], 50)
    self.assertEqual(p2_collab_card["damage"], 50)


  def test_hsd02_008_whatsinthepresent_pass_on_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "whatsinthepresent",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })
    
    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "whatsinthepresent", "power": 50 }),
      (EventType.EventType_Decision_Choice, {}),
      (EventType.EventType_DamageDealt, { "damage": 50 }), # no effect
      *end_turn_events()
    ])


  def test_hsd02_008_whatsinthepresent_effect_but_no_card_in_hand(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Ayame in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r2")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # remove all cards in hand
    p1.hand = []

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "whatsinthepresent",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "whatsinthepresent", "power": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }), # no choice offered since no card in hand
      *end_turn_events()
    ])


  def test_hsd02_008_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Ayame in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD02-008", p1.center))


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


  def test_hsd02_008_buzz_downed_health(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup to have player2 have Ayame damaged in the center
    p2.center = []
    p2_center_card, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hSD02-008", p2.center))
    p2_center_card["damage"] = p2_center_card["hp"] - 10

    _, center_card_id = unpack_game_id(p1.center[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, {}),
      (EventType.EventType_DamageDealt, {}),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "life_lost": 2, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hsd02_008_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD02-008"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 230)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen2", "#Shooter"])