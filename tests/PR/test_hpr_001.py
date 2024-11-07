import unittest

from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hPR_001(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str
  

  def setUp(self):
    p1_deck = generate_deck_with("", {
      "hPR-001": 1, # spot Miko 
    }, {
      "hY01-001": 10, # white cheer
      "hY03-001": 5, # red cheer
      "hY04-001": 5, # blue cheer
    })
    initialize_game_to_third_turn(self, p1_deck)

  
  def test_hPR_001_collab_effect(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # setup to have miko in the backstage
    p1.backstage = p1.backstage[:-1]
    _, collab_card_id = unpack_game_id(put_card_in_play(self, p1, "hPR-001", p1.backstage))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    events = do_collab_get_events(self, p1, collab_card_id)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, { "collab_card_id": collab_card_id }),
      (EventType.EventType_Decision_Choice, {})
    ])

    # only red and blue cheers
    cheer_targets = [cheer["game_card_id"] for cheer in p1.cheer_deck if cheer["card_id"] in ["hY03-001", "hY04-001"]]
    chosen_cheer = cheer_targets[0]
    chosen_target = p1.backstage[0]["game_card_id"]

    # choose to activate the collab effect
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, { "choice_index": 0 })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RollDie, {}),
      (EventType.EventType_Decision_ChooseCards, { "cards_can_choose": cheer_targets })
    ])

    # choose and attach cheer to a holomem in the backstage
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_cheer] })
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, { "card_ids": [chosen_target] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_ChooseHolomemForEffect, { "cards_can_choose": ids_from_cards(p1.backstage) }),
      (EventType.EventType_MoveCard, {
        "from_zone": "cheer_deck",
        "to_zone": "holomem",
        "zone_card_id": chosen_target,
        "card_id": chosen_cheer
      }),
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hPR_001_baton_pass(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)

    # Setup to have Miko in the center with cheers to baton pass
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hPR-001", p1.center))
    _, back_card_id = unpack_game_id(p1.backstage[0])
    _, cheer_1 = unpack_game_id(spawn_cheer_on_card(self, p1, center_card_id, "white", "w1"))
    _, cheer_2 = unpack_game_id(spawn_cheer_on_card(self, p1, center_card_id, "white", "w2"))


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)

    # Events
    available_actions = reset_mainstep(self)
    self.assertTrue(any(action for action in available_actions \
                          if action["action_type"] == GameAction.MainStepBatonPass and action["center_id"] == center_card_id))

    engine.handle_game_message(self.player1, GameAction.MainStepBatonPass, { "card_id": back_card_id, "cheer_ids": [cheer_1] })

    # Events
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveAttachedCard, { "from_holomem_id": center_card_id, "to_holomem_id": "archive", "attached_id": cheer_1 }),
      (EventType.EventType_MoveCard, { "from_zone": "center", "to_zone": "backstage", "card_id": center_card_id }),
      (EventType.EventType_MoveCard, { "from_zone": "backstage", "to_zone": "center" }),
      (EventType.EventType_Decision_MainStep, {})
    ])

    # check the details of the cards that moved
    self.assertTrue(any(True for card in p1.backstage if card["game_card_id"] == center_card_id))
    self.assertEqual(len(center_card["attached_cheer"]), 1)
    self.assertTrue(any(True for cheer in center_card["attached_cheer"] if cheer["game_card_id"] == cheer_2))
    self.assertEqual(p1.center[0]["game_card_id"], back_card_id)


  def test_hPR_001_HP_and_attack(self):
    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    # Setup to have Miko in the center with cheers
    p1.center = []
    center_card, center_card_id = unpack_game_id(put_card_in_play(self, p1, "hPR-001", p1.center))
    spawn_cheer_on_card(self, p1, center_card_id, "white", "w1")


    """Test"""
    self.assertEqual(engine.active_player_id, self.player1)
    self.assertEqual(center_card["hp"], 50)

    begin_performance(self)
    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "flowerrhapsody",
      "performer_id": center_card_id,
      "target_id": p2.center[0]["game_card_id"]
    })

    # Events
    events = engine.grab_events()
    jsonprint(events)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "power": 10 }),
      (EventType.EventType_DamageDealt, { "damage": 10 }),
      *end_turn_events()
    ])