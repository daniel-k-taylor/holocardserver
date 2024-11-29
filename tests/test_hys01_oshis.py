import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState, UNLIMITED_SIZE
from app.gameengine import EventType, GameOverReason
from app.gameengine import GameAction, GamePhase, EffectType
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand, do_cheer_step_on_card
from helpers import end_turn, validate_last_event_is_error, validate_last_event_not_error, do_collab_get_events, set_next_die_rolls
from helpers import put_card_in_play, spawn_cheer_on_card, reset_performancestep, generate_deck_with, begin_performance, use_oshi_action, pick_choice

class Test_hys01_oshis(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        pass

    def test_hys_4_vs_1_suisei_v_mumei(self):
        p1deck = generate_deck_with("hYS01-004", {"hBP01-076": 3 }, [])
        p2deck = generate_deck_with("hYS01-001", {"hBP01-015": 50 }, [])
        initialize_game_to_third_turn(self, p1deck, p2deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(3)
        player2.generate_holopower(1)
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.collab)
        player1.backstage = player1.backstage[1:]

        actions = reset_mainstep(self)

        # Use blue baton for fun.
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "bluebaton"})
        events = engine.grab_events()
        # Events - move 2 cards, oshi skill, add turn effect, main step
        self.assertEqual(len(events), 10)
        validate_event(self, events[4], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "skill_id": "bluebaton",
        })
        validate_event(self, events[6], EventType.EventType_AddTurnEffect, player1.player_id, {})
        reset_mainstep(self)

        p2center = player2.center[0]
        p2back = player2.backstage[0]
        spawn_cheer_on_card(self, player1, test_card["game_card_id"], "blue", "b1")
        begin_performance(self)
        cheer_on_p1 = ids_from_cards(player1.center[0]["attached_cheer"])
        engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"]
        })
        events = engine.grab_events()
        # Events - perform, turn effect boost, diamon choose
        self.assertEqual(len(events), 6)
        validate_event(self, events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": test_card["game_card_id"],
            "art_id": "diamondintherough",
            "target_id": p2center["game_card_id"],
            "power": 20,
        })
        validate_event(self, events[2], EventType.EventType_BoostStat, self.player1, {
            "stat": "power",
            "amount": 20,
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseHolomemForEffect, self.player1, {
            "effect_player_id": self.player1,
        })
        cards_can_choose = events[4]["cards_can_choose"]
        backstage_options = [card["game_card_id"] for card in player2.backstage]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [backstage_options[0]]
        })
        events = engine.grab_events()
        # Events - damage from effect immediatley mumei choice
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player2,
        })
        choices = events[0]["choice"]
        self.assertEqual(choices[0]["incoming_damage_info"]["amount"], 10)
        # Don't use it.
        events = pick_choice(self, self.player2, 1)
        # Events damage dealt, choice for backshot
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 10,
            "special": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Use comet
        events = pick_choice(self, self.player1, 0)
        # spend 1 holo, oshi activation, Choose target.
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player1,
            "skill_id": "backshot",
        })
        # Events - mumei choice to reduce.
        events = events[-2:]
        validate_event(self, events[0], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player2,
        })
        events = pick_choice(self, self.player2, 0)
        self.assertEqual(player2.backstage[0]["damage"], 40) # 10 from art, 30 from backshot (-20 from the quickguard)
        # 1x move card, oshi activation, Reduce damage, damage dealt 0
        # perform art, damage, performance step
        self.assertEqual(len(events), 12)
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "oshi_player_id": self.player2,
            "skill_id": "quickguard",
        })
        validate_event(self, events[4], EventType.EventType_BoostStat, self.player1, {
            "stat": "damage_prevented",
            "amount": 20
        })
        validate_event(self, events[6], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.backstage[0]["game_card_id"],
            "damage": 30,
            "special": True,
        })
        validate_event(self, events[8], EventType.EventType_DamageDealt, self.player1, {
            "target_id": player2.center[0]["game_card_id"],
            "damage": 40,
            "special": False,
        })

        reset_performancestep(self)


    def test_hys_002_pekora_heal_all(self):
        p1deck = generate_deck_with("hYS01-002", {"hBP01-076": 3, "hBP01-038": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(1)
        p1center = player1.center[0]
        test_card = put_card_in_play(self, player1, "hBP01-076", player1.collab)
        player1.backstage = []
        back1 = put_card_in_play(self, player1, "hBP01-038", player1.backstage)
        back2 = put_card_in_play(self, player1, "hBP01-038", player1.backstage)
        back3 = put_card_in_play(self, player1, "hBP01-038", player1.backstage)
        back4 = put_card_in_play(self, player1, "hBP01-038", player1.backstage)

        back1["damage"] = 20
        back2["damage"] = 40
        back3["damage"] = 50
        back4["damage"] = 10
        test_card["damage"] = 30
        p1center["damage"] = 20
        actions = reset_mainstep(self)

        # Use peko's heal all
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "letsdoourbesteveryone"})
        events = engine.grab_events()
        # Events - move 1 cards, oshi skill, healx4, main step
        self.assertEqual(len(events), 14)
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "skill_id": "letsdoourbesteveryone",
        })
        validate_event(self, events[4], EventType.EventType_RestoreHP, player1.player_id, {
            "target_player_id": self.player1,
            "card_id": back1["game_card_id"],
            "healed_amount": 20,
            "new_damage": 0,
        })
        validate_event(self, events[6], EventType.EventType_RestoreHP, player1.player_id, {
            "target_player_id": self.player1,
            "card_id": back2["game_card_id"],
            "healed_amount": 20,
            "new_damage": 20,
        })
        validate_event(self, events[8], EventType.EventType_RestoreHP, player1.player_id, {
            "target_player_id": self.player1,
            "card_id": back3["game_card_id"],
            "healed_amount": 20,
            "new_damage": 30,
        })
        validate_event(self, events[10], EventType.EventType_RestoreHP, player1.player_id, {
            "target_player_id": self.player1,
            "card_id": back4["game_card_id"],
            "healed_amount": 10,
            "new_damage": 0,
        })
        reset_mainstep(self)
        self.assertEqual(p1center["damage"], 20)
        self.assertEqual(back1["damage"], 0)
        self.assertEqual(back2["damage"], 20)
        self.assertEqual(back3["damage"], 30)
        self.assertEqual(back4["damage"], 0)
        self.assertEqual(test_card["damage"], 30)


    def test_hys_003_comeonagain(self):
        p1deck = generate_deck_with("hYS01-003", {"hBP01-076": 3, "hBP01-062": 4, "hBP01-113": 4 }, [])
        initialize_game_to_third_turn(self, p1deck)
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.

        """Test"""
        player1.generate_holopower(1)
        p1center = player1.center[0]
        put_card_in_play(self, player1, "hBP01-076", player1.archive)
        put_card_in_play(self, player1, "hBP01-076", player1.archive)
        put_card_in_play(self, player1, "hBP01-113", player1.archive)
        put_card_in_play(self, player1, "hBP01-113", player1.archive)
        put_card_in_play(self, player1, "hBP01-113", player1.archive)
        expect1 = put_card_in_play(self, player1, "hBP01-062", player1.archive)
        expect2 = put_card_in_play(self, player1, "hBP01-062", player1.archive)
        expect3 = put_card_in_play(self, player1, "hBP01-062", player1.archive)
        actions = reset_mainstep(self)

        # Use the ability to choose from archive
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "comeonagain"})
        events = engine.grab_events()
        # Events - move 1 cards, oshi skill, choosecards
        self.assertEqual(len(events), 6)
        validate_event(self, events[2], EventType.EventType_OshiSkillActivation, player1.player_id, {
            "skill_id": "comeonagain",
        })
        validate_event(self, events[4], EventType.EventType_Decision_ChooseCards, player1.player_id, {
            "from_zone": "archive",
            "to_zone": "hand",
        })
        cards_can_choose = events[4]["cards_can_choose"]
        self.assertEqual(len(cards_can_choose), 3)
        self.assertListEqual(cards_can_choose, [expect1["game_card_id"], expect2["game_card_id"], expect3["game_card_id"]])
        engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [expect2["game_card_id"]]
        })
        events = engine.grab_events()
        # Events - move card, main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, player1.player_id, {
            "card_id": expect2["game_card_id"],
            "from_zone": "archive",
            "to_zone": "hand",
        })
        reset_mainstep(self)


if __name__ == '__main__':
    unittest.main()
