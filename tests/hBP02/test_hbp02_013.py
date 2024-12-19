import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *

def support_action_is_present(action: dict, card_ids: list[str]) -> bool:
  return action.get("action_type") == GameAction.MainStepPlaySupport and action.get("card_id") in card_ids

class Test_hBP02_013(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-013": 1, # 2nd Fubuki
      "hBP02-089": 4, # support Mascot
      "hBP02-090": 1, # support Mascot
      "hBP02-091": 1, # support Mascot
    })
    p2_deck = generate_deck_with("", {
      "hBP02-061": 4, # debut Ina
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_013_acornucopia(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki with mascot in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-013", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "acornucopia",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "acornucopia", "power": 80 }),
      (EventType.EventType_BoostStat, { "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 100 }),
      *end_turn_events()
    ])

    
  def test_hbp02_013_acornucopia_mascot_in_different_zones(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki with mascot in the center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-013", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color
    put_card_in_play(self, p1, "hBP02-089", center_card["attached_support"])

    # Setup holomem in collab and backstage attached with Mascot
    p1.collab = p1.backstage[:1]
    p1.backstage = p1.backstage[1:]
    put_card_in_play(self, p1, "hBP02-089", p1.collab[0]["attached_support"])
    put_card_in_play(self, p1, "hBP02-089", p1.backstage[0]["attached_support"])
    put_card_in_play(self, p1, "hBP02-089", p1.backstage[1]["attached_support"])

    # give p2 center high hp
    p2.center[0]["hp"] = 300


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "acornucopia",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "acornucopia", "power": 80 }),
      (EventType.EventType_BoostStat, { "amount": 20 * 4 }),
      (EventType.EventType_DamageDealt, { "damage": 80 + 20 * 4 }),
      *end_turn_events()
    ])


  def test_hbp02_013_acornucopia_advantage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Fubuki with mascot in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-013", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2")
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1") # any color

    # Setup Ina in p2 center and give high hp
    p2.center = []
    put_card_in_play(self, p2, "hBP02-061", p2.center)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "acornucopia",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "acornucopia", "power": 80 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 130 }),
      *end_turn_events()
    ])


  def test_hbp02_013_gift_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup Fubuki with mascots in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-013", p1.center))

    _, first_mcard_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-089"))
    _, second_mcard_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-090"))
    _, third_mcard_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-091"))

    # remove other holomem on field
    p1.collab = []
    p1.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    mascot_actions = [action for action in actions if support_action_is_present(action, [first_mcard_id, second_mcard_id, third_mcard_id])]
    self.assertEqual(len(mascot_actions), 3)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": first_mcard_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [first_mcard_id])

    actions = reset_mainstep(self)
    mascot_actions = [action for action in actions if support_action_is_present(action, [second_mcard_id, third_mcard_id])]
    self.assertEqual(len(mascot_actions), 2)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": second_mcard_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [first_mcard_id, second_mcard_id])

    actions = reset_mainstep(self)
    mascot_actions = [action for action in actions if support_action_is_present(action, [third_mcard_id])]
    self.assertEqual(len(mascot_actions), 0)


  def test_hbp02_013_gift_effect_not_same_mascot_name(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup Fubuki with mascots in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-013", p1.center))

    _, first_mcard_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-089"))
    _, second_mcard_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-089"))

    # remove other holomem on field
    p1.collab = []
    p1.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    actions = reset_mainstep(self)
    mascot_actions = [action for action in actions if support_action_is_present(action, [first_mcard_id, second_mcard_id])]
    self.assertEqual(len(mascot_actions), 2)

    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, { "card_id": first_mcard_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [center_card_id] })
    self.assertCountEqual(ids_from_cards(center_card["attached_support"]), [first_mcard_id])

    actions = reset_mainstep(self)
    mascot_actions = [action for action in actions if support_action_is_present(action, [second_mcard_id])]
    self.assertEqual(len(mascot_actions), 0)


  def test_hbp02_013_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-013"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 180)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen1", "#Gamers", "#AnimalEars", "#Art"])