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

class DecisionType:
    DecisionChoice = "decision_choice"
    DecisionChooseNewCenter = "decision_choose_new_center"
    DecisionPlaceCheer = "decision_place_cheer"
    DecisionMainStep = "decision_main_step"
    DecisionPerformanceStep = "decision_performance_step"
    DecisionEffect_MoveCheerBetweenHolomems = "decision_effect_move_cheer_between_holomems"
    DecisionEffect_ChooseCardForEffect = "decision_choose_card_for_effect"

class EffectType:
    EffectType_AddTurnEffect = "add_turn_effect"
    EffectType_ChooseCard = "choose_card"
    EffectType_Draw = "draw"
    EffectType_MoveCheerBetweenHolomems = "move_cheer_between_holomems"
    EffectType_PowerBoost = "power_boost"
    EffectType_SendCheer = "send_cheer"
    EffectType_SendCollabBack = "send_collab_back"
    EffectType_ShuffleHandToDeck = "shuffle_hand_to_deck"
    EffectType_SwitchCenterWithBack = "switch_center_with_back"


    ### Unimplemented
    #"choose_die_result"
    #"roll_die"
    #"choose_from_deck"
    #"take_from_deck"

class Condition:
    Condition_CardsInHand = "cards_in_hand"
    Condition_CenterIsColor = "center_is_color"
    Condition_CheerInPlay = "cheer_in_play"
    Condition_CollabWith = "collab_with"
    Condition_HolomemOnStage = "holomem_on_stage"
    Condition_TargetColor = "target_color"


class TurnEffectType:
    TurnEffectType_CenterArtsBonus = "center_arts_bonus"

class EventType:
    EventType_Bloom = "bloom"
    EventType_BoostStat = "boost_stat"
    EventType_Choice_SendCollabBack = "choice_send_collab_back"
    EventType_Collab = "collab"
    EventType_Decision_ChooseCard = "decision_choose_card"
    EventType_Decision_MainStep = "decision_main_step"
    EventType_Decision_MoveCheerChoice = "decision_move_cheer_choice"
    EventType_Decision_PerformanceStep = "decision_performance_step"
    EventType_Decision_SwapHolomemToCenter = "decision_choose_holomem_swap_to_center"
    EventType_Draw = "draw"
    EventType_EndTurn = "end_turn"
    EventType_GameStartInfo = "game_start_info"
    EventType_InitialPlacement = "initial_placement"
    EventType_MoveCard = "move_card"
    EventType_MoveCheer = "move_cheer"
    EventType_MulliganDecision = "mulligan_decision"
    EventType_OshiSkillActivation = "oshi_skill_activation"
    EventType_PerformArt = "perform_art"
    EventType_Decision_SendCheer = "decision_send_cheer"

class ArtStatBoosts:
    def __init__(self):
        self.power = 0


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

    MainStepPlaceHolomem = "mainstep_place_holomem"
    MainStepPlaceHolomemFields = {
        "card_id": str,
    }

    MainStepBloom = "mainstep_bloom"
    MainStepBloomFields = {
        "card_id": str,
        "target_id": str,
    }

    MainStepCollab = "mainstep_collab"
    MainStepCollabFields = {
        "card_id": str,
    }

    MainStepOshiSkill = "mainstep_oshi_skill"
    MainStepOshiSkillFields = {
        "skill_id": str,
    }

    MainStepPlaySupport = "mainstep_play_support"
    MainStepPlaySupportFields = {
        "card_id": str,
    }

    MainStepBatonPass = "mainstep_baton_pass"
    MainStepBatonPassFields = {
        "card_id": str,
    }

    MainStepBeginPerformance = "mainstep_begin_performance"
    MainStepBeginPerformanceFields = {}

    MainStepEndTurn = "mainstep_end_turn"
    MainStepEndTurnFields = {}

    PerformanceStepUseArt = "performance_step_use_art"
    PerformanceStepUseArtFields = {
        "performer_id": str,
        "art_id": str,
    }

    PerformanceStepEndTurn = "performance_step_end_turn"
    PerformanceStepEndTurnFields = {}

    EffectResolution_MoveCheerBetweenHolomems = "effect_resolution_move_cheer_between_holomems"
    EffectResolution_MoveCheerBetweenHolomemsFields = {
        # Dict of cheer and target ids.
        "placements": Dict[str, str],
    }

    EffectResolution_ChooseCardForEffect = "effect_resolution_choose_card_for_effect"
    EffectResolution_ChooseCardForEffectFields = {
        "card_id": str,
    }

    EffectResolution_MakeChoice = "effect_resolution_make_choice"
    EffectResolution_MakeChoiceFields = {
        "choice_index": int,
    }

