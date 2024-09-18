import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState, UNLIMITED_SIZE
from app.gameengine import EventType
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand, do_cheer_step_on_card
from helpers import end_turn, validate_last_event_is_error, validate_last_event_not_error, do_collab_get_events, set_next_die_rolls

class TestOshiSkills(unittest.TestCase):

    engine : GameEngine
    player1 : str
    player2 : str

    def setUp(self):
        initialize_game_to_third_turn(self)

    def test_oshi_skill_conditions(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Test the oshi skill usage conditions"""
        actions = reset_mainstep(self)
        # No holopower, so no oshi actions.
        for action in actions:
            self.assertNotEqual(action["action_type"], GameAction.MainStepOshiSkill)

        # Azki has 1 activated and one on die roll, so if I get 3 holopower there should only be 1 oshi skill.
        player1.generate_holopower(3)
        player2.generate_holopower(3)
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 1)
        self.assertEqual(oshi_actions[0]["skill_id"], "micintherighthand")

        # Pretend we used it this game.
        player1.effects_used_this_game.append("micintherighthand")
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 0)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        # P2 gets both in their list.
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)
        self.assertEqual(oshi_actions[0]["skill_id"], "replacement")
        self.assertEqual(oshi_actions[1]["skill_id"], "soyouretheenemy")
        # Pretend p2 used replacement this turn.
        player2.effects_used_this_game.append("replacement")
        player2.effects_used_this_turn.append("replacement")
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 1)
        self.assertEqual(oshi_actions[0]["skill_id"], "soyouretheenemy")

        end_turn(self)
        do_cheer_step_on_card(self, player1.center[0])
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 0)

        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        # Both are available again
        actions = reset_mainstep(self)
        oshi_actions = [action for action in actions if action["action_type"] == GameAction.MainStepOshiSkill]
        self.assertEqual(len(oshi_actions), 2)
        self.assertEqual(oshi_actions[0]["skill_id"], "replacement")
        self.assertEqual(oshi_actions[1]["skill_id"], "soyouretheenemy")

    def test_sora_replacement(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Sora skill Replacement"""
        # Sora is p2.
        player2.generate_holopower(3)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        top_holopower = player2.holopower[0]
        engine.handle_game_message(self.player2, GameAction.MainStepOshiSkill, {"skill_id": "replacement"})
        events = self.engine.grab_events()
        # Events - holopower movecard to archive, oshi skill activation, move cheer ability
        self.assertEqual(len(events), 6)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top_holopower['game_card_id'],
        })
        self.assertEqual(top_holopower["game_card_id"], player2.archive[0]["game_card_id"])
        self.assertEqual(len(player2.holopower), 2)
        validate_event(self, events[3], EventType.EventType_OshiSkillActivation, self.player2, {
            "oshi_player_id": self.player2,
            "skill_id": "replacement",
        })
        validate_event(self, events[5], EventType.EventType_Decision_SendCheer, self.player2, {
            "effect_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
        })
        available_cheer = events[5]["from_options"]
        available_targets = events[5]["to_options"]
        self.assertEqual(len(available_cheer), 2) # 2 cheer for the 2 turns
        self.assertEqual(len(available_targets), 5) # It returns all holomems in play, but removes the target if they're the only one with cheer.

        # Try to give cheer to the center.
        placements = {
            available_cheer[0]: player2.center[0]["game_card_id"]
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 1)
        validate_last_event_is_error(self, events)

        # Give it to the first backstage.
        placements = {
            available_cheer[0]: player2.backstage[0]["game_card_id"]
        }
        engine.handle_game_message(self.player2, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # Events - move cheer, back to main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[1], EventType.EventType_MoveAttachedCard, self.player2, {
            "owning_player_id": self.player2,
            "from_holomem_id": player2.center[0]["game_card_id"],
            "to_holomem_id": player2.backstage[0]["game_card_id"],
            "attached_id": available_cheer[0],
        })
        validate_event(self, events[3], EventType.EventType_Decision_MainStep, self.player2, {"active_player": self.player2})
        self.assertEqual(len(player2.backstage[0]["attached_cheer"]), 1)
        self.assertEqual(player2.backstage[0]["attached_cheer"][0]["game_card_id"], available_cheer[0])
        self.assertEqual(len(player2.center[0]["attached_cheer"]), 1)
        self.assertEqual(player2.center[0]["attached_cheer"][0]["game_card_id"], available_cheer[1])

    def test_sora_soyouretheenemy(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Sora skill soyourethenemy"""
        # Sora is p2.
        player2.generate_holopower(3)
        end_turn(self)
        do_cheer_step_on_card(self, player2.center[0])
        top_holopower = player2.holopower[0]
        top2_holopower = player2.holopower[1]
        engine.handle_game_message(self.player2, GameAction.MainStepOshiSkill, {"skill_id": "soyouretheenemy"})
        events = self.engine.grab_events()
        # Events - holopower movecard to archive * 2, oshi skill activation, move holomem decision
        self.assertEqual(len(events), 8)
        validate_event(self, events[1], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top_holopower['game_card_id'],
        })
        validate_event(self, events[3], EventType.EventType_MoveCard, self.player2, {
            "moving_player_id": self.player2,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top2_holopower['game_card_id'],
        })
        self.assertEqual(top_holopower["game_card_id"], player2.archive[1]["game_card_id"])
        self.assertEqual(top2_holopower["game_card_id"], player2.archive[0]["game_card_id"])
        self.assertEqual(len(player2.holopower), 1)
        validate_event(self, events[5], EventType.EventType_OshiSkillActivation, self.player2, {
            "oshi_player_id": self.player2,
            "skill_id": "soyouretheenemy",
        })
        validate_event(self, events[7], EventType.EventType_Decision_SwapHolomemToCenter, self.player2, {
            "effect_player_id": self.player2,
        })
        choice_ids = events[7]["cards_can_choose"]
        opponent_current_center = player1.center[0]["game_card_id"]
        self.assertEqual(len(choice_ids), 5)
        self.assertTrue(opponent_current_center not in choice_ids)
        for choice_id in choice_ids:
            self.assertTrue(choice_id in ids_from_cards(player1.backstage))

        # Swap with #1
        current_center = player1.center[0]["game_card_id"]
        chosen_swap = choice_ids[0]
        engine.handle_game_message(self.player2, GameAction.EffectResolution_ChooseCardsForEffect, {
            "card_ids": [chosen_swap]
        })
        events = self.engine.grab_events()
        # Events - swap (2 moves), turn effect added, back to main step
        self.assertEqual(len(events), 8)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "center",
            "to_zone": "backstage",
            "zone_card_id": "",
            "card_id": current_center
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "backstage",
            "to_zone": "center",
            "zone_card_id": "",
            "card_id": chosen_swap
        })
        validate_event(self, events[5], EventType.EventType_AddTurnEffect, self.player2, { "effect_player_id": self.player2 })
        validate_event(self, events[7], EventType.EventType_Decision_MainStep, self.player2, { "active_player": self.player2 })

        # Now that that's done, enter performance and swing with the bonus.
        engine.handle_game_message(self.player2, GameAction.MainStepBeginPerformance, {})
        events = self.engine.grab_events()
        art_target = player1.center[0]
        performer = player2.center[0]
        validate_last_event_not_error(self, events)
        engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": art_target["game_card_id"]
        })
        events = self.engine.grab_events()
        validate_last_event_not_error(self, events)
        # Events - power boost, perform art, damage_dealt, distribute cheer
        self.assertEqual(len(events), 10)
        self.assertEqual(art_target["damage"], 80)
        validate_event(self, events[1], EventType.EventType_BoostStat, self.player2, {
            "card_id": performer["game_card_id"],
            "stat": "power",
            "amount": 50,
        })
        validate_event(self, events[3], EventType.EventType_PerformArt, self.player2, {
            "active_player": self.player2,
            "performer_id": performer["game_card_id"],
            "art_id": "nunnun",
            "target_id": art_target["game_card_id"],
            "target_player": self.player1,
            "power": 80,
        })
        validate_event(self, events[5], EventType.EventType_DamageDealt, self.player2, {
            "target_player": self.player1,
            "target_id": art_target["game_card_id"],
            "damage": 80,
            "special": False,
        })
        validate_event(self, events[7], EventType.EventType_DownedHolomem, self.player2, {
            "target_player": self.player1,
            "target_id": art_target["game_card_id"],
            "life_lost": 1,
            "life_loss_prevented": False,
            "game_over": False,
        })
        validate_event(self, events[9], EventType.EventType_Decision_SendCheer, self.player2, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "life",
        })


    def test_azki_micintherighthand(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Azki skill micintherighthand"""
        # Azki is p1.
        player1.generate_holopower(3)
        add_card_to_hand(self, player1, "hSD01-008") # Green azki debut
        player1.archive_holomem_from_play(player1.backstage[0]["game_card_id"])
        player1.move_card(player1.hand[-1]["game_card_id"], "backstage")
        azki_card = player1.backstage[-1]
        # Dump a bunch of cheer in the archive.
        for i in range(10):
            player1.move_card(player1.cheer_deck[0]["game_card_id"], "archive")
        reset_mainstep(self)

        top_holopower = player1.holopower[0]
        top2_holopower = player1.holopower[1]
        top3_holopower = player1.holopower[2]
        engine.handle_game_message(self.player1, GameAction.MainStepOshiSkill, {"skill_id": "micintherighthand"})
        events = self.engine.grab_events()
        # Events - holopower movecard to archive * 3, oshi skill activation, send_cheer
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top_holopower['game_card_id'],
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top2_holopower['game_card_id'],
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": top3_holopower['game_card_id'],
        })
        self.assertEqual(top_holopower["game_card_id"], player1.archive[2]["game_card_id"])
        self.assertEqual(top2_holopower["game_card_id"], player1.archive[1]["game_card_id"])
        self.assertEqual(top3_holopower["game_card_id"], player1.archive[0]["game_card_id"])
        self.assertEqual(len(player1.holopower), 0)
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "micintherighthand",
        })
        validate_event(self, events[8], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 0,
            "amount_max": 10,
            "from_zone": "archive",
            "to_zone": "holomem",
        })
        from_options = events[8]["from_options"]
        to_options = events[8]["to_options"]
        self.assertEqual(len(from_options), len(player1.archive) - 4) # 10 cheer in archive, 3 holopower and one holomem
        for option in from_options:
            self.assertTrue(option in ids_from_cards(player1.archive))
        self.assertEqual(len(to_options), 1) # Only 1 green holomem on board
        self.assertEqual(to_options[0], azki_card["game_card_id"])

        placements = {}
        cheer_placing = []
        for i in range(7):
            placements[from_options[i]] = azki_card["game_card_id"]
            cheer_placing = from_options[i]
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # 7 move cards, back to main step
        self.assertEqual(len(events), 16)
        self.assertEqual(len(azki_card["attached_cheer"]), 7)
        validate_event(self, events[15], EventType.EventType_Decision_MainStep, self.player2, {"active_player": self.player1})

    def test_azki_mapinthelefthand_setto1_goback(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Azki skill mapinthelefthand"""
        # Azki is p1.
        expected_holopower = [player1.deck[0], player1.deck[1], player1.deck[2]]
        expected_holopower.reverse()
        player1.generate_holopower(2)
        add_card_to_hand(self, player1, "hSD01-009") # Roll die collab azki
        player1.archive_holomem_from_play(player1.backstage[0]["game_card_id"])
        player1.move_card(player1.hand[-1]["game_card_id"], "backstage")
        azki_card = player1.backstage[-1]

        top_cheer = player1.cheer_deck[0]
        reset_mainstep(self)
        events = do_collab_get_events(self, player1, azki_card["game_card_id"])
        # Events - holopower gen, oshi skill choie
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": azki_card["game_card_id"],
            "holopower_generated": 1,
        })
        self.assertEqual(len(player1.holopower), 3)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Choice is to use ability or not, use it.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - holopower moved * 3, oshi skill activation, force result pick
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[0]["game_card_id"]
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[1]["game_card_id"]
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[2]["game_card_id"]
        })
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "mapinthelefthand",
        })
        validate_event(self, events[8], EventType.EventType_ForceDieResult, self.player1, {
            "choice_event": True,
            "effect_player_id": self.player1,
            "min_choice": 0,
            "max_choice": 5,
        })

        # Force the result to 1
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - die roll, collab effect 1 (decision_send_cheer)
        self.assertEqual(len(events), 4)

        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "to_limitation": "backstage",
        })
        backstage_recipient = player1.backstage[0]
        placements = {
            top_cheer["game_card_id"]: backstage_recipient["game_card_id"]
        }
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # Events - move cheer, 1 result effect, choose to go back.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": backstage_recipient["game_card_id"],
            "attached_id": top_cheer["game_card_id"],
        })
        self.assertEqual(len(backstage_recipient["attached_cheer"]), 1)
        self.assertEqual(backstage_recipient["attached_cheer"][0]["game_card_id"], top_cheer["game_card_id"])
        validate_event(self, events[2], EventType.EventType_Choice_SendCollabBack, self.player1, {
            "choice_event": True,
            "effect_player_id": self.player1,
            "min_choice": 0,
            "max_choice": 1,
        })
        # Decision to move back from collab.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 1
        })
        events = self.engine.grab_events()
        # Events - move back, back to main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "collab",
            "to_zone": "backstage",
            "card_id": azki_card["game_card_id"],
        })
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.collab), 0)

    def test_azki_mapinthelefthand_setto1_dontgoback(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Azki skill mapinthelefthand"""
        # Azki is p1.
        expected_holopower = [player1.deck[0], player1.deck[1], player1.deck[2]]
        expected_holopower.reverse()
        player1.generate_holopower(2)
        add_card_to_hand(self, player1, "hSD01-009") # Roll die collab azki
        player1.archive_holomem_from_play(player1.backstage[0]["game_card_id"])
        player1.move_card(player1.hand[-1]["game_card_id"], "backstage")
        azki_card = player1.backstage[-1]

        top_cheer = player1.cheer_deck[0]
        reset_mainstep(self)
        events = do_collab_get_events(self, player1, azki_card["game_card_id"])
        # Events - holopower gen, oshi skill question
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": azki_card["game_card_id"],
            "holopower_generated": 1,
        })
        self.assertEqual(len(player1.holopower), 3)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Choice is to use ability or not, use it.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - holopower moved * 3, oshi skill activation, force result pick
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[0]["game_card_id"]
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[1]["game_card_id"]
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[2]["game_card_id"]
        })
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "mapinthelefthand",
        })
        validate_event(self, events[8], EventType.EventType_ForceDieResult, self.player1, {
            "choice_event": True,
            "effect_player_id": self.player1,
            "min_choice": 0,
            "max_choice": 5,
        })

        # Force the result to 1
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - die roll, collab effect 1 (decision_send_cheer)
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 1,
            "rigged": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "to_limitation": "backstage",
        })
        backstage_recipient = player1.backstage[0]
        placements = {
            top_cheer["game_card_id"]: backstage_recipient["game_card_id"]
        }
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # Events - move cheer, 1 result effect, choose to go back.
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": backstage_recipient["game_card_id"],
            "attached_id": top_cheer["game_card_id"],
        })
        self.assertEqual(len(backstage_recipient["attached_cheer"]), 1)
        self.assertEqual(backstage_recipient["attached_cheer"][0]["game_card_id"], top_cheer["game_card_id"])
        validate_event(self, events[2], EventType.EventType_Choice_SendCollabBack, self.player1, {
            "choice_event": True,
            "effect_player_id": self.player1,
            "min_choice": 0,
            "max_choice": 1,
        })
        # Decision to move back from collab.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - back to main step
        self.assertEqual(len(events), 2)
        validate_event(self, events[0], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.collab), 1)


    def test_azki_mapinthelefthand_setto4(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Azki skill mapinthelefthand"""
        # Azki is p1.
        expected_holopower = [player1.deck[0], player1.deck[1], player1.deck[2]]
        expected_holopower.reverse()
        player1.generate_holopower(2)
        add_card_to_hand(self, player1, "hSD01-009") # Roll die collab azki
        player1.archive_holomem_from_play(player1.backstage[0]["game_card_id"])
        player1.move_card(player1.hand[-1]["game_card_id"], "backstage")
        azki_card = player1.backstage[-1]

        top_cheer = player1.cheer_deck[0]
        reset_mainstep(self)
        events = do_collab_get_events(self, player1, azki_card["game_card_id"])
        # Events - holopower gen, oshi skill question
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": azki_card["game_card_id"],
            "holopower_generated": 1,
        })
        self.assertEqual(len(player1.holopower), 3)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Choice is to use ability or not, use it.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 0
        })
        events = self.engine.grab_events()
        # Events - holopower moved * 3, oshi skill activation, force result pick
        self.assertEqual(len(events), 10)
        validate_event(self, events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[0]["game_card_id"]
        })
        validate_event(self, events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[1]["game_card_id"]
        })
        validate_event(self, events[4], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "archive",
            "card_id": expected_holopower[2]["game_card_id"]
        })
        validate_event(self, events[6], EventType.EventType_OshiSkillActivation, self.player1, {
            "oshi_player_id": self.player1,
            "skill_id": "mapinthelefthand",
        })
        validate_event(self, events[8], EventType.EventType_ForceDieResult, self.player1, {
            "choice_event": True,
            "effect_player_id": self.player1,
            "min_choice": 0,
            "max_choice": 5,
        })

        # Force the result to 4
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 3
        })
        events = self.engine.grab_events()
        # Events - die roll, collab effect 1 (decision_send_cheer)
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 4,
            "rigged": True,
        })
        validate_event(self, events[2], EventType.EventType_Decision_SendCheer, self.player1, {
            "effect_player_id": self.player1,
            "amount_min": 1,
            "amount_max": 1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "to_limitation": "backstage",
        })
        backstage_recipient = player1.backstage[0]
        placements = {
            top_cheer["game_card_id"]: backstage_recipient["game_card_id"]
        }
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {
            "placements": placements
        })
        events = self.engine.grab_events()
        # Events - move cheer, back to main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_MoveAttachedCard, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "cheer_deck",
            "to_holomem_id": backstage_recipient["game_card_id"],
            "attached_id": top_cheer["game_card_id"],
        })
        self.assertEqual(len(backstage_recipient["attached_cheer"]), 1)
        self.assertEqual(backstage_recipient["attached_cheer"][0]["game_card_id"], top_cheer["game_card_id"])
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.collab), 1)


    def test_azki_mapinthelefthand_skipuse_get6(self):
        player1 : PlayerState = self.engine.get_player(self.players[0]["player_id"])
        player2 : PlayerState = self.engine.get_player(self.players[1]["player_id"])
        engine = self.engine
        self.assertEqual(engine.active_player_id, self.player1)
        # Has 004 and 2 005 in hand.
        # Center is 003
        # Backstage has 3 003 and 2 004.
        # By default p1 is Azki, p2 is Sora.

        """Azki skill mapinthelefthand"""
        # Azki is p1.
        set_next_die_rolls(self, [6])
        expected_holopower = [player1.deck[0], player1.deck[1], player1.deck[2]]
        expected_holopower.reverse()
        player1.generate_holopower(2)
        add_card_to_hand(self, player1, "hSD01-009") # Roll die collab azki
        player1.archive_holomem_from_play(player1.backstage[0]["game_card_id"])
        player1.move_card(player1.hand[-1]["game_card_id"], "backstage")
        azki_card = player1.backstage[-1]

        top_cheer = player1.cheer_deck[0]
        reset_mainstep(self)
        events = do_collab_get_events(self, player1, azki_card["game_card_id"])
        # Events - holopower gen, oshi skill question
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": azki_card["game_card_id"],
            "holopower_generated": 1,
        })
        self.assertEqual(len(player1.holopower), 3)
        validate_event(self, events[2], EventType.EventType_Decision_Choice, self.player1, {
            "effect_player_id": self.player1,
        })
        # Choice is to use ability or not, pass.
        engine.handle_game_message(self.player1, GameAction.EffectResolution_MakeChoice, {
            "choice_index": 1
        })
        events = self.engine.grab_events()
        # Events - die roll, collab effect fails so back to main step
        self.assertEqual(len(events), 4)
        validate_event(self, events[0], EventType.EventType_RollDie, self.player1, {
            "effect_player_id": self.player1,
            "die_result": 6,
            "rigged": False,
        })
        validate_event(self, events[2], EventType.EventType_Decision_MainStep, self.player1, {"active_player": self.player1})
        self.assertEqual(len(player1.collab), 1)

if __name__ == '__main__':
    unittest.main()
