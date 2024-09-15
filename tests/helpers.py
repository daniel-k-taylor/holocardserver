import unittest
import os, json
from pathlib import Path
from app.card_database import CardDatabase
from app.gameengine import GameEngine, UNKNOWN_CARD_ID, GameAction, ids_from_cards, GamePhase, EventType, PlayerState
from copy import deepcopy

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

def validate_event(self : unittest.TestCase, event, event_type, event_player_id, event_data):
    self.assertEqual(event["event_type"], event_type)
    self.assertEqual(event["event_player_id"], event_player_id)
    for key, value in event_data.items():
        self.assertEqual(event[key], value)

def validate_actions(self : unittest.TestCase, actions, expected_actions):
    self.assertEqual(len(actions), len(expected_actions))
    for i in range(len(actions)):
        self.assertEqual(actions[i]["action_type"], expected_actions[i])

def do_cheer_step_on_card(self : unittest.TestCase, card):
    engine : GameEngine = self.engine
    active_player = engine.get_player(engine.active_player_id)
    cheer_to_place = active_player.cheer_deck[0]["game_card_id"]
    cheer_placement = {
        cheer_to_place: card["game_card_id"]
    }
    engine.handle_game_message(active_player.player_id, GameAction.PlaceCheer, {"placements": cheer_placement })
    self.assertEqual(card["attached_cheer"][-1]["game_card_id"], cheer_to_place)
    events = engine.grab_events()
    validate_last_event_not_error(self, events)
    return events

def pick_choice(self : unittest.TestCase, player_id, choice_index):
    self.engine.handle_game_message(player_id, GameAction.EffectResolution_MakeChoice, {
        "choice_index": choice_index
    })
    events = self.engine.grab_events()
    return events

def validate_last_event_not_error(self : unittest.TestCase, events):
    self.assertNotEqual(events[-1]["event_type"], EventType.EventType_GameError)

def validate_last_event_is_error(self : unittest.TestCase, events):
    self.assertEqual(events[-1]["event_type"], EventType.EventType_GameError)

def reset_mainstep(self : unittest.TestCase):
    self.assertEqual(self.engine.current_decision["decision_type"], EventType.EventType_Decision_MainStep)
    self.engine.clear_decision()
    self.engine.send_main_step_actions()
    events = self.engine.grab_events()
    # Always return the one with the actions listed in it.
    self.assertEqual(events[-1]["event_type"], EventType.EventType_Decision_MainStep)
    if events[-1]["available_actions"]:
        return events[-1]["available_actions"]
    else:
        return events[-2]["available_actions"]

def reset_performancestep(self : unittest.TestCase):
    self.engine.clear_decision()
    self.engine.send_performance_step_actions()
    events = self.engine.grab_events()
    # Always return the one with the actions listed in it.
    self.assertEqual(events[-1]["event_type"], EventType.EventType_Decision_PerformanceStep)
    if events[-1]["available_actions"]:
        return events[-1]["available_actions"]
    else:
        return events[-2]["available_actions"]

def begin_performance(self : unittest.TestCase):
    self.engine.handle_game_message(self.engine.active_player_id, GameAction.MainStepBeginPerformance, {})
    events = self.engine.grab_events()
    validate_last_event_not_error(self, events)
    actions = reset_performancestep(self)
    return actions

def use_oshi_action(self : unittest.TestCase, skill_id):
    self.engine.handle_game_message(self.engine.active_player_id, GameAction.MainStepOshiSkill, {
        "skill_id": skill_id,
    })
    events = self.engine.grab_events()
    validate_last_event_not_error(self, events)
    return events

def initialize_game_to_third_turn(self : unittest.TestCase, p1deck = None, p2deck = None):
    self.random_override = RandomOverride()

    if not p1deck:
        p1deck = azki_starter
    if not p2deck:
        p2deck = sora_starter

    self.players = [
        {
            "player_id": "player1",
            "oshi_id": p1deck["oshi_id"],
            "deck": p1deck["deck"],
            "cheer_deck": p1deck["cheer_deck"]
        },
        {
            "player_id": "player2",
            "oshi_id": p2deck["oshi_id"],
            "deck": p2deck["deck"],
            "cheer_deck": p2deck["cheer_deck"]
        }
    ]
    self.engine = GameEngine(card_db, "versus", self.players)

    self.player1 = self.players[0]["player_id"]
    self.player2 = self.players[1]["player_id"]
    player1 = self.engine.get_player(self.players[0]["player_id"])
    player2 = self.engine.get_player(self.players[1]["player_id"])

    self.engine.set_random_test_hook(self.random_override)

    self.engine.begin_game()
    self.engine.handle_game_message(self.player1, GameAction.Mulligan, {"do_mulligan": False })
    self.engine.handle_game_message(self.player2, GameAction.Mulligan, {"do_mulligan": False })

    hand_card_ids = []
    for card in self.engine.player_states[0].hand:
        hand_card_ids.append(card["card_id"])

    expected_ids = ["hSD01-003", "hSD01-003", "hSD01-003", "hSD01-003", "hSD01-004", "hSD01-004", "hSD01-004"]
    self.assertListEqual(hand_card_ids, expected_ids)

    hand = ids_from_cards(player1.hand)
    center = hand[0]
    back = hand[1:6]

    # Put out all 6 units
    self.engine.handle_game_message(self.player1, GameAction.InitialPlacement, {
        "center_holomem_card_id": center,
        "backstage_holomem_card_ids":back,
    })

    hand = ids_from_cards(player2.hand)
    center = hand[0]
    back = hand[1:6]

    # Put out all 6 units
    self.engine.handle_game_message(self.player2, GameAction.InitialPlacement, {
        "center_holomem_card_id": center,
        "backstage_holomem_card_ids":back,
    })

    events = do_cheer_step_on_card(self, player1.center[0])
    self.assertGreater(len(events), 1)
    validate_last_event_not_error(self, events)

    # Made it to main step.
    self.engine.handle_game_message(self.player1, GameAction.MainStepEndTurn, {})
    events = do_cheer_step_on_card(self, player2.center[0])
    self.engine.handle_game_message(self.player2, GameAction.MainStepEndTurn, {})
    events = do_cheer_step_on_card(self, player1.center[0])
    self.assertGreater(len(events), 1)
    validate_last_event_not_error(self, events)
    # Now it's the third turn.
    self.assertEqual(self.engine.turn_number, 3)
    self.assertEqual(self.engine.first_turn, False)
    self.assertEqual(self.engine.phase, GamePhase.PlayerTurn)

