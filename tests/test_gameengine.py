import os
import json
from pathlib import Path
import unittest
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, ids_from_cards
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
        self.move_cards_down = 0

    def randint(self, a, b):
        if self.random_values:
            return self.random_values.pop(0)
        return a

    def choice(self, seq):
        if self.random_values:
            return seq[self.random_values.pop(0)]
        return seq[0]

    def shuffle(self, x : list):
        if self.move_cards_down:
            temp = x[:self.move_cards_down]
            temp.reverse()
            for i in range(self.move_cards_down):
                x.pop(0)
            for i in range(self.move_cards_down):
                x.insert(self.move_cards_down + i, temp[i])


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

    def cheer_step_on_card(self, card):
        active_player = self.engine.get_player(self.engine.active_player_id)
        cheer_to_place = active_player.cheer_deck[0]["game_card_id"]
        cheer_placement = {
            cheer_to_place: card["game_card_id"]
        }
        self.engine.handle_game_message(active_player.player_id, GameAction.PlaceCheer, {"placements": cheer_placement })
        self.assertEqual(card["attached_cards"][-1]["game_card_id"], cheer_to_place)
        events = self.engine.grab_events()
        return events

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
        self.random_override.move_cards_down = 7
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
        events = self.cheer_step_on_card(player1.center[0])
        # Cheer placed and turn start and decision ask
        self.assertEqual(len(events), 6)
        self.assertTrue("available_actions" not in events[5] or not events[5]["available_actions"]) # Hidden from other player
        actions = events[4]["available_actions"]
        self.assertEqual(len(actions), 4) # Place 2 mems, perform, end turn
        # 2 003 sora's in hand as last 2 cards, place both.
        last_hand_id = player1.hand[-1]["game_card_id"]
        self.engine.handle_game_message(self.player1, GameAction.MainStepPlaceHolomem, {
            "card_id": last_hand_id
        })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4) # place mem and back and main decision
        self.validate_event(events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "backstage",
            "card_id": last_hand_id
        })
        self.validate_event(events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        actions = events[2]["available_actions"]
        self.assertEqual(len(actions), 5) # Place 1 more, collab, baton, perform, end turn
        current_center = player1.center[0]["game_card_id"]
        current_backstage = player1.backstage[0]["game_card_id"]
        top_cheer = player1.cheer_deck[0]["game_card_id"]
        # Do baton pass
        self.engine.handle_game_message(self.player1, GameAction.MainStepBatonPass, { "card_id": current_backstage})
        events = self.engine.grab_events()
        # Events - 2 move cards (center to back and back to center), archive a cheer, and main step decision
        self.assertEqual(len(events), 8)
        self.assertEqual(player1.archive[0]["game_card_id"], top_cheer)
        self.assertEqual(player1.center[0]["game_card_id"], current_backstage)
        self.assertEqual(player1.backstage[0]["game_card_id"], current_center)
        self.validate_event(events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "center",
            "to_zone": "backstage",
            "card_id": current_center
        })
        self.validate_event(events[2], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "backstage",
            "to_zone": "center",
            "card_id": current_backstage
        })
        self.validate_event(events[4], EventType.EventType_MoveCheer, self.player1, {
            "owning_player_id": self.player1,
            "from_holomem_id": "deck",
            "to_holomem_id": "archive",
            "cheer_id": top_cheer,
        })
        self.validate_event(events[6], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        actions = events[6]["available_actions"]
        # Actions - place, collab, perform, end turn
        self.assertEqual(len(actions), 4)
        current_backstage = player1.backstage[0]["game_card_id"]
        self.assertEqual(len(player1.holopower), 0)
        # For added testing, let's add some more holopower.
        player1.generate_holopower(3)
        self.assertEqual(len(player1.holopower), 3)
        # Do collab
        self.engine.handle_game_message(self.player1, GameAction.MainStepCollab, {"card_id": current_backstage })
        events = self.engine.grab_events()
        self.assertEqual(len(events), 4) # Collab, IRYS collab effect part 1 decision
        self.validate_event(events[0], EventType.EventType_Collab, self.player1, {
            "collab_player_id": self.player1,
            "collab_card_id": current_backstage,
            "holopower_generated": 1,
        })
        self.assertEqual(events[3]["card_options"][0], UNKNOWN_CARD_ID)
        self.validate_event(events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "hand",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": True,
            "remaining_cards_action": "nothing",
        })
        self.assertEqual(len(events[2]["card_options"]), len(player1.holopower))
        self.assertEqual(len(player1.holopower), 4) # +1 from the collab
        current_holopower_cards = player1.holopower.copy()
        chosen_card = player1.holopower[2]
        # Choose card 2
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardForEffect, {
            "card_ids": ids_from_cards([chosen_card])
        })
        events = self.engine.grab_events()
        # Events - holopower moved to hand, 2nd decision from irys effect.
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "holopower",
            "to_zone": "hand",
            "card_id": chosen_card["game_card_id"]
        })
        self.assertEqual(events[1]["card_id"], chosen_card["game_card_id"]) # p2 can see
        self.validate_event(events[2], EventType.EventType_Decision_ChooseCards, self.player1, {
            "effect_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "holopower",
            "amount_min": 1,
            "amount_max": 1,
            "reveal_chosen": False,
            "remaining_cards_action": "nothing",
        })
        self.assertEqual(len(current_holopower_cards) - 1, len(player1.holopower))
        self.assertTrue(chosen_card["game_card_id"] not in ids_from_cards(player1.holopower))
        self.assertTrue(chosen_card["game_card_id"] in ids_from_cards(player1.hand))
        # Now choose a hand card to send back.
        chosen_card = player1.hand[0]["game_card_id"]
        self.engine.handle_game_message(self.player1, GameAction.EffectResolution_ChooseCardForEffect, {
            "card_ids": [chosen_card]
        })
        events = self.engine.grab_events()
        # Events - hand card moved to holopower, main step decision
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_MoveCard, self.player1, {
            "moving_player_id": self.player1,
            "from_zone": "hand",
            "to_zone": "holopower",
            "card_id": chosen_card
        })
        self.assertEqual(events[1]["card_id"], UNKNOWN_CARD_ID) # p2 card is hidden
        self.validate_event(events[2], EventType.EventType_Decision_MainStep, self.player1, { "active_player": self.player1 })
        self.assertTrue(chosen_card in ids_from_cards(player1.holopower))
        self.assertTrue(chosen_card not in ids_from_cards(player1.hand))
        actions = events[2]["available_actions"]
        # Actions - place what we had before, the new place option, perform, oshi skill, end turn
        self.assertEqual(len(actions), 5)
        # That irys has 2 cheer, one from the life when the first irys died, and one from the cheer step.
        self.assertEqual(len(player1.collab[0]["attached_cards"]), 2)
        # Begin performance
        self.engine.handle_game_message(self.player1, GameAction.MainStepBeginPerformance, {})
        events = self.engine.grab_events()
        # Events - performance step start and decision
        actions = events[2]["available_actions"]
        self.assertEqual(len(actions), 2) # Perform with irys in collab slot or end turn
        self.engine.handle_game_message(self.player1, GameAction.PerformanceStepUseArt, {
            "performer_id": player1.collab[0]["game_card_id"],
            "art_id": "embodimentofhope",
            "target_id": player2.collab[0]["game_card_id"]
        })
        events = self.engine.grab_events()
        # Events - performance result, performance decision step
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_PerformArt, self.player1, {
            "performer_id": player1.collab[0]["game_card_id"],
            "art_id": "embodimentofhope",
            "target_id": player2.collab[0]["game_card_id"],
            "power": 20,
            "died": False, # Only does 20 of 50 hp
            "game_over": False,
        })
        self.validate_event(events[2], EventType.EventType_Decision_PerformanceStep, self.player1, { "active_player": self.player1 })
        self.assertEqual(player2.collab[0]["damage"], 20)
        self.assertEqual(player2.collab[0]["hp"], 50)
        # Actions - only end turn left
        actions = events[2]["available_actions"]
        self.assertEqual(len(actions), 1)
        # End the turn.
        self.engine.handle_game_message(self.player1, GameAction.PerformanceStepEndTurn, {})
        events = self.engine.grab_events()
        # Events - end turn, turn start, reset step (activate resters, collab resting), draw, cheer
        self.assertEqual(len(events), 12)
        self.validate_event(events[0], EventType.EventType_EndTurn, self.player1, {
            "ending_player_id": self.player1,
            "next_player_id": self.player2,
        })
        self.validate_event(events[2], EventType.EventType_TurnStart, self.player1, {
            "active_player": self.player2,
        })
        self.validate_event(events[4], EventType.EventType_ResetStepActivate, self.player1, {
            "active_player": self.player2,
        })
        activated_card_ids = events[4]["activated_card_ids"]
        self.assertEqual(len(activated_card_ids), 0) # Nobody was resting
        self.validate_event(events[6], EventType.EventType_ResetStepCollab, self.player1, {
            "active_player": self.player2,
        })
        rested_card_ids = events[6]["rested_card_ids"]
        self.assertEqual(len(rested_card_ids), 1) # Collab is resting now
        self.assertEqual(len(player2.collab), 0)
        self.assertEqual(player2.backstage[-1]["resting"], True)
        self.assertEqual(player2.backstage[-1]["damage"], 20)
        self.validate_event(events[8], EventType.EventType_Draw, self.player1, {
            "drawing_player_id": self.player2
        })
        self.validate_event(events[10], EventType.EventType_CheerStep, self.player1, { "active_player": self.player2, })
        events = self.cheer_step_on_card(player2.backstage[-1])
        # Events - cheer placed and main step start and decision
        self.assertEqual(len(events), 6)
        actions = events[5]["available_actions"]
        # Actions - place (no space), collab (4, 1 resting), bloom (12 options!) oshi, baton, perform, end turn
        self.assertEqual(len(actions), 20)
        self.validate_actions(actions, [
            GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom,
            GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom,
            GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom, GameAction.MainStepBloom,
            GameAction.MainStepCollab, GameAction.MainStepCollab,GameAction.MainStepCollab,GameAction.MainStepCollab,
            GameAction.MainStepOshiSkill, GameAction.MainStepBatonPass, GameAction.MainStepBeginPerformance, GameAction.MainStepEndTurn])

        # Pick some of the blooms to do.
        # Center is 003 sora, hand 1 and 2 are both 005 bloom 1
        # Backstage rester is 004 sora with 20 damage.
        # Each has 1 cheer attached.
        bloom_target1 = player2.center[0]
        bloom_target_attached1 = ids_from_cards(bloom_target1["attached_cards"])
        self.assertEqual(len(bloom_target_attached1), 1)
        bloom_target2 = player2.backstage[-1]
        bloom_target_attached2 = ids_from_cards(bloom_target2["attached_cards"])
        self.assertEqual(len(bloom_target_attached2), 1)
        bloom_card1 = player2.hand[1]
        bloom_card2 = player2.hand[2]

        # Bloom center.
        self.engine.handle_game_message(self.player2, GameAction.MainStepBloom, {
            "card_id": bloom_card1["game_card_id"],
            "target_id": bloom_target1["game_card_id"]
        })
        events = self.engine.grab_events()
        # Events - bloom, main step decision
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player2,
            "bloom_card_id": bloom_card1["game_card_id"],
            "target_card_id": bloom_target1["game_card_id"],
            "bloom_from_zone": "hand",
        })
        self.assertEqual(bloom_card1["attached_cards"][0]["game_card_id"], bloom_target_attached1[0])
        self.assertEqual(len(bloom_card1["attached_cards"]), 1)
        self.assertEqual(len(bloom_card1["stacked_cards"]), 1)
        self.assertEqual(bloom_card1["stacked_cards"][0]["game_card_id"], bloom_target1["game_card_id"])
        self.assertEqual(len(bloom_target1["attached_cards"]), 0)

        actions = events[3]["available_actions"]
        # Actions - place (no space), collab (4, 1 resting), bloom (down to 5 options) oshi, baton, perform, end turn
        self.assertEqual(len(actions), 13)

        # Bloom That backstager.
        self.engine.handle_game_message(self.player2, GameAction.MainStepBloom, {
            "card_id": bloom_card2["game_card_id"],
            "target_id": bloom_target2["game_card_id"]
        })
        events = self.engine.grab_events()
        # Events - bloom, main step decision
        self.assertEqual(len(events), 4)
        self.validate_event(events[0], EventType.EventType_Bloom, self.player1, {
            "bloom_player_id": self.player2,
            "bloom_card_id": bloom_card2["game_card_id"],
            "target_card_id": bloom_target2["game_card_id"],
            "bloom_from_zone": "hand",
        })
        self.assertEqual(bloom_card2["attached_cards"][0]["game_card_id"], bloom_target_attached2[0])
        self.assertEqual(len(bloom_card2["attached_cards"]), 1)
        self.assertEqual(len(bloom_card2["stacked_cards"]), 1)
        self.assertEqual(bloom_card2["stacked_cards"][0]["game_card_id"], bloom_target2["game_card_id"])
        self.assertEqual(len(bloom_target2["attached_cards"]), 0)
        self.assertEqual(bloom_card2["damage"], 20)
        self.assertTrue(bloom_card2["resting"])
        actions = events[3]["available_actions"]
        # Actions - place (no space), collab (4, 1 resting), bloom (none) oshi, baton, perform, end turn
        self.assertEqual(len(actions), 8)

        # End turn twice and check that our resting is gone.
        self.assertEqual(player2.backstage[-1]["resting"], True)
        self.engine.handle_game_message(self.player2, GameAction.MainStepEndTurn, {})
        events = self.engine.grab_events()
        events = self.cheer_step_on_card(player1.center[0])
        self.engine.handle_game_message(self.player1, GameAction.MainStepEndTurn, {})
        events = self.engine.grab_events()
        self.assertEqual(player2.backstage[-1]["resting"], False)



if __name__ == '__main__':
    unittest.main()