class PlayerState:
    def __init__(self, card_db:CardDatabase, player_info:Dict[str, Any], engine: 'GameEngine'):
        self.engine = engine
        self.player_id = player_info["player_id"]

        self.first_turn = True
        self.baton_pass_this_turn = False
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
        self.turn_effects = []

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
                generated_card["owner_id"] = self.player_id
                generated_card["game_card_id"] = self.player_id + "_" + str(card_number)
                generated_card["played_this_turn"] = False
                generated_card["bloomed_this_turn"] = False
                generated_card["attached_cards"] = []
                generated_card["stacked_cards"] = []
                generated_card["damage"] = 0
                generated_card["resting"] = False
                generated_card["used_art_this_turn"] = False
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
                generated_card["owner_id"] = self.player_id
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
            "event_type": EventType.EventType_Draw,
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
        self.shuffle_hand_to_deck()

        # Draw new hand, don't ever let them draw 0 and lose.
        draw_amount = max(STARTING_HAND_SIZE - (self.mulligan_count - 1), 1)
        self.draw(draw_amount)

    def complete_mulligan(self):
        self.mulligan_completed = True

    def shuffle_hand_to_deck(self):
        for card in self.hand:
            self.move_card(card["game_card_id"], "deck", hidden_info=True)
        self.shuffle_deck()

    def shuffle_deck(self):
        self.engine.shuffle_list(self.deck)
        shuffle_event = {
            "event_type": EffectType.EffectType_ShuffleDeck,
            "shuffling_player_id": self.player_id,
        }
        self.engine.broadcast_event(shuffle_event)

    def get_cheer_ids_on_holomems(self):
        cheer_ids = []
        for card in self.get_holomem_on_stage():
            for attached_card in card["attached_cards"]:
                if attached_card["card_type"] == "cheer":
                    cheer_ids.append(attached_card["game_card"])
        return cheer_ids

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

    def get_holomem_on_stage(self, only_performers = False):
        on_stage = []
        on_stage = self.center + self.collab
        if not only_performers:
            on_stage += self.backstage
        return on_stage

    def find_card(self, card_id):
        for zone in [self.hand, self.archive, self.backstage, self.center, self.collab, self.deck, self.cheer_deck, self.holopower]:
            for card in zone:
                if card["game_card_id"] == card_id:
                    zone_name = zone.__class__.__name__.lower()
                    return card, zone, zone_name
        return None, None, None

    def find_and_remove_card(self, card_id):
        card, zone, zone_name = self.find_card(card_id)
        if card and zone:
            zone.remove(card)
        return card, zone, zone_name

    def move_card(self, card_id, to_zone, zone_card_id="", hidden_info=False):
        card, _, from_zone_name = self.find_and_remove_card(card_id)

        if to_zone == "center":
            self.center.append(card)
        elif to_zone == "backstage":
            self.backstage.append(card)
        elif to_zone == "hand":
            self.hand.append(card)
        elif to_zone == "holomem":
            holomem_card, _, _ = self.find_card(zone_card_id)
            attach_card(card, holomem_card)
        elif to_zone == "holopower":
            self.holopower.insert(0, card)
        elif to_zone == "deck":
            self.deck.insert(0, card)

        if to_zone in ["center", "backstage", "holomem"] and from_zone_name == "hand":
            card["played_this_turn"] = True

        move_card_event = {
            "event_type": EventType.EventType_MoveCard,
            "moving_player_id": self.player_id,
            "from_zone": from_zone_name,
            "to_zone": to_zone,
            "zone_card_id": zone_card_id,
            "card_id": card_id,
        }
        if hidden_info:
            move_card_event["hidden_info_player"] = self.player_id
            move_card_event["hidden_info_fields"] = ["card_id"]
        self.engine.broadcast_event(move_card_event)

    def active_resting_cards(self):
        # For each card in the center, backstage, and collab zones, check if they are resting.
        # If so, set resting to false.
        activated_card_ids = []
        for card in self.get_holomem_on_stage():
            if is_card_resting(card):
                card["resting"] = False
                activated_card_ids.append(card["game_card_id"])
        return activated_card_ids

    def clear_used_art_this_turn(self):
        for card in self.get_holomem_on_stage():
            card["used_art_this_turn"] = False

    def reset_collab(self):
        # For all cards in collab, move them back to backstage and rest them.
        rested_card_ids = []
        for card in self.collab:
            self.backstage.append(card)
            card["resting"] = True
            rested_card_ids.append(card["game_card_id"])
        self.collab = []
        return rested_card_ids

    def return_collab(self):
        # For all cards in collab, move them back to backstage and rest them.
        collab_card_ids = ids_from_cards(self.collab)
        for card_id in collab_card_ids:
            self.move_card(card_id, "backstage")

    def bloom(self, bloom_card_id, target_card_id):
        bloom_card, _, bloom_from_zone_name = self.find_and_remove_card(bloom_card_id)
        target_card, zone, _ = self.find_and_remove_card(target_card_id)

        bloom_card["stacked_cards"].append(target_card)
        # Add any stacked cards on the target to this too.
        bloom_card["stacked_cards"] += target_card["stacked_cards"]
        target_card["stacked_cards"] = []

        bloom_card["attached_cards"] += target_card["attached_cards"]
        target_card["attached_cards"] = []

        bloom_card["bloomed_this_turn"] = True
        bloom_card["damage"] = target_card["damage"]
        bloom_card["resting"] = target_card["resting"]

        # Put the bloom card where the target card was.
        zone.append(bloom_card)

        bloom_event = {
            "event_type": EventType.EventType_Bloom,
            "bloom_player_id": self.player_id,
            "bloom_card_id": bloom_card_id,
            "target_card_id": target_card_id,
            "bloom_from_zone": bloom_from_zone_name,
        }
        self.engine.broadcast_event(bloom_event)

    def generate_holopower(self, amount):
        for _ in range(amount):
            self.holopower.insert(0, self.deck.pop(0))

    def collab_action(self, collab_card_id, continuation):
        # Move the card and generate holopower.
        collab_card, _, _ = self.find_and_remove_card(collab_card_id)
        self.collab.append(collab_card)
        self.collabed_this_turn = True
        self.generate_holopower(1)

        collab_event = {
            "event_type": EventType.EventType_Collab,
            "collab_player_id": self.player_id,
            "collab_card_id": collab_card_id,
            "holopower_generated": 1,
        }
        self.engine.broadcast_event(collab_event)

        # Handle collab effects.
        collab_effects = collab_card["collab_effects"]
        add_card_id_to_effects(collab_effects, collab_card_id)
        self.engine.begin_resolving_effects(collab_effects, continuation)

    def trigger_oshi_skill(self, skill_id):
        oshi_skill = next(skill for skill in self.oshi_card["oshi_skills"] if skill["skill_id"] == skill_id)
        skill_cost = oshi_skill["cost"]

        # Update skill usage.
        self.oshi_skills_used_this_game.append(skill_id)
        self.oshi_skills_used_this_turn.append(skill_id)

        # Remove the cost from holopower to archive.
        for _ in range(skill_cost):
            top_holopower_id = self.holopower[0]["game_card_id"]
            self.move_card(top_holopower_id, "archive")

        oshi_skill_event = {
            "event_type": EventType.EventType_OshiSkillActivation,
            "oshi_player_id": self.player_id,
            "skill_id": skill_id,
        }
        self.engine.broadcast_event(oshi_skill_event)

        # Get skill effects.
        skill_effects = oshi_skill["effects"]
        for effect in skill_effects:
            effect["player_id"] = self.player_id

        return skill_effects

    def find_and_remove_cheer(self, cheer_id):
        previous_holder_id = None
        for card in self.get_holomem_on_stage():
            if cheer_id in ids_from_cards(card["attached_cards"]):
                # Remove the cheer.
                cheer_card = next(card for card in card["attached_cards"] if card["game_card_id"] == cheer_id)
                previous_holder_id = card["game_card_id"]
                card["attached_cards"].remove(cheer_card)
                break
        if not previous_holder_id:
            # Check the life deck.
            if cheer_id in ids_from_cards(self.life):
                cheer_card = next(card for card in self.life if card["game_card_id"] == cheer_id)
                self.life.remove(cheer_card)
                previous_holder_id = "life"
            # And the archive.
            elif cheer_id in ids_from_cards(self.archive):
                cheer_card = next(card for card in self.archive if card["game_card_id"] == cheer_id)
                self.archive.remove(cheer_card)
                previous_holder_id = "archive"
            # And the cheer deck.
            elif cheer_id in ids_from_cards(self.cheer_deck):
                cheer_card = next(card for card in self.cheer_deck if card["game_card_id"] == cheer_id)
                self.cheer_deck.remove(cheer_card)
                previous_holder_id = "cheer_deck"
        return cheer_card, previous_holder_id

    def move_cheer_between_holomems(self, placements):
        for cheer_id, target_id in placements.items():
            # Find and remove the cheer from its current spot.
            cheer_card, previous_holder_id = self.find_and_remove_cheer(cheer_id)

            # Attach to the target.
            target_card = self.find_card(target_id)
            target_card["attached_cards"].append(cheer_card)

            move_cheer_event = {
                "event_type": EventType.EventType_MoveCheer,
                "owning_player_id": self.player_id,
                "from_holomem_id": previous_holder_id,
                "to_holomem_id": target_card["game_card_id"],
                "cheer_id": cheer_id,
            }
            self.engine.broadcast_event(move_cheer_event)

    def archive_cheer(self, cheer_ids):
        for cheer_id in cheer_ids:
            cheer_card, previous_holder_id = self.find_and_remove_cheer(cheer_id)
            self.archive.append(cheer_card)
            move_cheer_event = {
                "event_type": EventType.EventType_MoveCheer,
                "owning_player_id": self.player_id,
                "from_holomem_id": previous_holder_id,
                "to_holomem_id": "archive",
                "cheer_id": cheer_id,
            }
            self.engine.broadcast_event(move_cheer_event)

    def archive_cheer_from_deck(self, amount):
        for _ in range(amount):
            cheer_card = self.cheer_deck.pop(0)
            self.archive.append(cheer_card)
            move_cheer_event = {
                "event_type": EventType.EventType_MoveCheer,
                "owning_player_id": self.player_id,
                "from_holomem_id": "deck",
                "to_holomem_id": "archive",
                "cheer_id": cheer_card["game_card_id"],
            }
            self.engine.broadcast_event(move_cheer_event)

    def archive_holomem_from_play(self, card_id):
        card, _, _ = self.find_and_remove_card(card_id)
        attached_cards = card["attached_cards"]
        stacked_cards = card["stacked_cards"]

        for extra_card in attached_cards + stacked_cards:
            self.archive.insert(0, extra_card)
        self.archive.insert(0, card)

    def swap_center_with_back(self, back_id):
        self.move_card(self.center[0]["game_card_id"], "backstage")
        self.move_card(back_id, "center")

    def add_turn_effect(self, turn_effect):
        self.turn_effects.append(turn_effect)

