from typing import List, Dict, Any
from app.card_database import CardDatabase
import random

UNKNOWN_CARD_ID = "HIDDEN"
STARTING_HAND_SIZE = 7
MAX_MEMBERS_ON_STAGE = 6

class GamePhase:
    Initializing = "Initializing"
    Mulligan = "Mulligan"
    InitialPlacement = "InitialPlacement"
    PlayerTurn = "PlayerTurn"
    GameOver = "gameover"

class GameAction:
    Mulligan = "mulligan"
    MulliganActionFields = {
        "do_mulligan": bool,
    }

    InitialPlacement = "initial_placement"
    InitialPlacementActionFields = {
        "center_holomem_card_id": str,
        "backstage_holomem_card_ids": List[str],
    }

    ChooseNewCenter = "choose_new_center"
    ChooseNewCenterActionFields = {
        "new_center_card_id": str,
    }

    PlaceCheer = "place_cheer"
    PlaceCheerActionFields = {
        # A dict of all cheer placed with its target id.
        "placements": Dict[str, str],
    }

class PlayerState:
    def __init__(self, card_db:CardDatabase, player_info:Dict[str, Any], engine: 'GameEngine'):
        self.engine = engine
        self.player_id = player_info["player_id"]

        self.first_turn = True
        self.collabed_this_turn = False
        self.mulligan_completed = False
        self.mulligan_count = 0
        self.initial_placement_completed = False
        self.life = []
        self.hand = []
        self.archive = []
        self.backstage = []
        self.center = []
        self.collab = []
        self.holopower = []
        self.oshi_skills_used_this_turn = []
        self.oshi_skills_used_this_game = []
        self.used_limited_this_turn = False

        # Set up Oshi.
        self.oshi_id = player_info["oshi_id"]
        self.oshi_card = card_db.get_card_by_id(self.oshi_id)

        self.deck_list = player_info["deck"]
        # Generate unique cards for all cards in the deck.
        self.deck = []
        card_number = 1
        for card_id, count in self.deck_list.items():
            card = card_db.get_card_by_id(card_id)
            for _ in range(count):
                generated_card = card.copy()
                generated_card["game_card_id"] = self.player_id + "_" + str(card_number)
                generated_card["played_this_turn"] = False
                generated_card["bloomed_this_turn"] = False
                generated_card["attached_cards"] = []
                generated_card["stacked_cards"] = []
                generated_card["damage"] = 0
                generated_card["resting"] = False
                card_number += 1
                self.deck.append(generated_card)

        self.cheer_deck_list = player_info["cheer_deck"]
        # Generate unique cards for all cards in the cheer deck.
        self.cheer_deck = []
        card_number = 1001
        for card_id, count in player_info["cheer_deck"].items():
            card = card_db.get_card_by_id(card_id)
            for _ in range(count):
                generated_card = card.copy()
                generated_card["game_card_id"] = self.player_id + "_" + str(card_number)
                card_number += 1
                self.cheer_deck.append(generated_card)

        self.game_cards_map = {card["game_card_id"]: card["card_id"] for card in self.deck + self.cheer_deck}

    def initialize_life(self):
        # Move cards from the cheer deck to the life area equal to the oshi's life.
        self.life = self.cheer_deck[:self.oshi_card["life"]]
        # Remove them from the cheer deck.
        self.cheer_deck = self.cheer_deck[self.oshi_card["life"]:]

    def draw(self, amount: int):
        # Draw from the top starting at 0.
        amount = min(amount, len(self.deck))
        drawn_cards = self.deck[:amount]
        self.hand += drawn_cards
        self.deck = self.deck[amount:]

        draw_event = {
            "event_type": "draw",
            "drawing_player_id": self.player_id,
            "hidden_info_player": self.player_id,
            "hidden_info_fields": ["drawn_card_ids"],
            "drawn_card_ids": ids_from_cards(drawn_cards),
            "deck_count": len(self.deck),
            "hand_count": len(self.hand),
        }
        self.engine.broadcast_event(draw_event)

    def mulligan(self):
        self.mulligan_count += 1

        # Move cards from hand to deck.
        self.deck += self.hand
        self.hand = []

        # Shuffle.
        self.engine.shuffle_list(self.deck)

        # Draw new hand, don't ever let them draw 0 and lose.
        draw_amount = max(STARTING_HAND_SIZE - (self.mulligan_count - 1), 1)
        self.draw(draw_amount)

    def complete_mulligan(self):
        self.mulligan_completed = True

    def add_to_deck(self, card, top: bool):
        if top:
            self.deck.insert(0, card)
        else:
            self.deck.append(card)

    def are_cards_in_hand(self, card_ids):
        hand_card_ids = ids_from_cards(self.hand)
        for card_id in card_ids:
            if card_id not in hand_card_ids:
                return False
        return True

    def get_card_from_hand(self, card_id):
        for card in self.hand:
            if card["game_card_id"] == card_id:
                return card
        return None

    def get_holomem_on_stage(self):
        return self.center + self.backstage + self.collab

    def find_card(self, card_id):
        for zone in [self.hand, self.archive, self.backstage, self.center, self.collab, self.deck, self.cheer_deck, self.holopower]:
            for card in zone:
                if card["game_card_id"] == card_id:
                    zone_name = zone.__class__.__name__.lower()
                    return card, zone, zone_name
        return None

    def find_and_remove_card(self, card_id):
        card, zone, zone_name = self.find_card(card_id)
        if card:
            zone.remove(card)
        return card, zone_name

    def move_card(self, card_id, to_zone, zone_card_id=""):
        card, from_zone = self.find_and_remove_card(card_id)

        if to_zone == "center":
            self.center.append(card)
        elif to_zone == "backstage":
            self.backstage.append(card)
        elif to_zone == "holomem":
            holomem_card, _, _ = self.find_card(zone_card_id)
            attach_card(card, holomem_card)

        if to_zone in ["center", "backstage", "holomem"] and from_zone == "hand":
            card["played_this_turn"] = True

        move_card_event = {
            "event_type": "move_card",
            "moving_player_id": self.player_id,
            "from_zone": from_zone,
            "to_zone": to_zone,
            "zone_card_id": zone_card_id,
            "card_id": card_id,
        }
        self.engine.broadcast_event(move_card_event)

    def active_resting_cards(self):
        # For each card in the center, backstage, and collab zones, check if they are resting.
        # If so, set resting to false.
        activated_card_ids = []
        for card in self.center + self.backstage + self.collab:
            if is_card_resting(card):
                card["resting"] = False
                activated_card_ids.append(card["game_card_id"])
        return activated_card_ids

    def reset_collab(self):
        # For all cards in collab, move them back to backstage and rest them.
        rested_card_ids = []
        for card in self.collab:
            self.backstage.append(card)
            card["resting"] = True
            rested_card_ids.append(card["game_card_id"])
        self.collab = []
        return rested_card_ids


