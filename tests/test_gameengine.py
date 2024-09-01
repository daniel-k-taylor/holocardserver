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

    def validate_actions(self, actions, expected_actions):
        self.assertEqual(len(actions), len(expected_actions))
        for i in range(len(actions)):
            self.assertEqual(actions[i]["action_type"], expected_actions[i])

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
        self.assertEqual(len(player1.hand), 6)
        self.assertEqual(len(player1.center), 1)
        self.assertEqual(len(player1.backstage), 1)
        self.assertEqual(len(player2.center), 1)
        self.assertEqual(len(player2.backstage), 5)
        self.validate_event(events[8], EventType.EventType_CheerStep, self.player1, { "active_player": self.player1, })
        cheer_event = events[8]
        self.assertEqual(len(cheer_event['options']), 2)
        self.assertEqual(cheer_event['options'][0], player1.center[0]["game_card_id"])
        self.assertEqual(cheer_event['options'][1], player1.backstage[0]["game_card_id"])
        self.assertEqual(len(cheer_event["cheer_to_place"]), 1)
        self.assertEqual(cheer_event["cheer_to_place"][0], player1.cheer_deck[0]["game_card_id"])
        # Give the cheer to our center.
        cheer_to_place = player1.cheer_deck[0]["game_card_id"]
        cheer_placement = {
            cheer_event["cheer_to_place"][0]: player1.center[0]["game_card_id"]
        }
        self.engine.handle_game_message(self.player1, GameAction.PlaceCheer, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Expected events:
        # - Cheer placed
        # - Main step start
        # - Turn start event with available actions
        self.assertEqual(len(events), 6)
        self.validate_event(events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "cheer_deck",
            "to_zone": "holomem",
            "zone_card_id": player1.center[0]["game_card_id"],
            "card_id": cheer_to_place
        })
        self.validate_event(events[2], EventType.EventType_MainStepStart, self.player1, { "active_player": self.player1 })
        self.assertEqual(player1.center[0]["attached_cards"][0]["game_card_id"], cheer_to_place)
        self.validate_event(events[4], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        actions = events[4]["available_actions"]
        # Expected actions
        # + 1 placement, we drew an azki 008
        # Can't bloom on first turn (and only irys in play anyway)
        # + Can collab, 1 choice
        # Can't oshi, no holopower
        # No support in hand
        # +Can baton pass
        # - can't perform on first turn!
        # +Can end turn
        self.assertEqual(len(actions), 4)
        self.assertEqual(actions[0]["action_type"], GameAction.MainStepPlaceHolomem)
        self.assertEqual(actions[1]["action_type"], GameAction.MainStepCollab)
        self.assertEqual(actions[2]["action_type"], GameAction.MainStepBatonPass)
        self.assertEqual(actions[3]["action_type"], GameAction.MainStepEndTurn)

        self.engine.handle_game_message(self.player1, GameAction.MainStepEndTurn, {})
        events = self.engine.grab_events()
        # Expected events:
        # - Turn end event
        # - Turn start event for p2
        #    First turn, skip reset activate/collab
        # - P2's turn draw
        # - P2's cheer choice
        self.assertEqual(len(events), 8)
        self.validate_event(events[0], EventType.EventType_EndTurn, self.player1, { "ending_player_id": self.player1, "next_player_id": self.player2 })
        self.validate_event(events[2], EventType.EventType_TurnStart, self.player1, { "active_player": self.player2, "turn_count": 2 })
        self.validate_event(events[4], EventType.EventType_Draw, self.player1, { "drawing_player_id": self.player2 })
        self.validate_event(events[6], EventType.EventType_CheerStep, self.player1, { "active_player": self.player2 })
        # Give the cheer to the center.
        cheer_event = events[7]
        self.assertEqual(cheer_event["cheer_to_place"][0], player2.cheer_deck[0]["game_card_id"])
        # Give the cheer to our center.
        cheer_to_place = player2.cheer_deck[0]["game_card_id"]
        cheer_placement = {
            cheer_event["cheer_to_place"][0]: player2.center[0]["game_card_id"]
        }
        self.engine.handle_game_message(self.player2, GameAction.PlaceCheer, {"placements": cheer_placement })
        events = self.engine.grab_events()
        # Expected events:
        # - Cheer placed
        # - Main step start
        # - Turn start event with available actions
        self.assertEqual(len(events), 6)
        actions = events[5]["available_actions"]
        # Actions - 5 collabs, baton pass, performance, end turn = 8
        self.assertEqual(len(actions), 8)
        # Let's collab with one of the 004's that have the +20 center collab power.
        collab_card = player2.backstage[3]["game_card_id"]
        self.assertEqual(player2.backstage[3]["card_id"], "hSD01-004")
        self.engine.handle_game_message(self.player2, GameAction.MainStepCollab, {"card_id": collab_card })
        events = self.engine.grab_events()
        # Events: Collab and back to main step
        self.assertEqual(len(events), 4)
        self.validate_event(events[1], EventType.EventType_Collab, self.player2, {
            "collab_player_id": self.player2,
            "collab_card_id": collab_card,
            "holopower_generated": 1,
            })
        self.validate_event(events[3], EventType.EventType_Decision_MainStep, self.player2, { "active_player": self.player2 })
        actions = events[3]["available_actions"]
        # Same as before minus collab actions + oshi skill costs 1 and is available.
        self.assertEqual(len(actions), 4)
        self.validate_actions(actions, [GameAction.MainStepOshiSkill, GameAction.MainStepBatonPass, GameAction.MainStepBeginPerformance, GameAction.MainStepEndTurn])
        self.engine.handle_game_message(self.player2, GameAction.MainStepBeginPerformance, {})
        events = self.engine.grab_events()
        # Events - performance step and actions
        self.assertEqual(len(events), 4)
        self.validate_event(events[1], EventType.EventType_PerformanceStepStart, self.player2, { "active_player": self.player2 })
        self.validate_event(events[3], EventType.EventType_Decision_PerformanceStep, self.player2, { "active_player": self.player2 })
        actions = events[3]["available_actions"]
        self.validate_actions(actions, [GameAction.PerformanceStepUseArt, GameAction.PerformanceStepEndTurn])
        # Validate the perform art
        self.assertEqual(actions[0]["performer_id"], player2.center[0]["game_card_id"])
        self.assertEqual(actions[0]["art_id"], "nunnun")
        self.assertEqual(actions[0]["power"], 30)
        self.assertEqual(len(actions[0]["valid_targets"]), 1)
        self.assertEqual(actions[0]["valid_targets"][0], player1.center[0]["game_card_id"])
        # DO it
        self.assertEqual(player1.center[0]["hp"], 50)
        top_p1_life_before_attack = player1.life[0]["game_card_id"]
        p1_center_before_attack = player1.center[0]
        cheer_on_center = player1.center[0]["attached_cards"][0]["game_card_id"]
        self.engine.handle_game_message(self.player2, GameAction.PerformanceStepUseArt, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": "nunnun",
            "target_id": player1.center[0]["game_card_id"]
        })
        events = self.engine.grab_events()
        # Events = stat boost from effect, performance, player 1's mem died, so distribute cheer decision.
        self.assertEqual(len(events), 6)
        self.validate_event(events[0], EventType.EventType_BoostStat, self.player1, {
            "card_id": player2.center[0]["game_card_id"],
            "stat": "power",
            "amount": 20,
        })
        self.validate_event(events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": player2.center[0]["arts"][0]["art_id"],
            "target_id": p1_center_before_attack["game_card_id"],
            "power": 50, # 30 art + 20 from collab
            "died": True, # Irys only had 50 hp
            "game_over": False,
        })
        self.validate_event(events[2], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player2.center[0]["game_card_id"],
            "art_id": player2.center[0]["arts"][0]["art_id"],
            "target_id": p1_center_before_attack["game_card_id"],
            "power": 50, # 30 art + 20 from collab
            "died": True, # Irys only had 50 hp
            "game_over": False,
        })
        self.validate_event(events[5], EventType.EventType_Decision_MoveCheerChoice, self.player2, {
            "event_player_id": self.player2,
            "amount_min": 1,
            "amount_max": 1,
            "from_life_pool": True,
        })
        available_cheer = events[5]["available_cheer"]
        available_targets = events[5]["available_targets"]
        self.assertEqual(len(available_cheer), 1)
        self.assertEqual(available_cheer[0], top_p1_life_before_attack)
        self.assertEqual(len(available_targets), 1)
        self.assertEqual(available_targets[0], player1.backstage[0]["game_card_id"])
        # Archive should have the irys and a cheer card.
        self.assertEqual(len(player1.archive), 2)
        self.assertEqual(player1.archive[0]["game_card_id"], p1_center_before_attack["game_card_id"])
        self.assertEqual(player1.archive[1]["game_card_id"], cheer_on_center)
        ## Give that cheer to the only choice.
        cheer_placement = {
            top_p1_life_before_attack: player1.backstage[0]["game_card_id"]
        }
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_MoveCheerBetweenHolomems, {"placements": cheer_placement })
        events = self.engine.grab_events()
        self.assertEqual(len(player1.life), 4)
        p1backstage = player1.backstage[0]
        self.assertEqual(p1backstage["attached_cards"][0]["game_card_id"], top_p1_life_before_attack)
        # Events - cheer moved and back to performance step.
        self.assertEqual(len(events), 4)
        self.validate_event(events[2], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player2 })
        actions = events[2]["available_actions"]
        self.assertEqual(len(actions), 1) # Just end turn.
        self.engine.handle_game_message(self.player2, GameAction.PerformanceStepEndTurn, {})
        events = self.engine.grab_events()
        # Events - end turn, start turn, reset step (activate, collab, replace holomem), draw, cheer
        self.assertEqual(len(events), 14)
        self.validate_event(events[0], EventType.EventType_EndTurn, self.player1, {
            "ending_player_id": self.player2,
            "next_player_id": self.player1,
        })
        self.validate_event(events[2], EventType.EventType_TurnStart, self.player1, {
            "active_player": self.player1,
        })
        self.validate_event(events[4], EventType.EventType_ResetStepActivate, self.player1, {
            "active_player": self.player1,
        })
        activated_card_ids = events[4]["activated_card_ids"]
        self.assertEqual(len(activated_card_ids), 0) # Nobody was resting
        self.validate_event(events[6], EventType.EventType_ResetStepCollab, self.player1, {
            "active_player": self.player1,
        })
        rested_card_ids = events[6]["rested_card_ids"]
        self.assertEqual(len(rested_card_ids), 0) # Nobody was collabing
        self.validate_event(events[8], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": p1backstage["game_card_id"],
        })
        self.assertEqual(player1.center[0]["game_card_id"], p1backstage["game_card_id"])
        self.validate_event(events[10], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player1
        })
        self.validate_event(events[12], EventType.EventType_CheerStep, self.player1, { "active_player": self.player1, })

if __name__ == '__main__':
    unittest.main()
