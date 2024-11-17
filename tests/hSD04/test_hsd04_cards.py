import unittest
from app.gameengine import GameEngine, GameAction
from app.gameengine import PlayerState
from app.gameengine import EventType
from tests.helpers import *


class Test_hSD04(unittest.TestCase):
  engine: GameEngine
  player1: str
  player2: str

  def setUp(self):
    pass

  def test_hSD04_001_cardchange(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    p1.generate_holopower(1)
    reset_mainstep(self)

    """Test"""
    # Events
    self.assertEqual(len(p1.hand), 3)
    events = use_oshi_action(self, "cardchange")
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "holopower", "to_zone": "archive" }),
      (EventType.EventType_OshiSkillActivation, { "skill_id": "cardchange" }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_Decision_ChooseCards, {})
    ])
    self.assertEqual(len(p1.hand), 5)
    archive_it = p1.hand[3]["game_card_id"]
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [archive_it],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.hand), 4)
    self.assertEqual(p1.archive[0]["game_card_id"], archive_it)


  def test_hSD04_003_oshi_is_purple(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-003": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.backstage = []
    test_card = put_card_in_play(self, p1, "hSD04-003", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.hand), 4)
    reset_mainstep(self)


  def test_hSD04_003_not_oshi_is_purple(self):
    p1_deck = generate_deck_with("hSD01-001", # oshi not purple!
    {
      "hSD04-003": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.backstage = []
    test_card = put_card_in_play(self, p1, "hSD04-003", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(len(p1.hand), 3)
    reset_mainstep(self)


  def test_hSD04_004_search_food_none(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-004": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    test_card = put_card_in_play(self, p1, "hSD04-004", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_Choice, {})
    ])
    self.assertEqual(len(p1.hand), 3)
    events = pick_choice(self, p1.player_id, 0)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_ChooseCards, {})
    ])
    chosen_card = p1.hand[2]["game_card_id"]
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [chosen_card],
    })
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_Decision_ChooseCards, {})
    ])
    self.assertEqual(p1.archive[0]["game_card_id"], chosen_card)
    # Searching deck for card.
    # There is none to choose from.
    self.assertEqual(len(events[1]["cards_can_choose"]), 0)
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])

    reset_mainstep(self)


  def test_hSD04_004_search_food_found(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-004": 1,
      "hSD04-013": 2,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    test_card = put_card_in_play(self, p1, "hSD04-004", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_Choice, {})
    ])
    self.assertEqual(len(p1.hand), 3)
    events = pick_choice(self, p1.player_id, 0)
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_ChooseCards, {})
    ])
    chosen_card = p1.hand[2]["game_card_id"]
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [chosen_card],
    })
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "hand", "to_zone": "archive" }),
      (EventType.EventType_Decision_ChooseCards, {})
    ])
    self.assertEqual(p1.archive[0]["game_card_id"], chosen_card)
    # Searching deck for card.
    # There is none to choose from.
    cards_can_choose = events[1]["cards_can_choose"]
    self.assertEqual(len(cards_can_choose), 2)
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [cards_can_choose[0]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "deck", "to_zone": "hand", }),
      (EventType.EventType_ShuffleDeck, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    self.assertEqual(p1.hand[-1]["game_card_id"], cards_can_choose[0])

    reset_mainstep(self)


  def test_hSD04_006_forbiddenkiss_default(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-006": 2,
    },
    {
      "hY05-001": 20,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.center = []
    p1.backstage = []
    test_card = put_card_in_play(self, p1, "hSD04-006", p1.center)
    test_card2 = put_card_in_play(self, p1, "hSD04-006", p1.collab)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.collab[0]["game_card_id"], "purple", "p3")
    spawn_cheer_on_card(self, p1, p1.collab[0]["game_card_id"], "purple", "p4")
    reset_mainstep(self)
    begin_performance(self)

    # Preset some damage to heal
    test_card["damage"] = 50

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "forbiddenkiss",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "forbiddenkiss", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_RestoreHP, { "healed_amount": 30, "new_damage": 20 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
    ])
    self.assertEqual(test_card["damage"], 20)


  def test_hSD04_006_forbiddenkiss_stoneaxe(self):
    """
    Currently for this interaction, deal damage is treated as before the cleanup phase
    So stone axe is the last thing.
    """
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-006": 2,
      "hBP01-114": 2,
    },
    {
      "hY05-001": 20,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.center = []
    p1.backstage = []
    test_card = put_card_in_play(self, p1, "hSD04-006", p1.center)
    axe = put_card_in_play(self, p1, "hBP01-114", test_card["attached_support"])
    test_card2 = put_card_in_play(self, p1, "hSD04-006", p1.collab)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.collab[0]["game_card_id"], "purple", "p3")
    spawn_cheer_on_card(self, p1, p1.collab[0]["game_card_id"], "purple", "p4")
    reset_mainstep(self)
    begin_performance(self)

    # Preset some damage to heal
    test_card["damage"] = 40

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "forbiddenkiss",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Event
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "forbiddenkiss", "power": 30 }),
      (EventType.EventType_BoostStat, { "stat": "power", "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 50 }),
      (EventType.EventType_RestoreHP, { "healed_amount": 40, "new_damage": 0 }),
      (EventType.EventType_DamageDealt, { "damage": 10 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
    ])
    self.assertEqual(test_card["damage"], 10)


  def test_hSD04_007_art_heal_backstage(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
    },
    {
      "hY05-001": 20,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.center = []
    p1.backstage = p1.backstage[1:]
    test_card = put_card_in_play(self, p1, "hSD04-007", p1.center)
    test_card2 = put_card_in_play(self, p1, "hSD04-007", p1.collab)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, test_card2["game_card_id"], "purple", "p3")
    spawn_cheer_on_card(self, p1, test_card2["game_card_id"], "purple", "p4")
    reset_mainstep(self)
    begin_performance(self)

    # Preset some damage to heal
    damaged_back = p1.backstage[0]
    damaged_back["damage"] = 30

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "daisukichu",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })

    # Event
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "daisukichu", "power": 30 }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, { }),
    ])
    cards_can_choose = events[1]["cards_can_choose"]
    self.assertListEqual(cards_can_choose, ids_from_cards(p1.backstage))
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [damaged_back["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 10 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      (EventType.EventType_Decision_PerformanceStep, {}),
    ])
    self.assertEqual(damaged_back["damage"], 10)

  def test_hSD04_007_bloom_retrieve_nonlimited_event(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-012": 1,
      "hSD04-013": 1,
    },
    {
      "hY05-001": 20,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.center = []
    test_card = put_card_in_play(self, p1, "hSD04-002", p1.center)
    bloom_card = add_card_to_hand(self, p1, "hSD04-007")
    limited = put_card_in_play(self, p1, "hSD04-012", p1.archive)
    nonlimited = put_card_in_play(self, p1, "hSD04-013", p1.archive)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    reset_mainstep(self)

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
      "card_id": bloom_card["game_card_id"],
      "target_id": test_card["game_card_id"]
    })
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card["game_card_id"], "target_card_id": test_card["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, { }),
    ])
    cards_can_choose = events[1]["cards_can_choose"]
    self.assertTrue(limited["game_card_id"] not in cards_can_choose)
    self.assertTrue(nonlimited["game_card_id"] in cards_can_choose)
    self.assertEqual(len(cards_can_choose), 1)
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [nonlimited["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])
    self.assertEqual(p1.hand[-1]["game_card_id"], nonlimited["game_card_id"])