def ids_from_cards(cards):
    return [card["game_card_id"] for card in cards]

def is_card_resting(card):
    return "resting" in card and card["resting"]

def add_card_id_to_effects(effects, card_id):
    for effect in effects:
        effect["source_card_id"] = card_id

def get_owner_id_from_card_id(card_id):
    return card_id.split("_")[0]

def art_requirement_met(card, art):
    attached_cheer_cards = [attached_card for attached_card in card["attached_cards"] if attached_card["card_type"] == "cheer"]

    white_cheer = 0
    green_cheer = 0
    blue_cheer = 0
    red_cheer = 0

    for attached_cheer_card in attached_cheer_cards:
        if attached_cheer_card["color"] == "white":
            white_cheer += 1
        elif attached_cheer_card["color"] == "green":
            green_cheer += 1
        elif attached_cheer_card["color"] == "blue":
            blue_cheer += 1
        elif attached_cheer_card["color"] == "red":
            red_cheer += 1

    cheer_costs = art["costs"]
    any_cost = 0
    # First go through all the costs and subtract any from the color counts.
    for cost in cheer_costs:
        color_required = cost["color"]
        color_amount = cost["amount"]
        if color_required == "any":
            any_cost += color_amount
        else:
            if color_required == "white":
                white_cheer -= color_amount
            elif color_required == "green":
                green_cheer -= color_amount
            elif color_required == "blue":
                blue_cheer -= color_amount
            elif color_required == "red":
                red_cheer -= color_amount

    # If any cheer is negative, the requirement is not met.
    if white_cheer < 0 or green_cheer < 0 or blue_cheer < 0 or red_cheer < 0:
        return False

    total_cheer_left = white_cheer + green_cheer + blue_cheer + red_cheer
    if total_cheer_left < any_cost:
        return False

    return True

def attach_card(attaching_card, target_card):
    target_card["attached_cards"].append(attaching_card)

def is_card_limited(card):
    return "limited" in card and card["limited"]

