import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine
from app.gameengine import EventType
from app.gameengine import GameAction, GamePhase
from app.card_database import CardDatabase


card_db = CardDatabase()

# Load the starter deck from decks/starter_azki.json
decks_path = os.path.join(Path(__file__).parent.parent, "decks")
azki_path = os.path.join(decks_path, "starter_azki.json")
sora_path = os.path.join(decks_path, "starter_sora.json")
with open(azki_path, "r") as f:
    azki_starter = json.load(f)
with open(sora_path, "r") as f:
    sora_starter = json.load(f)

class RandomOverride:
    def __init__(self):
        self.random_values = []
        self.move_cards_to_end = 0

    def randint(self, a, b):
        if self.random_values:
            return self.random_values.pop(0)
        return a

    def choice(self, seq):
        if self.random_values:
            return seq[self.random_values.pop(0)]
        return seq[0]

    def shuffle(self, x):
        if self.move_cards_to_end:
            temp = x[:-self.move_cards_to_end]
            x[:-self.move_cards_to_end] = x[self.move_cards_to_end:]
            x[self.move_cards_to_end:] = temp
            self.move_cards_to_end = 0

class TestGameEngine(unittest.TestCase):

    def setUp(self):
        # This method is called before each test. Use it to set up any common test data.
        self.random_override = RandomOverride()

        self.players = [
            {
                "player_id": "player1",
                "oshi_id": azki_starter["oshi_id"],
                "deck": azki_starter["deck"],
                "cheer_deck": azki_starter["cheer_deck"]
            },
            {
                "player_id": "player2",
                "oshi_id": sora_starter["oshi_id"],
                "deck": sora_starter["deck"],
                "cheer_deck": sora_starter["cheer_deck"]
            }
        ]

        self.player1 = self.players[0]["player_id"]
        self.player2 = self.players[1]["player_id"]

        self.engine = GameEngine(card_db, "versus", self.players)
        self.engine.set_random_test_hook(self.random_override)

    def validate_event(self, event, event_type, event_player_id, event_data):
        self.assertEqual(event["event_type"], event_type)
        self.assertEqual(event["event_player_id"], event_player_id)
        for key, value in event_data.items():
            self.assertEqual(event[key], value)

    def get_game_card(self, player_id, index):
        return self.engine.get_player(player_id).hand[index]["game_card_id"]

    def test_basic_game_flow(self):
        self.engine.begin_game()
        self.assertEqual(self.engine.starting_player_id, self.players[0]["player_id"])

        player1 = self.engine.get_player(self.players[0]["player_id"])
        player2 = self.engine.get_player(self.players[1]["player_id"])

        events = self.engine.grab_events()
        # Beginning game events are:
        # - Game start
        # - Initial draw player 1
        # - Initial draw player 2
        # - Mulligan ask to player 1
        # Events are all doubled since both players have a version.
        self.assertEqual(len(events), 8)
        self.validate_event(events[0], EventType.EventType_GameStartInfo, self.player1, {"your_id": self.player1 })
        self.validate_event(events[1], EventType.EventType_GameStartInfo, self.player2, {"your_id": self.player2 })
        self.validate_event(events[2], EventType.EventType_Draw, self.player1, {"drawing_player_id": self.player1})
        self.validate_event(events[3], EventType.EventType_Draw, self.player2, {"drawing_player_id": self.player1})
        self.validate_event(events[4], EventType.EventType_Draw, self.player1, {"drawing_player_id": self.player2})
        self.validate_event(events[5], EventType.EventType_Draw, self.player2, {"drawing_player_id": self.player2})
        self.validate_event(events[6], EventType.EventType_MulliganDecision, self.player1, {"active_player": self.player1 })
        self.validate_event(events[7], EventType.EventType_MulliganDecision, self.player2, {"active_player": self.player1 })

        # Player 1 mulligan choice.
        # Make it so the cards we put back on top are "Shuffled" to the back.
        self.random_override.move_cards_to_end = 7
        self.engine.handle_game_message(self.player1, GameAction.Mulligan, {"do_mulligan": True })
        events = self.engine.grab_events()
        # After calling a mulligan, the following events occur.
        # - (Skip 1 Mulligan reveal event since this wasn't forced)
        # - 7 cards being put back.
        # - 1 Shuffle event
        # - 1 draw 7 more.
        # - 1 Mulligan ask to player 2
        # That's 10 total, for 20 events
        self.assertEqual(len(events), 20)

        # P2 choice
        self.engine.handle_game_message(self.player2, GameAction.Mulligan, {"do_mulligan": False })
        events = self.engine.grab_events()
        # After no mulligan, we get:
        # - Initial placement of holomems
        self.assertEqual(len(events), 2)
        self.validate_event(events[0], EventType.EventType_InitialPlacementBegin, self.player1, {})

        # With no shuffling, p1 mulligan should get us starting at card index 8.
        # Validate the hand:
        #"hSD01-005": 3,
        #"hSD01-006": 2,
        #"hSD01-007": 2,
        hand_card_ids = []
        for card in self.engine.player_states[0].hand:
            hand_card_ids.append(card["card_id"])
        expected_ids = ["hSD01-005", "hSD01-005", "hSD01-005", "hSD01-006", "hSD01-006", "hSD01-007", "hSD01-007"]
        self.assertListEqual(hand_card_ids, expected_ids)
        # 005 is bloom 1 sora
        # 006 is bloom 1 sora
        # 007 is debut irys, so we can place 1 in center and 1 in back.
        center = self.get_game_card(self.player1, 5)
        back = [self.get_game_card(self.player1, 6)]
        self.engine.handle_game_message(self.player1, GameAction.InitialPlacement, {
            "center_holomem_card_id": center,
            "backstage_holomem_card_ids":back,
        })
        events = self.engine.grab_events()
        # P1 placed their units, event:
        # - Initial placement of holomems for p1
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_InitialPlacementPlaced, self.player1, {"active_player": self.player1})
        self.validate_event(events[2], EventType.EventType_InitialPlacementBegin, self.player1, {"active_player": self.player2})
        self.assertEqual(len(player1.hand), 5)

        # Place p2 units.
        # P2's hand is 4 003s, and 3 004s. Both are debut soras
        hand_card_ids = []
        for card in player2.hand:
            hand_card_ids.append(card["card_id"])
        expected_ids = ["hSD01-003", "hSD01-003", "hSD01-003", "hSD01-003", "hSD01-004", "hSD01-004", "hSD01-004"]
        self.assertListEqual(hand_card_ids, expected_ids)
        center = self.get_game_card(self.player2, 0)
        back = [self.get_game_card(self.player2, 1), self.get_game_card(self.player2, 2),
                self.get_game_card(self.player2, 3), self.get_game_card(self.player2, 4),
                self.get_game_card(self.player2, 5)]
        # Should be able to put 6 units out!
        self.engine.handle_game_message(self.player2, GameAction.InitialPlacement, {
            "center_holomem_card_id": center,
            "backstage_holomem_card_ids":back,
        })
        events = self.engine.grab_events()
        # The game has started.
        # Events:
        # - p2's placement
        # - placement reveals
        # - Turn start event for p1
        # - P1's turn draw
        # - P1's cheer choice
        self.assertEqual(len(events), 10)
        self.assertEqual(self.engine.phase, GamePhase.PlayerTurn)



if __name__ == '__main__':
    unittest.main()
