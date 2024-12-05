import unittest
from app.gameengine import GameEngine, GameAction, is_card_holomem
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hBP02_033(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hBP02-033": 1, # 2nd Marine
      "hBP02-030": 1, # 1st Marine
    })
    p2_deck = generate_deck_with("", {
      "hBP02-061": 1, # debut Ina
    })
    initialize_game_to_third_turn(self, p1_deck, p2_deck)


  def test_hbp02_033_kimitachi(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Marine in center with holomem stacked
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-033", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]
    stacked_holomem_count = len([is_card_holomem(card) for card in center_card["stacked_cards"]])
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "kimitachi",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "kimitachi", "power": 80 }),
      (EventType.EventType_BoostStat, { "amount": 20 * stacked_holomem_count }),
      (EventType.EventType_DamageDealt, { "damage": 80 + 20 * stacked_holomem_count }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_033_kimitachi_advantage(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup Marine in center
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-033", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "red", "r1")
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w2") # any color
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]
    stacked_holomem_count = len([is_card_holomem(card) for card in center_card["stacked_cards"]])

    # Setup Ina in p2 center
    p2.center = []
    _, p2_center_card_id = unpack_game_id(put_card_in_play(self, p2, "hBP02-061", p2.center))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "kimitachi",
      "performer_id": center_card_id,
      "target_id": p2_center_card_id
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "kimitachi", "power": 80 }),
      (EventType.EventType_BoostStat, { "amount": 50 }),
      (EventType.EventType_BoostStat, { "amount": 20 * stacked_holomem_count }),
      (EventType.EventType_DamageDealt, { "damage": 80 + 50 + 20 * stacked_holomem_count }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {})
    ])


  def test_hbp02_033_bloom_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup 1st Marine in center and 2nd Marine in hand
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]
    archive_card_id, archive_2_card_id = ids_from_cards(p1.backstage[:2])

    # Fill archive with non-holomem cards and 2 holomem card
    p1.archive = []
    add_card_to_archive(self, p1, "hSD01-019")
    add_card_to_archive(self, p1, "hSD01-019")
    add_card_to_archive(self, p1, "hSD01-019")
    p1.archive += p1.backstage[:2]


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [archive_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [archive_card_id, archive_2_card_id] }),

      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand", "card_id": archive_card_id }),
      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2.center[0]["game_card_id"] }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_blooom_effect_no_holomem_in_archive(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup 1st Marine in center and 2nd Marine in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))

    # Fill archive with non-holomem cards
    p1.archive = []
    add_card_to_archive(self, p1, "hSD01-019")
    add_card_to_archive(self, p1, "hSD01-019")
    add_card_to_archive(self, p1, "hSD01-019")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_bloom_effect_pass_less_than_3_stacked(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup 1st Marine in center and 2nd Marine in hand
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_bloom_effect_pass_3_or_more_stacked(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup 1st Marine in center and 2nd Marine in hand with at least 3 stacked holomem
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]

    # Setup p2 center and collab
    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2.collab = p2.backstage[:1]
    p2.backstage = p2.backstage[1:]
    _, p2_collab_card_id = unpack_game_id(p2.collab[0])


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 }),
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p2_center_card_id] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": [p2_center_card_id, p2_collab_card_id] }),

      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_bloom_effect_pass_3_or_more_stacked_no_center(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup 1st Marine in center and 2nd Marine in hand with at least 3 stacked holomem
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]

    # Setup p2 collab with no center
    p2.collab = p2.backstage[:1]
    p2.backstage = p2.backstage[1:]
    _, p2_collab_card_id = unpack_game_id(p2.collab[0])
    p2.center = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 }),

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2_collab_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_bloom_effect_pass_3_or_more_stacked_no_collab(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)
    
    # Setup 1st Marine in center and 2nd Marine in hand with at least 3 stacked holomem
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-030", p1.center))
    _, bloom_card_id = unpack_game_id(add_card_to_hand(self, p1, "hBP02-033"))
    center_card["stacked_cards"] = p1.backstage[:2]
    p1.backstage = p1.backstage[2:]

    # Setup p2 center with no collab
    _, p2_center_card_id = unpack_game_id(p2.center[0])
    p2.collab = []


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, { "card_id": bloom_card_id, "target_id": center_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 1 }),

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card_id }),
      (EventType.EventType_Decision_Choice, {}),

      (EventType.EventType_DamageDealt, { "damage": 50, "special": True, "target_id": p2_center_card_id }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hbp02_033_baton_pass(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
  
    # Setup
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hBP02-033", p1.center))
  
  
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


  def test_hbp02_033_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hBP02-033"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 200)
    self.assertCountEqual(card["tags"], ["#JP", "#Gen3", "#Art", "#Sea"])