def get_effects_at_timing(art_effects, timing):
    return [effect for effect in art_effects if effect["timing"] == timing]

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
        self.effects_to_resolve = []
        self.effect_resolution_continuation = self.blank_continuation
        self.effect_resolution_cleanup_card = None

        self.performance_artstatboosts = ArtStatBoosts()
        self.performance_performer_card = None
        self.performance_target_card = None
        self.performance_art = None
        self.performance_continuation = self.blank_continuation

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
                "event_type": EventType.EventType_GameStartInfo,
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
                "event_type": EventType.EventType_MulliganDecision,
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

    def set_decision(self, new_decision):
        if self.current_decision:
            raise Exception("Decision already set.")
        self.current_decision = new_decision

    def begin_initial_placement(self):
        self.phase = GamePhase.InitialPlacement
        self.active_player_id = self.starting_player_id

        # The player must now choose their center holomem and any backstage holomems from hand.
        decision_event = {
            "event_type": EventType.EventType_InitialPlacement,
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
                "event_type": EventType.EventType_InitialPlacement,
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
                        "event_type": DecisionType.DecisionChooseNewCenter,
                        "active_player": self.active_player_id,
                        "center_options": new_center_option_ids,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionChooseNewCenter,
                        "decision_player": self.active_player_id,
                        "options": new_center_option_ids,
                        "continuation": self.continue_begin_turn,
                    })

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
        if len(active_player.cheer_deck) > 0:
            top_cheer_card_id = active_player.cheer_deck[0]["game_card_id"]
            target_options = ids_from_cards(active_player.center + active_player.collab + active_player.backstage)

            decision_event = {
                "event_type": DecisionType.DecisionPlaceCheer,
                "active_player": self.active_player_id,
                "cheer_to_place": [top_cheer_card_id],
                "source": "cheer_deck",
                "options": target_options,
            }
            self.broadcast_event(decision_event)
            self.set_decision({
                "decision_type": DecisionType.DecisionPlaceCheer,
                "decision_player": self.active_player_id,
                "cheer_to_place": [top_cheer_card_id],
                "options": target_options,
                "continuation": self.begin_main_step,
            })
        else:
            # No cheer left!
            self.begin_main_step()

    def get_available_mainstep_actions(self):
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

                if "play_conditions" in card:
                    for condition in card["play_conditions"]:
                        if not self.is_effect_condition_met(active_player, condition):
                            continue

                play_requirements = {}
                if "play_requirements" in card:
                    play_requirements = card["play_requirements"]

                available_actions.append({
                    "action_type": "play_support",
                    "card_id": card["game_card_id"],
                    "play_requirements": play_requirements,
                })

        # F. Pass the baton
        # If center holomem is not resting, can swap with a back who is not resting by archiving Cheer.
        # Must be able to archive that much cheer.
        center_mem = active_player.center[0]
        baton_cost = center_mem["baton_cost"]
        if not active_player.baton_pass_this_turn and not is_card_resting(center_mem) and len(active_player.cheer_deck) >= baton_cost:
            backstage_options = []
            for card in active_player.backstage:
                if not is_card_resting(card):
                    backstage_options.append(card)["game_card_id"]
            if backstage_options:
                available_actions.append({
                    "action_type": "pass_baton",
                    "center_id": center_mem["game_card_id"],
                    "backstage_options": backstage_options,
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

    def send_main_step_actions(self):
        # Determine available actions.
        available_actions = self.get_available_mainstep_actions()

        decision_event = {
            "event_type": EventType.EventType_Decision_MainStep,
            "hidden_info_player": self.active_player_id,
            "hidden_info_fields": ["available_actions"],
            "hidden_info_erase": ["available_actions"],
            "active_player": self.active_player_id,
            "available_actions": available_actions,
        }
        self.broadcast_event(decision_event)
        self.set_decision({
            "decision_type": DecisionType.DecisionMainStep,
            "decision_player": self.active_player_id,
            "available_actions": available_actions,
            "continuation": self.continue_main_step,
        })

    def begin_main_step(self):
        self.send_main_step_actions()

    def continue_main_step(self):
        self.send_main_step_actions()

    def end_player_turn(self):
        active_player = self.get_player(self.active_player_id)
        active_player.first_turn = False
        active_player.baton_pass_this_turn = False
        active_player.collabed_this_turn = False
        active_player.oshi_skills_used_this_turn = []
        active_player.used_limited_this_turn = False
        active_player.turn_effects = []
        active_player.clear_used_art_this_turn()

        self.first_turn = False

        ending_player_id = self.active_player_id
        self.switch_active_player()

        end_turn_event = {
            "event_type": EventType.EventType_EndTurn,
            "ending_player_id": ending_player_id,
            "next_player_id": self.active_player_id,
        }
        self.broadcast_event(end_turn_event)

        self.begin_player_turn()

    def send_performance_step_actions(self):
        # Determine available actions.
        available_actions = self.get_available_performance_actions()

        decision_event = {
            "event_type": EventType.EventType_Decision_PerformanceStep,
            "active_player": self.active_player_id,
            "available_actions": available_actions,
        }
        self.broadcast_event(decision_event)
        self.set_decision({
            "decision_type": DecisionType.DecisionPerformanceStep,
            "decision_player": self.active_player_id,
            "available_actions": available_actions,
            "continuation": self.continue_performance_step,
        })

    def get_available_performance_actions(self):
        active_player = self.get_player(self.active_player_id)

        # Determine available actions.
        available_actions = []

        # Between collab and center, they can perform an art if:
        # * That card has not performed an art this turn.
        # * That card is not resting.
        # * That card has the cheer attached that is required for the art.
        performers = active_player.get_holomem_on_stage(only_performers=True)
        for performer in performers:
            if performer["resting"] or performer["used_art_this_turn"]:
                continue

            for art in performer["arts"]:
                if art_requirement_met(performer, art):
                    opponent_performers = self.other_player(self.active_player_id).get_holomem_on_stage(only_performers=True)
                    available_actions.append({
                        "action_type": "perform_art",
                        "performer_id": performer["game_card_id"],
                        "art_id": art["art_id"],
                        "power": art["power"],
                        "art_effects": art["art_effects"],
                        "valid_targets": ids_from_cards(opponent_performers),
                    })

        # End Performance
        available_actions.append({
            "action_type": "end_turn",
        })

        return available_actions

    def begin_performance_step(self):
        self.send_performance_step_actions()

    def continue_performance_step(self):
        self.send_performance_step_actions()

    def begin_perform_art(self, performer_id, art_id, target_id, continuation):
        player = self.get_player(self.active_player_id)
        performer = player.find_card(performer_id)
        target = self.other_player(self.active_player_id).find_card(target_id)
        art = next(art for art in performer["arts"] if art["art_id"] == art_id)

        self.performance_artstatboosts = ArtStatBoosts()
        self.performance_performer_card = performer
        self.performance_target_card = target
        self.performance_art = art
        self.performance_continuation = continuation

        # Get any before effects and resolve them.
        art_effects = get_effects_at_timing(art["art_effects"], "before_art")
        add_card_id_to_effects(art_effects, performer_id)
        player_turn_effects = get_effects_at_timing(player.turn_effects, "before_art")
        all_effects = art_effects + player_turn_effects
        self.begin_resolving_effects(all_effects, self.continue_perform_art)

    def continue_perform_art(self):
        # Now all before effects have been resolved.
        # Actually do the art.
        total_power = self.performance_art["power"]
        total_power += self.performance_artstatboosts.power

        # Deal damage.
        self.performance_target_card["damage"] += total_power
        died = self.performance_target_card["damage"] >= self.performance_target_card["hp"]
        owner = self.get_player(self.performance_target_card["owner_id"])

        game_over = False
        life_to_distribute = []
        if died:
            # Move all attached and stacked cards and the card itself to the archive.
            owner.archive_holomem_from_play(self.performance_target_card["game_card_id"])
            life_lost = 1
            if "down_life_cost" in self.performance_target_card:
                life_lost = self.performance_target_card["down_life_cost"]

            current_life = len(owner.life)
            if len(owner.get_holomem_on_stage()) == 0 or life_lost >= current_life:
                game_over = True

            if not game_over:
                life_to_distribute = ids_from_cards(owner.life[:life_lost])

        # Send an event
        art_event = {
            "event_type": EventType.EventType_PerformArt,
            "performer_id": self.performance_performer_card["game_card_id"],
            "art_id": self.performance_art["art_id"],
            "target_id": self.performance_target_card["game_card_id"],
            "power": total_power,
            "died": died,
            "game_over": game_over,
        }
        self.broadcast_event(art_event)

        if game_over:
            self.end_game(loser=owner.player_id)
        elif life_to_distribute:
            # Tell the owner to distribute this life amongst their holomems.
            remaining_holomems = ids_from_cards(owner.get_holomem_on_stage())
            decision_event = {
                "event_type": EventType.EventType_Decision_MoveCheerChoice,
                "effect_player_id": owner.player_id,
                "amount_min": len(life_to_distribute),
                "amount_max": len(life_to_distribute),
                "available_cheer": life_to_distribute,
                "available_targets": remaining_holomems,
                "from_life_pool": True,
            }
            self.broadcast_event(decision_event)
            self.set_decision({
                "decision_type": DecisionType.DecisionEffect_MoveCheerBetweenHolomems,
                "decision_player": owner.player_id,
                "amount_min": len(life_to_distribute),
                "amount_max": len(life_to_distribute),
                "available_cheer": life_to_distribute,
                "available_targets": remaining_holomems,
                "continuation": self.performance_continuation,
            })
        else:
            # Return to the performance step.
            self.performance_continuation()

    def begin_resolving_effects(self, effects, continuation, cleanup_card_to_archive=None):
        self.effects_to_resolve = effects
        self.effect_resolution_continuation = continuation
        self.effect_resolution_cleanup_card = cleanup_card_to_archive
        self.continue_resolving_effects()

    def continue_resolving_effects(self):
        if not self.effects_to_resolve:
            if self.effect_resolution_cleanup_card:
                owner = self.get_player(self.effect_resolution_cleanup_card["owner_id"])
                owner.archive.append(self.effect_resolution_cleanup_card)
                cleanup_event = {
                    "event_type": EventType.EventType_MoveCard,
                    "moving_player_id": owner.player_id,
                    "from_zone": "floating",
                    "to_zone": "archive",
                    "zone_card_id": "",
                    "card_id": self.effect_resolution_cleanup_card["game_card_id"],
                }
                self.broadcast_event(cleanup_event)
                self.effect_resolution_cleanup_card = None

            continuation = self.effect_resolution_continuation
            self.effect_resolution_continuation = self.blank_continuation
            continuation()
            return

        effect = self.effects_to_resolve.pop(0)
        effect_player = self.get_player(effect_player_id)
        effect_player_id = effect["player_id"]
        if self.is_effect_condition_met(effect_player, effect):
            self.do_effect(effect_player, effect)

        if not self.current_decision:
            self.continue_resolving_effects()

    def is_effect_condition_met(self, effect_player: PlayerState, effect):
        if "condition" not in effect:
            return True

        match effect["condition"]:
            case Condition.Condition_CardsInHand:
                amount_min = effect["amount_min"]
                amount_max = effect["amount_max"]
                if amount_max == -1:
                    amount_max = 1000
                return amount_min <= len(effect_player.hand) <= amount_max
            case Condition.Condition_CenterIsColor:
                condition_colors = effect["condition_colors"]
                center_colors = effect_player.center[0]["colors"]
                if any(color in center_colors for color in condition_colors):
                    return True
            case Condition.Condition_CheerInPlay:
                amount_min = effect["amount_min"]
                amount_max = effect["amount_max"]
                if amount_max == -1:
                    amount_max = 1000
                return amount_min <= len(effect_player.get_cheer_ids_on_holomems()) <= amount_max
            case Condition.Condition_CollabWith:
                required_member_name = effect["required_member_name"]
                holomems = effect_player.get_holomem_on_stage(only_performers=True)
                return any(required_member_name in holomem["holomem_names"] for holomem in holomems)
            case Condition.Condition_HolomemOnStage:
                required_member_name = effect["required_member_name"]
                holomems = effect_player.get_holomem_on_stage()
                return any(required_member_name in holomem["holomem_names"] for holomem in holomems)
            case Condition.Condition_TargetColor:
                color_requirement = effect["color_requirement"]
                return color_requirement in self.performance_target_card["colors"]
            case _:
                raise NotImplementedError(f"Unimplemented condition: {effect['condition']}")

        return False

    def do_effect(self, effect_player : PlayerState, effect):
        effect_player_id = effect_player.player_id
        match effect["effect_type"]:
            case EffectType.EffectType_AddTurnEffect:
                effect["turn_effect"]["source_card_id"] = effect["source_card_id"]
                effect_player.add_turn_effect(effect["turn_effect"])
            case EffectType.EffectType_ChooseCard:
                from_zone = effect["from"]
                to_zone = effect["to"]
                amount = effect["amount"]
                reveal = effect["reveal"]

                card_options = []
                hidden_zone = False
                if from_zone == "hand":
                    card_options = ids_from_cards(effect_player.hand)
                    hidden_zone = True
                elif from_zone == "holopower":
                    card_options = ids_from_cards(effect_player.holopower)
                    hidden_zone = True

                if reveal:
                    hidden_zone = False

                choose_event = {
                    "event_type": EventType.EventType_Decision_ChooseCard,
                    "effect_player_id": effect_player_id,
                    "card_options": card_options,
                    "from_zone": from_zone,
                    "to_zone": to_zone,
                    "amount": amount,
                    "reveal": reveal,
                }
                if hidden_zone:
                    choose_event["hidden_info_player"] = effect_player_id
                    choose_event["hidden_info_fields"] = ["card_options"]
                self.broadcast_event(choose_event)
                self.set_decision({
                    "decision_type": DecisionType.DecisionEffect_ChooseCardForEffect,
                    "decision_player": effect_player_id,
                    "choice_ids": card_options,
                    "from_zone": from_zone,
                    "to_zone": to_zone,
                    "reveal": reveal,
                    "effect_resolution": self.handle_choose_card_result,
                    "continuation": self.continue_resolving_effects,
                })
            case EffectType.EffectType_Draw:
                amount = effect["amount"]
                effect_player.draw(amount)
            case EffectType.EffectType_MoveCheerBetweenHolomems:
                amount = effect["amount"]
                available_cheer = effect_player.get_cheer_ids_on_holomems()
                available_targets = ids_from_cards(effect_player.get_holomem_on_stage())
                decision_event = {
                    "event_type": EventType.EventType_Decision_MoveCheerChoice,
                    "effect_player_id": effect_player_id,
                    "amount_min": amount,
                    "amount_max": amount,
                    "available_cheer": available_cheer,
                    "available_targets": available_targets,
                }
                self.broadcast_event(decision_event)
                self.set_decision({
                    "decision_type": DecisionType.DecisionEffect_MoveCheerBetweenHolomems,
                    "decision_player": effect_player_id,
                    "amount_min": amount,
                    "amount_max": amount,
                    "available_cheer": available_cheer,
                    "available_targets": available_targets,
                    "continuation": self.continue_resolving_effects,
                })
            case EffectType.EffectType_PowerBoost:
                amount = effect["amount"]
                self.performance_artstatboosts.power += amount
                self.send_boost_event(self.performance_performer_card["game_card_id"], "power", amount)
            case EffectType.EffectType_SendCheer:
                # Required params
                amount_min = effect["amount_min"]
                amount_max = effect["amount_max"]
                from_zone = effect["from"]
                to_zone = effect["to"]
                # Optional
                from_limitation = effect.get("from_limitation", "")
                from_limitation_colors = effect.get("from_limitation_colors", [])
                to_limitation = effect.get("to_limitation", "")
                to_limitation_colors = effect.get("to_limitation_colors", [])

                # Determine options
                from_options = []
                to_options = []

                match from_zone:
                    case "archive":
                        # Get archive cheer cards.
                        relevant_archive_cards = [card for card in effect_player.archive if card["card_type"] == "cheer"]
                        if from_limitation:
                            match from_limitation:
                                case "color_in":
                                    from_options = [card for card in relevant_archive_cards if any(color in card["colors"] for color in from_limitation_colors)]
                                case _:
                                    raise NotImplementedError(f"Unimplemented from limitation: {from_limitation}")

                    case "cheer_deck":
                        # Cheer deck is from top.
                        if len(effect_player.cheer_deck) > 0:
                            from_options = [effect_player.cheer_deck[0]]
                    case _:
                        raise NotImplementedError(f"Unimplemented from zone: {from_zone}")

                match to_zone:
                    case "holomem":
                        if to_limitation:
                            match to_limitation:
                                case "color_in":
                                    to_options = [card for card in effect_player.get_holomem_on_stage() if any(color in card["colors"] for color in to_limitation_colors)]
                                case "back":
                                    to_options = [card for card in effect_player.backstage]
                                case "center":
                                    to_options = effect_player.center
                                case _:
                                    raise NotImplementedError(f"Unimplemented to limitation: {to_limitation}")
                    case "this_holomem":
                        to_options = [effect["source_card_id"]]

                if len(to_options) == 0 or len(from_options) == 0:
                    # No effect.
                    pass
                else:
                    if len(from_options) < amount_min:
                        # If there's less cheer than the min, do as many as you can.
                        amount_min = len(from_options)
                    if amount_max == -1:
                        amount_max = 1000

                    decision_event = {
                        "event_type": EventType.EventType_Decision_SendCheer,
                        "effect_player_id": effect_player_id,
                        "amount_min": amount_min,
                        "amount_max": amount_max,
                        "from_zone": from_zone,
                        "from_limitation": from_limitation,
                        "from_limitation_colors": from_limitation_colors,
                        "to_zone": to_zone,
                        "to_limitation": to_limitation,
                        "to_limitation_colors": to_limitation_colors,
                        "from_options": ids_from_cards(from_options),
                        "to_options": ids_from_cards(to_options),
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_MoveCheerBetweenHolomems,
                        "decision_player": effect_player_id,
                        "amount_min": amount_min,
                        "amount_max": amount_max,
                        "available_cheer": ids_from_cards(from_options),
                        "available_targets": ids_from_cards(to_options),
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_SendCollabBack:
                optional = effect.get("optional", False)
                if optional:
                    # Ask the user if they want to send this collab back to the backstage.
                    choice_info = {
                        "specific_options": ["pass", "ok"]
                    }
                    min_choice = 0
                    max_choice = 2
                    decision_event = {
                        "event_type": EventType.EventType_Choice_SendCollabBack,
                        "choice_event": True,
                        "effect_player_id": effect_player_id,
                        "choice_info": choice_info,
                        "min_choice": min_choice,
                        "max_choice": max_choice,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionChoice,
                        "decision_player": effect_player_id,
                        "choice_info": choice_info,
                        "min_choice": min_choice,
                        "max_choice": max_choice,
                        "resolution_func": self.handle_choice_return_collab,
                        "continuation": self.continue_resolving_effects,
                    })
                else:
                    effect_player.return_collab()

            case EffectType.EffectType_ShuffleHandToDeck:
                effect_player.shuffle_hand_to_deck()
            case EffectType.EffectType_SwitchCenterWithBack:
                target_player = effect_player
                if effect["target_player"] == "opponent":
                    target_player = self.other_player(effect_player_id)
                available_backstage_ids = ids_from_cards(target_player.backstage)
                if len(available_backstage_ids) == 0:
                    # No effect.
                    pass
                elif len(available_backstage_ids) == 1:
                    # Do it right away.
                    target_player.swap_center_with_back(available_backstage_ids[0])
                else:
                    # Ask for a decision.
                    decision_event = {
                        "event_type": EventType.EventType_Decision_SwapHolomemToCenter,
                        "effect_player_id": effect_player_id,
                        "choice_ids": available_backstage_ids,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardForEffect,
                        "decision_player": effect_player_id,
                        "choice_ids": available_backstage_ids,
                        "effect_resolution": self.handle_holomem_swap,
                        "continuation": self.continue_resolving_effects,
                    })
            case _:
                raise NotImplementedError(f"Unimplemented effect type: {effect['effect_type']}")

    def end_game(self, loser_id):
        self.phase = GamePhase.GameOver

        gameover_event = {
            "event_type": "gameover",
            "loser": loser_id,
        }
        self.broadcast_event(gameover_event)

    def send_boost_event(self, card_id, stat:str, amount:int):
        boost_event = {
            "event_type": EventType.EventType_BoostStat,
            "card_id": card_id,
            "stat": stat,
            "amount": amount,
        }
        self.broadcast_event(boost_event)

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
                self.handle_mulligan(player_id, action_data)
            case GameAction.InitialPlacement:
                self.handle_initial_placement(player_id, action_data)
            case GameAction.ChooseNewCenter:
                self.handle_choose_new_center(player_id, action_data)
            case GameAction.PlaceCheer:
                self.handle_place_cheer(player_id, action_data)
            case GameAction.MainStepPlaceHolomem:
                self.handle_main_step_place_holomem(player_id, action_data)
            case GameAction.MainStepBloom:
                self.handle_main_step_bloom(player_id, action_data)
            case GameAction.MainStepCollab:
                self.handle_main_step_collab(player_id, action_data)
            case GameAction.MainStepOshiSkill:
                self.handle_main_step_oshi_skill(player_id, action_data)
            case GameAction.MainStepPlaySupport:
                self.handle_main_step_play_support(player_id, action_data)
            case GameAction.MainStepPassBaton:
                self.handle_main_step_pass_baton(player_id, action_data)
            case GameAction.MainStepBeginPerformance:
                self.handle_main_step_begin_performance(player_id, action_data)
            case GameAction.MainStepEndTurn:
                self.handle_main_step_end_turn(player_id, action_data)
            case GameAction.PerformanceStepUseArt:
                self.handle_performance_step_use_art(player_id, action_data)
            case GameAction.PerformanceStepEndTurn:
                self.handle_performance_step_end_turn(player_id, action_data)
            case GameAction.EffectResolution_MoveCheerBetweenHolomems:
                self.handle_effect_resolution_move_cheer_between_holomems(player_id, action_data)
            case GameAction.EffectResolution_ChooseCardForEffect:
                self.handle_effect_resolution_choose_card_for_effect(player_id, action_data)
            case GameAction.EffectResolution_MakeChoice:
                self.handle_effect_resolution_make_choice(player_id, action_data)
            case _:
                self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action type."))

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
        # The center card id must be in the current_decision options
        # The center card id has to be a card that is in the player's backstage.
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionChooseNewCenter, GameAction.ChooseNewCenterActionFields):
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

    def blank_continuation(self):
        raise NotImplementedError("Continuation expected.")

    def clear_decision(self):
        continuation = self.blank_continuation
        if self.current_decision:
            continuation = self.current_decision["continuation"]
            self.current_decision = None
        return continuation

    def handle_choose_new_center(self, player_id:str, action_data:dict):
        if not self.validate_choose_new_center(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        new_center_card_id = action_data["new_center_card_id"]
        player.move_card(new_center_card_id, "center")

        continuation()

    def validate_place_cheer(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionPlaceCheer, GameAction.PlaceCheerActionFields):
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

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        placements = action_data["placements"]
        for cheer_id, target_id in placements.items():
            player.move_card(cheer_id, "holomem", target_id)

        continuation()

    def validate_main_step_place_holomem(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepPlaceHolomemFields):
            return False

        chosen_card_id = action_data["card_id"]
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "place_holomem" and action["card_id"] == chosen_card_id:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_main_step_place_holomem(self, player_id:str, action_data:dict):
        if not self.validate_main_step_place_holomem(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        card_id = action_data["card_id"]
        player.move_card(card_id, "backstage")

        continuation()


    def validate_main_step_bloom(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepBloomFields):
            return False

        chosen_card_id = action_data["card_id"]
        target_id = action_data["target_id"]
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "bloom" and action["card_id"] == chosen_card_id and action["target_id"] == target_id:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_main_step_bloom(self, player_id:str, action_data:dict):
        if not self.validate_main_step_bloom(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        card_id = action_data["card_id"]
        target_id = action_data["target_id"]
        player.bloom(card_id, target_id)

        continuation()

    def validate_main_step_collab(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepCollabFields):
            return False

        chosen_card_id = action_data["card_id"]
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "collab" and action["card_id"] == chosen_card_id:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_main_step_collab(self, player_id:str, action_data:dict):
        if not self.validate_main_step_collab(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        card_id = action_data["card_id"]
        player.collab_action(card_id, continuation)

    def validate_decision_base(self, player_id:str, action_data:dict, expected_decision_type, expected_action_type):
        if not self.current_decision:
            self.send_event(self.make_error_event(player_id, "invalid_decision", "No current decision."))
            return False

        if not self.validate_action_fields(action_data, expected_action_type):
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action fields."))
            return False

        if player_id != self.current_decision["decision_player"]:
            self.send_event(self.make_error_event(player_id, "invalid_player", "Not your turn."))
            return False

        if self.current_decision["decision_type"] != expected_decision_type:
            self.send_event(self.make_error_event(player_id, "invalid_decision", "Invalid decision."))
            return False

        return True

    def validate_main_step_oshi_skill(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepOshiSkillFields):
            return False

        skill_id = action_data["skill_id"]
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "oshi_skill" and action["skill_id"] == skill_id:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_main_step_oshi_skill(self, player_id:str, action_data:dict):
        if not self.validate_main_step_oshi_skill(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        skill_id = action_data["skill_id"]

        skill_effects = player.trigger_oshi_skill(skill_id)
        add_card_id_to_effects(skill_effects, "oshi")
        self.begin_resolving_effects(skill_effects, continuation)

    def validate_main_step_play_support(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepPlaySupportFields):
            return False

        player = self.get_player(player_id)
        chosen_card_id = action_data["card_id"]
        action_found = None
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "play_support" and action["card_id"] == chosen_card_id:
                action_found = action
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        if "play_requirements" in action_found:
            # All fields in play_requirements must exist in action_data.
            for required_field in action_found["play_requirements"]:
                if required_field not in action_data:
                    self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
                    return False

                if required_field["type"] == "list":
                    if not isinstance(action_data[required_field], list) or len(action_data[required_field]) != required_field["length"]:
                        self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
                        return False

                    if required_field["content_type"] == "cheer_in_play":
                        # Validate that all items in the list are cheer cards on holomems.
                        validated = True
                        for cheer_id in action_data[required_field]:
                            if not isinstance(cheer_id, str):
                                validated = False
                                break
                            if cheer_id in player.get_cheer_ids_on_holomems():
                                validated = False
                                break

                        # The list must also be unique.
                        if len(set(action_data[required_field])) != len(action_data[required_field]):
                            validated = False

                        if not validated:
                            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
                            return False

        return True

    def handle_main_step_play_support(self, player_id:str, action_data:dict):
        if not self.validate_main_step_play_support(player_id, action_data):
            return

        continuation = self.clear_decision()

        player = self.get_player(player_id)
        card_id = action_data["card_id"]

        # Send an event showing the card being played.
        play_event = {
            "event_type": "play_support",
            "player_id": player_id,
            "card_id": card_id,
            "limited": is_card_limited(card),
        }
        self.broadcast_event(play_event)

        # Remove the card from hand.
        card, _, _ = player.find_and_remove_card(card_id)

        # Handle any requirements to play the card.
        cheer_to_archive_from_play = action_data.get("cheer_to_archive_from_play", [])
        if cheer_to_archive_from_play:
            player.archive_cheer(cheer_to_archive_from_play)

        # Begin resolving the card effects.
        if is_card_limited(card):
            player.used_limited_this_turn = True

        card_effects = card["effects"]
        add_card_id_to_effects(card_effects, card_id)
        self.begin_resolving_effects(card_effects, continuation, cleanup_card_to_archive=card)

    def validate_main_step_baton_pass(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepBatonPassFields):
            return False

        card_id = action_data["card_id"]
        # The card must be in the options in the available action.
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "pass_baton" and card_id in action["backstage_options"]:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_main_step_pass_baton(self, player_id:str, action_data:dict):
        if not self.validate_main_step_baton_pass(player_id, action_data):
            return

        player = self.get_player(player_id)
        new_center_id = action_data["card_id"]
        center_mem = player.center[0]
        baton_cost = center_mem["baton_cost"]
        player.swap_center_with_back(new_center_id)
        player.archive_cheer_from_deck(baton_cost)
        player.baton_pass_this_turn = True

        continuation = self.clear_decision()
        continuation()

    def validate_main_step_begin_performance(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepBeginPerformanceFields):
            return False

        return True

    def handle_main_step_begin_performance(self, player_id:str, action_data:dict):
        if not self.validate_main_step_begin_performance(player_id, action_data):
            return

        self.clear_decision()
        self.begin_performance_step()

    def handle_main_step_end_turn(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepEndTurnFields):
            return

        self.clear_decision()
        self.end_player_turn()

    def validate_performance_step_use_art(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionPerformanceStep, GameAction.PerformanceStepUseArtFields):
            return False

        performer_id = action_data["performer_id"]
        art_id = action_data["art_id"]
        target_id = action_data["target_id"]

        # Validate that there is an available action that matches.
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == "perform_art" and action["performer_id"] == performer_id and action["art_id"] == art_id:
                if target_id in action["valid_targets"]:
                    action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        return True

    def handle_performance_step_use_art(self, player_id:str, action_data:dict):
        if not self.validate_performance_step_use_art(player_id, action_data):
            return

        continuation = self.clear_decision()

        performer_id = action_data["performer_id"]
        art_id = action_data["art_id"]
        target_id = action_data["target_id"]

        self.begin_perform_art(performer_id, art_id, target_id, continuation)

    def handle_performance_step_end_turn(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionPerformanceStep, GameAction.PerformanceStepEndTurnFields):
            return

        self.clear_decision()
        self.end_player_turn()

    def validate_move_cheer_between_holomems(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionEffect_MoveCheerBetweenHolomems, GameAction.EffectResolution_MoveCheerBetweenHolomemsFields):
            return False

        placements = action_data["placements"]
        # All placement cheer_ids must be unique.
        if len(set(placements.keys())) != len(placements):
            self.send_event(self.make_error_event(player_id, "invalid_cheer", "Duplicate cheer placements."))
            return False

        # Amount must match.
        if len(placements) < self.current_decision["amount_min"] or len(placements) > self.current_decision["amount_max"]:
            self.send_event(self.make_error_event(player_id, "invalid_amount", "Invalid amount of cheer to move."))
            return False

        for cheer_id, target_id in placements.items():
            if cheer_id not in self.current_decision["available_cheer"]:
                self.send_event(self.make_error_event(player_id, "invalid_cheer", "Invalid cheer to place."))
                return False
            if target_id not in self.current_decision["available_targets"]:
                self.send_event(self.make_error_event(player_id, "invalid_target", "Invalid target for cheer."))
                return False

        return True

    def handle_effect_resolution_move_cheer_between_holomems(self, player_id:str, action_data:dict):
        if not self.validate_move_cheer_between_holomems(player_id, action_data):
            return

        player = self.get_player(player_id)
        placements = action_data["placements"]
        player.move_cheer_between_holomems(placements)

        continuation = self.clear_decision()
        continuation()

    def validate_choose_card_for_effect(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionEffect_ChooseCardForEffect, GameAction.EffectResolution_ChooseCardForEffectFields):
            return False

        chosen_card_id = action_data["card_id"]
        if chosen_card_id not in self.current_decision["choice_ids"]:
            self.send_event(self.make_error_event(player_id, "invalid_card", "Invalid card choice."))
            return False

        return True

    def handle_effect_resolution_choose_card_for_effect(self, player_id:str, action_data:dict):
        if not self.validate_choose_card_for_effect(player_id, action_data):
            return

        chosen_card_id = action_data["card_id"]
        resolution = self.current_decision["effect_resolution"]
        resolution(player_id, chosen_card_id)

        continuation = self.clear_decision()
        continuation()

    def validate_effect_resolution_make_choice(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionChoice, GameAction.EffectResolution_MakeChoiceFields):
            return

        choice_index = action_data["choice_index"]
        if choice_index < self.current_decision["min_choice"] or choice_index > self.current_decision["max_choice"]:
            self.send_event(self.make_error_event(player_id, "invalid_choice", "Invalid choice."))
            return False

        return True

    def handle_effect_resolution_make_choice(self, player_id:str, action_data:dict):
        if not self.validate_effect_resolution_make_choice(player_id, action_data):
            return

        choice_index = action_data["choice_index"]
        resolution_func = self.current_decision["resolution_func"]

        continuation = self.clear_decision()
        resolution_func(player_id, choice_index, continuation)

    def handle_holomem_swap(self, performing_player_id:str, card_id:str):
        owner_id = get_owner_id_from_card_id(card_id)
        owner = self.get_player(owner_id)
        owner.swap_center_with_back(card_id)

    def handle_choose_card_result(self, performing_player_id:str, card_id:str):
        from_zone = self.current_decision["from_zone"]
        to_zone = self.current_decision["to_zone"]
        reveal = self.current_decision["reveal"]

        player = self.get_player(performing_player_id)
        player.move_card(self, card_id, to_zone, zone_card_id="", hidden_info=not reveal)

    def handle_choice_return_collab(self, player_id, choice_index, continuation):
        # 0 is pass, 1 is okay
        if choice_index == 1:
            player = self.get_player(player_id)
            player.return_collab()

        continuation()