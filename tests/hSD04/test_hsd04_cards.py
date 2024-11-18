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


  def test_hSD04_008_art_retrieve_event_bonus(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-008": 2,
      "hSD04-013": 2,
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
    archived_food = put_card_in_play(self, p1, "hSD04-013", p1.archive)
    test_card = put_card_in_play(self, p1, "hSD04-008", p1.center)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p3")
    reset_mainstep(self)
    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "enjoythemeal",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "enjoythemeal", "power": 60 }),
      (EventType.EventType_Decision_ChooseCards, { }),
    ])
    cards_can_choose = events[1]["cards_can_choose"]
    self.assertEqual(len(cards_can_choose), 1)
    self.assertEqual(cards_can_choose[0], archived_food["game_card_id"])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [archived_food["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "archive", "to_zone": "hand" }),
      (EventType.EventType_BoostStat, { "stat": "power", "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 80 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_008_art_dont_retrieve_event_no_bonus(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-008": 2,
      "hSD04-013": 2,
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
    archived_food = put_card_in_play(self, p1, "hSD04-013", p1.archive)
    test_card = put_card_in_play(self, p1, "hSD04-008", p1.center)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p3")
    reset_mainstep(self)
    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "enjoythemeal",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "enjoythemeal", "power": 60 }),
      (EventType.EventType_Decision_ChooseCards, { }),
    ])
    cards_can_choose = events[1]["cards_can_choose"]
    self.assertEqual(len(cards_can_choose), 1)
    self.assertEqual(cards_can_choose[0], archived_food["game_card_id"])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_009_art_boost_per_event_0(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-009": 2,
      "hSD04-013": 4,
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
    test_card = put_card_in_play(self, p1, "hSD04-009", p1.center)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p3")
    reset_mainstep(self)
    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "artname_go",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "artname_go", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_009_art_boost_per_event(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-009": 2,
      "hSD04-013": 4,
      "hBP01-107": 4,
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
    test_card = put_card_in_play(self, p1, "hSD04-009", p1.center)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p3")
    reset_mainstep(self)

    # Play some events.
    event1 = add_card_to_hand(self, p1, "hBP01-107")
    event2 = add_card_to_hand(self, p1, "hBP01-107")
    event3 = add_card_to_hand(self, p1, "hSD04-013")
    nonevent = add_card_to_hand(self, p1, "hSD01-016")

    # Waste the event card just to play it.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event1["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event1["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])
    # Waste the event card just to play it.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event2["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event2["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Play a 3rd event card of a different type.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event3["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event3["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.backstage[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AddTurnEffect, { }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Also play a non-event.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": nonevent["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": nonevent["game_card_id"] }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Now we have played 3 events and 1 staff.
    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "artname_go",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "artname_go", "power": 60 }),
      (EventType.EventType_BoostStat, { "stat": "power", "amount": 120 }),
      (EventType.EventType_DamageDealt, { "damage": 180 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_009_art_boost_per_event_resets_at_turnend(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-007": 2,
      "hSD04-009": 2,
      "hSD04-013": 4,
      "hBP01-107": 4,
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
    test_card = put_card_in_play(self, p1, "hSD04-009", p1.center)
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p2")
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p3")
    reset_mainstep(self)

    # Play some events.
    event1 = add_card_to_hand(self, p1, "hBP01-107")
    event2 = add_card_to_hand(self, p1, "hBP01-107")
    event3 = add_card_to_hand(self, p1, "hSD04-013")
    nonevent = add_card_to_hand(self, p1, "hSD01-016")

    # Waste the event card just to play it.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event1["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event1["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])
    # Waste the event card just to play it.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event2["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event2["game_card_id"] }),
      (EventType.EventType_Decision_ChooseCards, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Play a 3rd event card of a different type.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event3["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event3["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.backstage[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AddTurnEffect, { }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Also play a non-event.
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": nonevent["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": nonevent["game_card_id"] }),
      (EventType.EventType_Draw, {}),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Now we have played 3 events and 1 staff.
    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])
    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "artname_go",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "artname_go", "power": 60 }),
      (EventType.EventType_DamageDealt, { "damage": 60 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_010_collabwith_choco_not_choco_center_nothinghappens(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-003": 1,
      "hSD04-010": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.backstage = []
    test_card = put_card_in_play(self, p1, "hSD04-010", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_MainStep, {})
    ])
    reset_mainstep(self)


  def test_hSD04_010_collabwith_choco_noarchive(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-003": 1,
      "hSD04-010": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.backstage = []
    p1.center = []
    test_card2 = put_card_in_play(self, p1, "hSD04-003", p1.center)
    test_card = put_card_in_play(self, p1, "hSD04-010", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_Choice, {})
    ])
    events = pick_choice(self, p1.player_id, 0)
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_MainStep, {})
    ])


  def test_hSD04_010_collabwith_choco_cheerinarchive(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-003": 1,
      "hSD04-010": 1,
    })
    initialize_game_to_third_turn(self, p1_deck)

    engine = self.engine

    p1: PlayerState = engine.get_player(self.player1)
    p2: PlayerState = engine.get_player(self.player2)

    reset_mainstep(self)

    """Test"""
    self.assertEqual(len(p1.hand), 3)
    p1.backstage = []
    p1.center = []
    p1.archive.append(p1.cheer_deck.pop())
    test_card2 = put_card_in_play(self, p1, "hSD04-003", p1.center)
    test_card = put_card_in_play(self, p1, "hSD04-010", p1.backstage)
    events = do_collab_get_events(self, p1, test_card["game_card_id"])
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Collab, {  }),
      (EventType.EventType_Decision_Choice, {})
    ])
    events = pick_choice(self, p1.player_id, 0)
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Decision_SendCheer, {})
    ])
    from_options = events[0]["from_options"]
    placements = {
      from_options[0]: p1.collab[0]["game_card_id"],
    }
    engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
      "placements": placements
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveAttachedCard, {}),
      (EventType.EventType_Decision_MainStep, {})
    ])
    reset_mainstep(self)
    self.assertEqual(len(p1.archive), 0)
    self.assertEqual(len(p1.collab[0]["attached_cheer"]), 1)



  def test_hSD04_013_omurice_heal_powerboost_cooking_no_choco_no_effect(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-013": 4,
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
    reset_mainstep(self)

    # Play some events.
    event1 = add_card_to_hand(self, p1, "hSD04-013")
    event2 = add_card_to_hand(self, p1, "hSD04-013")

    p1.center[0]["damage"] = 20
    # Play omurice
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event1["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event1["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.center[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 0 }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Play omurice 2
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event2["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event2["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.center[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "nunnun",
      "performer_id": p1.center[0]["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "nunnun", "power": 30 }),
      (EventType.EventType_DamageDealt, { "damage": 30 }),
      *end_turn_events()
    ])


  def test_hSD04_013_omurice_heal_powerboost_cooking(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-013": 4,
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
    spawn_cheer_on_card(self, p1, p1.center[0]["game_card_id"], "purple", "p1")
    reset_mainstep(self)

    # Play some events.
    event1 = add_card_to_hand(self, p1, "hSD04-013")
    event2 = add_card_to_hand(self, p1, "hSD04-013")

    p1.center[0]["damage"] = 20
    # Play omurice
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event1["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event1["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.center[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 0 }),
      (EventType.EventType_AddTurnEffect, {  }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    # Play omurice 2
    engine.handle_game_message(self.player1, GameAction.MainStepPlaySupport, {
      "card_id": event2["game_card_id"],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PlaySupportCard, { "card_id": event2["game_card_id"] }),
      (EventType.EventType_Decision_ChooseHolomemForEffect, {}),
    ])
    engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
        "card_ids": [p1.center[0]["game_card_id"]],
    })
    events = engine.grab_events()
    validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_AddTurnEffect, {  }),
      (EventType.EventType_MoveCard, { "from_zone": "floating", "to_zone": "archive" }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    begin_performance(self)

    engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
      "art_id": "underworldschoolnurse",
      "performer_id": test_card["game_card_id"],
      "target_id": p2.center[0]["game_card_id"]
    })
    events = engine.grab_events()

    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_PerformArt, { "art_id": "underworldschoolnurse", "power": 30 }),
      (EventType.EventType_BoostStat, { "stat": "power", "amount": 20 }),
      (EventType.EventType_BoostStat, { "stat": "power", "amount": 20 }),
      (EventType.EventType_DamageDealt, { "damage": 70 }),
      (EventType.EventType_DownedHolomem_Before, {}),
      (EventType.EventType_DownedHolomem, {}),
      (EventType.EventType_Decision_SendCheer, {}),
    ])


  def test_hSD04_014_bloom_chocolat(self):
    p1_deck = generate_deck_with("hSD04-001", # oshi choco
    {
      "hSD04-002": 2,
      "hSD04-005": 2,
      "hSD04-014": 1,
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
    bloom_card = add_card_to_hand(self, p1, "hSD04-005")
    bloom_card2 = add_card_to_hand(self, p1, "hSD04-005")
    chocolat = put_card_in_play(self, p1, "hSD04-014", test_card["attached_support"])
    reset_mainstep(self)
    test_card["damage"] = 50

    engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
      "card_id": bloom_card["game_card_id"],
      "target_id": test_card["game_card_id"]
    })
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card["game_card_id"], "target_card_id": test_card["game_card_id"] }),
      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 30 }),
      (EventType.EventType_Decision_MainStep, {}),
    ])

    end_turn(self)
    do_cheer_step_on_card(self, p2.center[0])
    end_turn(self)
    do_cheer_step_on_card(self, p1.center[0])
    engine.handle_game_message(self.player1, GameAction.MainStepBloom, {
      "card_id": bloom_card2["game_card_id"],
      "target_id": bloom_card["game_card_id"]
    })
    events = engine.grab_events()
    events = validate_consecutive_events(self, self.player1, events, [
      (EventType.EventType_Bloom, { "bloom_card_id": bloom_card2["game_card_id"], "target_card_id": bloom_card["game_card_id"] }),
      (EventType.EventType_RestoreHP, { "healed_amount": 20, "new_damage": 10 }),
      (EventType.EventType_Decision_MainStep, {}),
    ])
