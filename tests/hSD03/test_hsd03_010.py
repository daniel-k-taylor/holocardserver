import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD03_010(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str


  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hSD03-010": 1, # spot Korone
      "hSD03-002": 1, # debut Okayu
      "hSD03-014": 4, # fan Onigirya
      "hSD02-014": 4, # mascot Poyoyo
    })
    initialize_game_to_third_turn(self, p1_deck)


  def test_hsd03_010_orayo(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Korone in the center
    p1.center = []
    _, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1") # any color


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "orayo",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "orayo", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hsd03_010_collab_effect(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)
    
    # Setup to have Okayu in the center and Korone in the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.backstage))

    fans_and_mascots_ids = ids_from_cards([card for card in p1.deck if card.get("sub_type") in ["fan", "mascot"]])
    card_chosen = fans_and_mascots_ids[0]

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [card_chosen] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": fans_and_mascots_ids }),
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", "card_id": card_chosen }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    self.assertEqual(ids_from_cards(p1.hand[-1:]), [card_chosen])


  def test_hsd03_010_collab_effect_center_not_okayu(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Korone in backstage
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.backstage))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    

  def test_hsd03_010_collab_effect_no_target(self):
    engine = self.engine
  
    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Okayu in the center and Korone in the backstage
    p1.center = []
    put_card_in_play(self, p1, "hSD03-002", p1.center)
    p1.backstage = p1.backstage[1:]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hSD03-010", p1.backstage))

    # Remove all fans and mascots in the deck
    p1.deck = [card for card in p1.deck if card.get("sub_type") not in ["fan", "mascot"]]
    

    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    engine.handle_game_message(self.player1, GameAction.MainStepCollab, { "card_id": collab_card_id })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": [] }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hsd03_010_overall_check(self):
    p1: PlayerState = self.engine.get_player(self.player1)
    card = next((card for card in p1.deck if card["card_id"] == "hSD03-010"), None)
    self.assertIsNotNone(card)

    # check hp and tags
    self.assertEqual(card["hp"], 70)
    self.assertCountEqual(card["tags"], ["#JP", "#Gamers", "#AnimalEars"])