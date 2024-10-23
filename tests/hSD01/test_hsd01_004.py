import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD01_004(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  
  def test_hSD01_004_collab_effect_does_not_apply_to_arts_advantage_damage(self):
    # QnA: Q3 (2024.09.21)
    
    # Setup to put a holomem with color advantage against p2 center
    p1_deck = generate_deck_with("", { "hBP01-047": 1 })
    initialize_game_to_third_turn(self, p1_deck)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP01-047", p1.center)
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g1")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g2")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "green", "g3")
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "white", "w1")
    
    downed_holomem = p2.center[0] # holomem to be downed after the attack
        

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    collab_card_id = "player1_5"

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    self.assertEqual(len(p1.collab), 1)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "anewmap",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    collab_boost = 20
    center_art = 120
    color_advantage = 50

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": collab_boost, "source_card_id": collab_card_id }),
      (EventType.EventType_BoostStat, { "amount": color_advantage, "source_card_id": p1.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": collab_boost + center_art + color_advantage }), # no additional damage for color adv.
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

  def test_hSD01_004_collab_effect_does_not_apply_to_arts_additional_damage(self):
    # QnA: Q3 (2024.09.21)

    # Setup to put a holomem with additional arts damage
    p1_deck = generate_deck_with("", { "hBP01-062": 1 })
    initialize_game_to_third_turn(self, p1_deck)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.center = []
    center_card = put_card_in_play(self, p1, "hBP01-062", p1.center)
    spawn_cheer_on_card(self, p1, center_card["game_card_id"], "red", "r1")

    downed_holomem = p2.center[0] # holomem to be downed after the attack

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    collab_card_id = "player1_5"

    events = do_collab_get_events(self, p1, collab_card_id)
    self.assertEqual(len(p1.collab), 1)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "kikkeriki",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    collab_boost = 20
    center_art = 20

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": collab_boost, "source_card_id": collab_card_id }),
      (EventType.EventType_Decision_Choice, {}) # choose to activate kiara art boost
    ])

    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [p1.hand[0]["game_card_id"]] })

    # Events
    art_boost = 20

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_ChooseCards, { "from_zone": "hand" }),
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_BoostStat, { "amount": art_boost, "source_card_id": p1.center[0]["game_card_id"] }),
      (EventType.EventType_DamageDealt, { "damage": collab_boost + center_art + art_boost }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, { "target_id": downed_holomem["game_card_id"] }),
      (EventType.EventType_Decision_SendCheer, {})
    ])

  def test_hsd01_004_collab_boost_still_applies_after_bloom(self):
    # QnA: Q208 (2024.10.04)
    initialize_game_to_third_turn(self)
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    collab_card_id = "player1_5" # hSD01-004
    bloom_card_id = "player1_9" # hSD01-005

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    self.assertEqual(len(p1.collab), 1)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_AddTurnEffect, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    do_bloom(self, p1, bloom_card_id, p1.center[0]["game_card_id"])

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, { 
      "art_id": "nunnunshiyo",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    collab_boost = 20
    center_art = 30

    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "active_player": self.player1, "power": center_art }),
      (EventType.EventType_BoostStat, { "amount": collab_boost, "source_card_id": collab_card_id }),
      (EventType.EventType_DamageDealt, { "damage": collab_boost + center_art }), # boost still applies
      (EventType.EventType_EndTurn, {}),
      (EventType.EventType_TurnStart, { "active_player": self.player2 }),
      (EventType.EventType_ResetStepActivate, {}),
      (EventType.EventType_ResetStepCollab, {}),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_CheerStep, {})
    ])