def do_bloom(self : unittest.TestCase, player : PlayerState, card_id, target_id):
    if target_id in ids_from_cards(player.center):
        zone = player.center
    elif target_id in ids_from_cards(player.backstage):
        zone = player.backstage
    else:
        self.fail("Target ID not found in center or backstage.")

    self.engine.handle_game_message(player.player_id, GameAction.MainStepBloom, {
        "card_id": card_id,
        "target_id": target_id
    })
    events = self.engine.grab_events()
    validate_last_event_not_error(self, events)
    self.assertEqual(len(events), 4) # bloom + mainstep again
    validate_event(self, events[0], EventType.EventType_Bloom, player.player_id, {
        "bloom_player_id": player.player_id,
        "bloom_card_id": card_id,
        "target_card_id": target_id,
        "bloom_from_zone": "hand",
    })
    self.assertTrue(target_id not in ids_from_cards(zone))
    self.assertTrue(card_id in ids_from_cards(zone))
    bloomed_card, _, _ = player.find_card(card_id)
    self.assertTrue(target_id in ids_from_cards(bloomed_card["stacked_cards"]))


def do_collab_get_events(self : unittest.TestCase, player : PlayerState, card_id):
    self.engine.handle_game_message(player.player_id, GameAction.MainStepCollab, {
        "card_id": card_id
    })
    events = self.engine.grab_events()
    return events

def add_card_to_hand(self : unittest.TestCase, player : PlayerState, card_definition_id, reset_main=True):
    # card_definition is like the 005 number.
    found_card = None
    for card in player.deck:
        if card["card_id"] == card_definition_id:
            found_card = card
            break

    if not found_card:
        self.fail("Card not found in deck.")

    player.deck.remove(found_card)
    player.hand.append(found_card)
    if reset_main:
        reset_mainstep(self)
    return found_card

def end_turn(self : unittest.TestCase):
    active_player_id = self.engine.active_player_id
    self.engine.handle_game_message(active_player_id, GameAction.MainStepEndTurn, {})
    events = self.engine.grab_events()
    validate_last_event_not_error(self, events)
    self.assertTrue(self.engine.active_player_id != active_player_id)
    return events

def set_next_die_rolls(self : unittest.TestCase, rolls):
    self.random_override.random_values = rolls

def put_card_in_play(self, player : PlayerState, card_id, location):
    card = add_card_to_hand(self, player, card_id, reset_main=False)
    player.hand.remove(card)
    location.append(card)
    card["played_this_turn"] = False
    reset_mainstep(self)
    return card

def spawn_cheer_on_card(self, player : PlayerState, card_id, cheer_color, desired_game_card_id):
    card_db = self.engine.card_db
    match cheer_color:
        case "white":
            spawn_id = "hY01-001"
        case "green":
            spawn_id = "hY02-001"
        case "red":
            spawn_id = "hY03-001"
        case "blue":
            spawn_id = "hY04-001"
        case _:
            self.fail("Invalid cheer color.")

    card = card_db.get_card_by_id(spawn_id)
    cheer_card = deepcopy(card)
    cheer_card["owner_id"] = player.player_id
    cheer_card["game_card_id"] = player.player_id + "_" + desired_game_card_id

    if card_id == "archive":
        player.archive.insert(0, cheer_card)
    else:
        found_card, _, _ = player.find_card(card_id)
        found_card["attached_cheer"].append(cheer_card)

    return cheer_card

def generate_deck_with(oshi_id, cards : dict[str, int] = [], cheer = []):
    new_deck = deepcopy(sora_starter)
    if oshi_id:
        new_deck["oshi_id"] = oshi_id
    if cheer:
        new_deck["cheer_deck"] = cheer

    if cards:
        new_card_count = 0
        for card_id, count in cards.items():
            new_card_count += count
        deck = new_deck["deck"]
        # Remove cards from the end of the existing deck then add these to the end.
        removed_count = 0
        while removed_count < new_card_count:
            # Get the last item in the dictionary.
            card_id = list(deck.keys())[-1]
            count_in_deck = deck[card_id]
            remaining_to_remove = new_card_count - removed_count
            if count_in_deck > remaining_to_remove:
                deck[card_id] = count_in_deck - remaining_to_remove
                removed_count += remaining_to_remove
            else:
                removed_count += count_in_deck
                del deck[card_id]

        # Now add these cards to the end.
        for card_id, count in cards.items():
            deck[card_id] = count

    return new_deck
