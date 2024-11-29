import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_064(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-064": 1, # buzz Ina
      "hBP02-061": 10, # debut Ina
    })
    p2_deck = generate_deck_with("", {
      "hBP02-064": 1, # buzz Ina
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_064_archaicsmile_0_myth_in_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Ina in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "purple", "p1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Random cards in archive
    p1.archive = p1.deck[:5]
    p1.deck = p1.deck[5:]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "archaicsmile",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "archaicsmile", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_064_archaicsmile_5_myth(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Ina in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
    _, cheer_card_id = unpack_game_id(spawn_cheer_on_card(self, p1, center_card_id, "purple", "p1"))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Random cards and 5 debut Ina in archive
    p1.archive = p1.deck[:5] + p1.deck[-5:]
    p1.deck = p1.deck[5:-5]

    chosen_card, chosen_card_id = unpack_game_id(p1.backstage[0])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    self.assertGreaterEqual(len([card for card in p1.archive if "#Myth" in card["tags"]]), 5)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "archaicsmile",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { cheer_card_id: chosen_card_id }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "archaicsmile", "power": 60 }),

      (EventType.EventType_Decision_SendCheer, {}),
      
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": chosen_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertCountEqual(ids_from_cards(chosen_card["attached_cheer"]), [cheer_card_id])


  def test_hbp02_064_5_myth_no_other_holomem_to_transfer_cheer(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Ina in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "purple", "p1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Random cards and 5 debut Ina in archive
    p1.archive = p1.deck[:5] + p1.deck[-5:]
    p1.deck = p1.deck[5:-5]

    # Remove backstage
    p1.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    self.assertGreaterEqual(len([card for card in p1.archive if "#Myth" in card["tags"]]), 5)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "archaicsmile",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "archaicsmile", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_064_10_myth(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Ina in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
    _, cheer_card_id = unpack_game_id(spawn_cheer_on_card(self, p1, center_card_id, "purple", "p1"))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Random cards and 10 debut Ina in archive
    p1.archive = p1.deck[:5] + p1.deck[-10:]
    p1.deck = p1.deck[5:-10]

    chosen_card, chosen_card_id = unpack_game_id(p1.backstage[0])

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    self.assertGreaterEqual(len([card for card in p1.archive if "#Myth" in card["tags"]]), 10)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "archaicsmile",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": { cheer_card_id: chosen_card_id }
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "archaicsmile", "power": 60 }),

      (EventType.EventType_Decision_SendCheer, {}),
      
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": chosen_card_id, "attached_id": cheer_card_id }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 110 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    self.assertCountEqual(ids_from_cards(chosen_card["attached_cheer"]), [cheer_card_id])


  def test_hbp02_064_10_myth_no_other_holomem_to_transfer_cheer(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup buzz Ina in center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "purple", "p1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color

    # Random cards and 10 debut Ina in archive
    p1.archive = p1.deck[:5] + p1.deck[-10:]
    p1.deck = p1.deck[5:-10]

    # Remove backstage
    p1.backstage = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    
    self.assertGreaterEqual(len([card for card in p1.archive if "#Myth" in card["tags"]]), 10)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "archaicsmile",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "archaicsmile", "power": 60 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_DamageDealt, { "damage": 110 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])

    
  def test_hbp02_064_buzz_downed_life(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have p2 have a damaged buzz ina in the center
    p2.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-064", p2.center))
    center_card["damage"] = center_card["hp"] - 10


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "life_lost": 2, "target_player": self.player2 }),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_064_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-064", p1.center))
  
  
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
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
    actions = reset_mainstep(self)
    self.assertIsNotNone(
      next((action for action in actions if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id), None))


  def test_hbp02_064_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-064"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 250)
    self.assertCountEqual(card["tags"], ["#EN", "#Myth", "#Art", "#Sea"])