def ids_from_cards(cards):
    return [card["game_card_id"] for card in cards]

def is_card_resting(card):
    return "resting" in card and card["resting"]

def attach_card(attaching_card, target_card):
    target_card["attached_cards"].append(attaching_card)

def is_card_limited(card):
    return "limited" in card and card["limited"]

class GameEngine:
    def __init__(self,
        card_db:CardDatabase,
        game_type : str,
        player_infos : List[Dict[str, Any]],
    ):
        self.phase = GamePhase.Initializing
        self.first_turn = True
        self.card_db = card_db
        self.latest_events = []
        self.current_decision = None

        self.seed = random.randint(0, 2**32 - 1)
        self.game_type = game_type
        self.player_ids = [player_info["player_id"] for player_info in player_infos]
        self.player_states = [PlayerState(card_db, player_info, self) for player_info in player_infos]
        self.starting_player_id = None

        # Combine all game card mappings into a single dict.
        self.all_game_cards_map = {}
        for player_state in self.player_states:
            self.all_game_cards_map.update(player_state.game_cards_map)

    def grab_events(self):
        events = self.latest_events
        self.latest_events = []
        return events

    def get_player(self, player_id:str):
        return self.player_states[self.player_ids.index(player_id)]

    def other_player(self, player_id:str):
        return self.player_states[1 - self.player_ids.index(player_id)]

    def shuffle_list(self, lst):
        self.random_gen.shuffle(lst)

    def random_pick_list(self, lst):
        return self.random_gen.choice(lst)

    def switch_active_player(self):
        self.active_player_id = self.other_player(self.active_player_id).player_id

    def begin_game(self):
        # Set the seed.
        self.random_gen = random.Random(self.seed)

        # Shuffle decks.
        for player_state in self.player_states:
            self.shuffle_list(player_state.deck)
            self.shuffle_list(player_state.cheer_deck)

        # Determine first player.
        self.starting_player_id = self.random_pick_list(self.player_ids)

        # Send initial game info.
        for player_state in self.player_states:
            player_id = player_state.player_id
            self.send_event({
                "event_player_id": player_id,
                "event_type": "game_start_info",
                "starting_player": self.starting_player_id,
                "your_id": player_id,
                "game_card_map": self.all_game_cards_map,
            })

        # Draw starting hands
        for player_state in self.player_states:
            player_state.draw(STARTING_HAND_SIZE)

        self.phase = GamePhase.Mulligan
        self.active_player_id = self.starting_player_id

        self.handle_mulligan_phase()

    def handle_mulligan_phase(self):
        # Process any forced mulligans.
        while True:
            forced_mulligan = self.check_forced_mulligans()
            if not forced_mulligan:
                break

        # Are both players done mulliganing?
        # If so, move on to the next phase.
        if all(player_state.mulligan_completed for player_state in self.player_states):
            self.begin_initial_placement()
        else:
            # Tell the active player we're waiting on them to mulligan.
            decision_event = {
                "event_type": "decision_mulligan",
                "active_player": self.active_player_id,
            }
            self.broadcast_event(decision_event)

    def send_event(self, event):
        self.latest_events.append(event)

    def broadcast_event(self, event):
        hidden_fields = event.get("hidden_info_fields", [])
        hidden_erase = event.get("hidden_info_erase", [])
        for player_state in self.player_states:
            should_sanitize = not (player_state.player_id == event.get("hidden_info_player"))
            new_event = {
                "event_player_id": player_state.player_id,
                **event,
            }
            if should_sanitize:
                for field in hidden_fields:
                    if field in hidden_erase:
                        new_event[field] = None
                    else:
                        # If the field is a single id, replace it.
                        # If it is a list, replace them all.
                        if isinstance(new_event[field], str):
                            new_event[field] = UNKNOWN_CARD_ID
                        elif isinstance(new_event[field], list):
                            new_event[field] = [UNKNOWN_CARD_ID] * len(new_event[field])
            self.latest_events.append(new_event)

    def begin_initial_placement(self):
        self.phase = GamePhase.InitialPlacement
        self.active_player_id = self.starting_player_id

        # The player must now choose their center holomem and any backstage holomems from hand.
        decision_event = {
            "event_type": "decision_initial_placement",
            "active_player": self.active_player_id,
        }
        self.broadcast_event(decision_event)

    def continue_initial_placement(self):
        self.switch_active_player()
        if all(player_state.initial_placement_completed for player_state in self.player_states):

            # Initialize life.
            for player_state in self.player_states:
                player_state.initialize_life()

            # Reveal all oshis, center, and backstage cards.
            reveal_event = {
                "event_type": "reveal_initial_placement",
                "placement_info": [
                    {
                        "player_id": player_state.player_id,
                        "oshi_id": player_state.oshi_id,
                        "center_card_id": player_state.center[0]["game_card_id"],
                        "backstage_card_ids": ids_from_cards(player_state.backstage),
                        "hand_count": len(player_state.hand),
                        "cheer_deck_count": len(player_state.cheer_deck),
                        "life_count": len(player_state.life),
                    }
                    for player_state in self.player_states
                ]
            }
            self.broadcast_event(reveal_event)

            # Move on to the first player's turn.
            self.active_player_id = self.starting_player_id
            self.begin_player_turn()
        else:
            # Tell the active player we're waiting on them to place cards.
            decision_event = {
                "event_type": "decision_initial_placement",
                "active_player": self.active_player_id,
            }
            self.broadcast_event(decision_event)

    def begin_player_turn(self):
        self.phase = GamePhase.PlayerTurn
        active_player = self.get_player(self.active_player_id)

        # Reset Step
        if not self.first_turn:
            # 1. Activate resting cards.
            activated_cards = active_player.active_resting_cards()
            activation_event = {
                "event_type": "reset_step_activate",
                "active_player": self.active_player_id,
                "activated_card_ids": activated_cards,
            }
            self.broadcast_event(activation_event)

            # 2. Move and rest collab.
            rested_cards = active_player.reset_collab()
            reset_collab_event = {
                "event_type": "reset_step_collab",
                "active_player": self.active_player_id,
                "rested_card_ids": rested_cards,
            }
            self.broadcast_event(reset_collab_event)

            # 3. If Center is empty, select a non-resting backstage to be center.
            # If all are resting, select a resting one.
            if not active_player.center:
                new_center_option_ids = []
                for card in active_player.backstage:
                    if not is_card_resting(card):
                        new_center_option_ids.append(card["game_card_id"])
                if not new_center_option_ids:
                    new_center_option_ids = ids_from_cards(active_player.backstage)

                if len(new_center_option_ids) == 1:
                    # No decision to be made.
                    new_center_id = new_center_option_ids[0]
                    active_player.move_card(new_center_id, "center")
                else:
                    decision_event = {
                        "event_type": "decision_choose_new_center",
                        "active_player": self.active_player_id,
                        "center_options": new_center_option_ids,
                    }
                    self.broadcast_event(decision_event)

                    self.current_decision = {
                        "decision_type": "decision_choose_new_center",
                        "decision_player": self.active_player_id,
                        "options": new_center_option_ids,
                        "continuation": self.continue_begin_turn,
                    }

        if self.current_decision:
            # We are waiting on a decision to be made.
            return
        self.continue_begin_turn()

    def continue_begin_turn(self):
        # The Reset Step is over.

        ## Draw Step - draw a card, game over if you have none.
        active_player = self.get_player(self.active_player_id)
        if len(active_player.deck) == 0:
            # Game over, no cards to draw.
            self.end_game(active_player.player_id)
            return

        active_player.draw(1)

        ## Cheer Step
        # Get the top cheer card id and send a decision.
        # Any holomem in center/collab/backstage can be the target.
        top_cheer_card_id = active_player.cheer_deck[0]["game_card_id"]
        target_options = ids_from_cards(active_player.center + active_player.collab + active_player.backstage)

        decision_event = {
            "event_type": "decision_place_cheer",
            "active_player": self.active_player_id,
            "cheer_to_place": [top_cheer_card_id],
            "source": "cheer_deck",
            "options": target_options,
        }
        self.broadcast_event(decision_event)
        self.current_decision = {
            "decision_type": "decision_place_cheer",
            "decision_player": self.active_player_id,
            "cheer_to_place": [top_cheer_card_id],
            "options": target_options,
            "continuation": self.begin_main_step,
        }

        # Always wait for the decision.

    def get_available_actions(self):
        active_player = self.get_player(self.active_player_id)

        # Determine available actions.
        available_actions = []

        # A. Place debut/spot cards.
        on_stage_mems = active_player.get_holomem_on_stage()
        if len(on_stage_mems) < MAX_MEMBERS_ON_STAGE:
            for card in active_player.hand:
                if card["card_type"] in ["holomem_debut", "holomem_spot"]:
                    available_actions.append({
                        "action_type": "place_holomem",
                        "card_id": card["game_card_id"]
                    })

        # B. Bloom
        if not active_player.first_turn:
            for mem_card in on_stage_mems:
                if mem_card["played_this_turn"]:
                    # Can't bloom if played this turn.
                    continue
                if mem_card["bloomed_this_turn"]:
                    # Can't bloom if already bloomed this turn.
                    continue

                target_bloom_level = 0
                if mem_card["card_type"] == "holomem_debut":
                    target_bloom_level = 1
                elif mem_card["card_type"] == "holomem_bloom":
                    target_bloom_level = mem_card["bloom_level"] + 1

                if target_bloom_level > 0:
                    for card in active_player.hand:
                        if card["card_type"] == "holomem_bloom" and card["bloom_level"] == target_bloom_level:
                            # Check the names of the bloom card, at last one must match a name from the base card.
                            if any(name in card["holomem_names"] for name in mem_card["holomem_names"]):
                                # Check the damage, if the bloom version would die, you can't.
                                if mem_card["damage"] < card["hp"]:
                                    available_actions.append({
                                        "action_type": "bloom",
                                        "card_id": card["game_card_id"],
                                        "target_id": mem_card["game_card_id"],
                                    })

        # C. Collab
        # Can't have collabed this turn.
        # Must have a card in deck to move to holopower.
        # Must have a non-resting backstage card.
        if not active_player.collabed_this_turn and len(active_player.deck) > 0:
            for card in active_player.backstage:
                if not is_card_resting(card):
                    available_actions.append({
                        "action_type": "collab",
                        "card_id": card["game_card_id"],
                    })

        # D. Use Oshi skills.
        for oshi_skill in active_player.oshi_card["oshi_skills"]:
            skill_id = oshi_skill["skill_id"]
            if oshi_skill["timing"] != "action":
                continue

            if oshi_skill["limit"] == "once_per_turn" and skill_id in active_player.oshi_skills_used_this_turn:
                continue

            if oshi_skill["limit"] == "once_per_game" and skill_id in active_player.oshi_skills_used_this_game:
                continue

            skill_cost = oshi_skill["cost"]
            if skill_cost > len(active_player.holopower):
                continue

            available_actions.append({
                "action_type": "oshi_skill",
                "skill_cost": skill_cost,
                "skill_id": skill_id,
            })

        # E. Use Support Cards
        for card in active_player.hand:
            if card["card_type"] == "support":
                if is_card_limited(card):
                    if active_player.used_limited_this_turn:
                        continue
                    if self.starting_player_id == active_player.player_id and active_player.first_turn:
                        continue

                available_actions.append({
                    "action_type": "play_support",
                    "card_id": card["game_card_id"],
                })

        # F. Pass the baton
        # If center holomem is not resting, can swap with a back who is not resting by archiving Cheer.
        # Must be able to archive that much cheer.
        center_mem = active_player.center[0]
        baton_cost = center_mem["baton_cost"]
        if not is_card_resting(center_mem) and len(active_player.cheer_deck) >= baton_cost:
            for card in active_player.backstage:
                if not is_card_resting(card):
                    available_actions.append({
                        "action_type": "pass_baton",
                        "center_id": center_mem["game_card_id"],
                        "back_id": card["game_card_id"],
                        "cost": baton_cost,
                    })

        # G. Begin Performance
        if not (self.starting_player_id == active_player.player_id and active_player.first_turn):
            available_actions.append({
                "action_type": "begin_performance",
            })

        # H. End Turn
        available_actions.append({
            "action_type": "end_turn",
        })

        return available_actions

    def begin_main_step(self):

        # Determine available actions.
        available_actions = self.get_available_actions()

        decision_event = {
            "event_type": "decision_main_step",
            "hidden_info_player": self.active_player_id,
            "hidden_info_fields": ["available_actions"],
            "hidden_info_erase": ["available_actions"],
            "active_player": self.active_player_id,
            "available_actions": available_actions,
        }
        self.broadcast_event(decision_event)


    def end_game(self, loser_id):
        self.phase = GamePhase.GameOver

        gameover_event = {
            "event_type": "gameover",
            "loser": loser_id,
        }
        self.broadcast_event(gameover_event)

    def perform_mulligan(self, active_player: PlayerState):
        revealed_card_ids = ids_from_cards(active_player.hand)
        mulligan_reveal_event = {
            "event_type": "mulligan_reveal",
            "revealed_card_ids": revealed_card_ids,
        }
        self.broadcast_event(mulligan_reveal_event)

        # Do the mulligan reshuffle/drawing.
        active_player.mulligan()

        # If the player has 1 card and a debut holomem, they are complete.
        if len(active_player.hand) == 1 and active_player.hand[0]["card_type"] == "holomem_debut":
            active_player.complete_mulligan()

        self.switch_active_player()

    def check_forced_mulligans(self):
        # If the player has no debut holomems, they must mulligan.
        active_player = self.get_player(self.active_player_id)
        if active_player.mulligan_completed:
            self.switch_active_player()
        else:
            if not any(card["card_type"] == "holomem_debut" for card in active_player.hand):
                self.perform_mulligan(active_player)
                return True
        return False

    def make_error_event(self, player_id:str, error_id:str, error_message:str):
        return {
            "event_player_id": player_id,
            "event_type": "game_error",
            "error_id": error_id,
            "error_message": error_message,
        }

    def validate_action_fields(self, action_data:dict, expected_fields:dict):
        for field_name, field_type in expected_fields.items():
            if field_name not in action_data:
                return False
            if not isinstance(action_data[field_name], field_type):
                return False

    def handle_game_message(self, player_id:str, action_type:str, action_data: dict):
        match action_type:
            case GameAction.Mulligan:
                return self.handle_mulligan(player_id, action_data)
            case GameAction.InitialPlacement:
                return self.handle_initial_placement(player_id, action_data)
            case GameAction.ChooseNewCenter:
                return self.handle_choose_new_center(player_id, action_data)
            case GameAction.PlaceCheer:
                return self.handle_place_cheer(player_id, action_data)
            case _:
                error_event = self.make_error_event(player_id, "invalid_action", "Invalid action type.")
                return [error_event]

    def validate_mulligan(self, player_id:str, action_data: dict):
        if self.phase != GamePhase.Mulligan:
            self.send_event(self.make_error_event(player_id, "invalid_phase", "Invalid phase for mulligan."))
            return False

        if player_id != self.active_player_id:
            self.send_event(self.make_error_event(player_id, "invalid_player", "Not your turn to mulligan."))
            return False

        if not self.validate_action_fields(action_data, GameAction.MulliganActionFields):
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid mulligan action."))
            return False

        return True

    def handle_mulligan(self, player_id:str, action_data: dict):
        if not self.validate_mulligan(player_id, action_data):
            return

        player_state = self.get_player(player_id)
        do_mulligan = action_data["do_mulligan"]
        if do_mulligan:
            self.perform_mulligan(player_state)
        else:
            player_state.complete_mulligan()
            self.switch_active_player()

        self.handle_mulligan_phase()

    def validate_initial_placement(self, player_id:str, action_data: dict):
        if self.phase != GamePhase.InitialPlacement:
            self.send_event(self.make_error_event(player_id, "invalid_phase", "Invalid phase for initial placement."))
            return False

        if player_id != self.active_player_id:
            self.send_event(self.make_error_event(player_id, "invalid_player", "Not your turn to place cards."))
            return False

        if not self.validate_action_fields(action_data, GameAction.InitialPlacementActionFields):
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid initial placement action."))
            return False

        player_state = self.get_player(player_id)
        center_holomem_card_id = action_data["center_holomem_card_id"]
        backstage_holomem_card_ids = action_data["backstage_holomem_card_ids"]
        chosen_card_ids = [center_holomem_card_id] + backstage_holomem_card_ids

        # These cards must be in hand and unique.
        if not player_state.are_cards_in_hand(chosen_card_ids) or len(set(chosen_card_ids)) != len(chosen_card_ids):
            self.send_event(self.make_error_event(player_id, "invalid_cards", "Invalid cards for initial placement."))
            return False

        # The center must be a debut holomem and the backstage must be debut.
        center_card = player_state.get_card_from_hand(center_holomem_card_id)
        if center_card["card_type"] != "holomem_debut":
            self.send_event(self.make_error_event(player_id, "invalid_center", "Invalid center card for initial placement."))
            return False

        backstage_cards = [player_state.get_card_from_hand(card_id) for card_id in backstage_holomem_card_ids]
        if any(card["card_type"] != "holomem_debut" and card["card_type"] != "holomem_spot" for card in backstage_cards):
            self.send_event(self.make_error_event(player_id, "invalid_backstage", "Invalid backstage cards for initial placement."))
            return False

        return True

    def handle_initial_placement(self, player_id:str, action_data:dict):
        if not self.validate_initial_placement(player_id, action_data):
            return

        player_state = self.get_player(player_id)
        center_holomem_card_id = action_data["center_holomem_card_id"]
        backstage_holomem_card_ids = action_data["backstage_holomem_card_ids"]

        # Move the cards from the player's hand to the center and backstage.
        player_state.move_card(center_holomem_card_id, "center")
        for card_id in backstage_holomem_card_ids:
            player_state.move_card(card_id, "backstage")

        player_state.initial_placement_completed = True

        # Broadcast the event.
        placement_event = {
            "event_type": "initial_placement",
            "hidden_info_player": player_id,
            "hidden_info_fields": ["center_card_id", "backstage_card_ids"],
            "active_player": player_id,
            "center_card_id": center_holomem_card_id,
            "backstage_card_ids": backstage_holomem_card_ids,
            "hand_count": len(player_state.hand),
        }
        self.broadcast_event(placement_event)

        self.continue_initial_placement()

    def validate_choose_new_center(self, player_id:str, action_data:dict):
        # The action_data must have the new center card id.
        # The player_id must match the current_decision decision_player
        # decision_choose_new_center must be the current decision type.
        # The center card id must be in the current_decision options
        # The center card id has to be a card that is in the player's backstage.
        if not self.current_decision:
            self.send_event(self.make_error_event(player_id, "invalid_decision", "No current decision."))
            return False

        if not self.validate_action_fields(action_data, GameAction.ChooseNewCenterActionFields):
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid choose new center action."))
            return False

        if player_id != self.current_decision["decision_player"]:
            self.send_event(self.make_error_event(player_id, "invalid_player", "Not your turn to choose new center."))
            return False

        if self.current_decision["decision_type"] != "decision_choose_new_center":
            self.send_event(self.make_error_event(player_id, "invalid_decision", "Not a choose new center decision."))
            return False

        new_center_card_id = action_data["new_center_card_id"]
        if new_center_card_id not in self.current_decision["options"]:
            self.send_event(self.make_error_event(player_id, "invalid_card", "Invalid new center card."))
            return False

        player_state = self.get_player(player_id)
        if not any(card["game_card_id"] == new_center_card_id for card in player_state.backstage):
            self.send_event(self.make_error_event(player_id, "invalid_card", "New center card not in backstage."))
            return False

        return True

    def call_decision_continuation(self):
        decision_continuation = self.current_decision["continuation"]
        self.current_decision = None
        decision_continuation()

    def handle_choose_new_center(self, player_id:str, action_data:dict):
        if not self.validate_choose_new_center(player_id, action_data):
            return

        player = self.get_player(player_id)
        new_center_card_id = action_data["new_center_card_id"]
        player.move_card(new_center_card_id, "center")

        self.call_decision_continuation()

    def validate_place_cheer(self, player_id:str, action_data:dict):
        # The action_data must have the right fields.
        # The player_id must match the current_decision decision_player
        # decision_place_cheer must be the current decision type.
        if not self.current_decision:
            self.send_event(self.make_error_event(player_id, "invalid_decision", "No current decision."))
            return False

        if not self.validate_action_fields(action_data, GameAction.PlaceCheerActionFields):
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid place cheer action."))
            return False

        if player_id != self.current_decision["decision_player"]:
            self.send_event(self.make_error_event(player_id, "invalid_player", "Not your turn to place cheer."))
            return False

        if self.current_decision["decision_type"] != "decision_place_cheer":
            self.send_event(self.make_error_event(player_id, "invalid_decision", "Not a place cheer decision."))
            return False

        placements = action_data["placements"]
        for cheer_id, target_id in placements.items():
            if cheer_id not in self.current_decision["cheer_to_place"]:
                self.send_event(self.make_error_event(player_id, "invalid_cheer", "Invalid cheer to place."))
                return False
            if target_id not in self.current_decision["options"]:
                self.send_event(self.make_error_event(player_id, "invalid_target", "Invalid target for cheer."))
                return False

        return True

    def handle_place_cheer(self, player_id:str, action_data:dict):
        if not self.validate_place_cheer(player_id, action_data):
            return

        player = self.get_player(player_id)
        placements = action_data["placements"]
        for cheer_id, target_id in placements.items():
            player.move_card(cheer_id, "holomem", target_id)

        self.call_decision_continuation()