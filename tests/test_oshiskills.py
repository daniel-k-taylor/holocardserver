import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards, PlayerState
from app.gameengine import EventType
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase
from helpers import RandomOverride, initialize_game_to_third_turn, validate_event, validate_actions, do_bloom, reset_mainstep, add_card_to_hand, do_cheer_step_on_card
from helpers import end_turn

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
        player1.oshi_skills_used_this_game.append("micintherighthand")
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
        player2.oshi_skills_used_this_game.append("replacement")
        player2.oshi_skills_used_this_turn.append("replacement")
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


if __name__ == '__main__':
    unittest.main()
