from typing import List, Dict, Any
from app.card_database import CardDatabase
import random
from copy import deepcopy
import logging
logger = logging.getLogger(__name__)

UNKNOWN_CARD_ID = "HIDDEN"
UNLIMITED_SIZE = 9999
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
    DecisionEffect_ChooseCardsForEffect = "decision_choose_cards_for_effect"
    DecisionEffect_OrderCards = "decision_order_cards"

class EffectType:
    EffectType_AddTurnEffect = "add_turn_effect"
    EffectType_AddTurnEffectForHolomem = "add_turn_effect_for_holomem"
    EffectType_AfterArchiveCheerCheck = "after_archive_check"
    EffectType_ArchiveCheerFromHolomem = "archive_cheer_from_holomem"
    EffectType_ArchiveFromHand = "archive_from_hand"
    EffectType_ArchiveFromHandVariable = "archive_from_hand_variable"
    EffectType_AttachCardToHolomem = "attach_card_to_holomem"
    EffectType_AttachCardToHolomem_Internal = "attach_card_to_holomem_internal"
    EffectType_BlockOpponentMovement = "block_opponent_movement"
    EffectType_Choice = "choice"
    EffectType_ChooseCards = "choose_cards"
    EffectType_DealDamage = "deal_damage"
    EffectType_DownHolomem = "down_holomem"
    EffectType_Draw = "draw"
    EffectType_ForceDieResult = "force_die_result"
    EffectType_GenerateChoiceTemplate = "generate_choice_template"
    EffectType_GenerateHolopower = "generate_holopower"
    EffectType_OshiActivation = "oshi_activation"
    EffectType_MoveCheerBetweenHolomems = "move_cheer_between_holomems"
    EffectType_OrderCards = "order_cards"
    EffectType_Pass = "pass"
    EffectType_PerformanceLifeLostIncrease = "performance_life_lost_increase"
    EffectType_PlaceHolomem = "place_holomem"
    EffectType_PowerBoost = "power_boost"
    EffectType_PowerBoostPerBackstage = "power_boost_per_backstage"
    EffectType_PowerBoostPerHolomem = "power_boost_per_holomem"
    EffectType_PowerBoostPerStacked = "power_boost_per_stacked"
    EffectType_RecordEffectCardIdUsedThisTurn = "record_effect_card_id_used_this_turn"
    EffectType_RecordUsedOncePerGameEffect = "record_used_once_per_game_effect"
    EffectType_RecordUsedOncePerTurnEffect = "record_used_once_per_turn_effect"
    EffectType_RecoverDownedHolomemCards = "recover_downed_holomem_cards"
    EffectType_ReduceDamage = "reduce_damage"
    EffectType_ReduceRequiredArchiveCount = "reduce_required_archive_count"
    EffectType_RepeatArt = "repeat_art"
    EffectType_RestoreHp = "restore_hp"
    EffectType_RevealTopDeck = "reveal_top_deck"
    EffectType_RollDie = "roll_die"
    EffectType_RollDie_ChooseResult = "choose_die_result"
    EffectType_RollDie_Internal = "roll_die_INTERNAL"
    EffectType_SendCheer = "send_cheer"
    EffectType_SendCollabBack = "send_collab_back"
    EffectType_SetCenterHP = "set_center_hp"
    EffectType_ShuffleHandToDeck = "shuffle_hand_to_deck"
    EffectType_SpendHolopower = "spend_holopower"
    EffectType_SwitchCenterWithBack = "switch_center_with_back"

class Condition:
    Condition_AttachedTo = "attached_to"
    Condition_BloomTargetIsDebut = "bloom_target_is_debut"
    Condition_CanArchiveFromHand = "can_archive_from_hand"
    Condition_CanMoveFrontStage = "can_move_front_stage"
    Condition_CardsInHand = "cards_in_hand"
    Condition_CenterIsColor = "center_is_color"
    Condition_CenterHasAnyTag = "center_has_any_tag"
    Condition_CheerInPlay = "cheer_in_play"
    Condition_ChosenCardHasTag = "chosen_card_has_tag"
    Condition_CollabWith = "collab_with"
    Condition_CurrentHolopower = "current_holopower"
    Condition_DamageAbilityIsColor = "damage_ability_is_color"
    Condition_DamagedHolomemIsBackstage = "damaged_holomem_is_backstage"
    Condition_DamagedHolomemIsCenterOrCollab = "damaged_holomem_is_center_or_collab"
    Condition_DamageSourceIsOpponent = "damage_source_is_opponent"
    Condition_DownedCardBelongsToOpponent = "downed_card_belongs_to_opponent"
    Condition_DownedCardIsColor = "downed_card_is_color"
    Condition_EffectCardIdNotUsedThisTurn = "effect_card_id_not_used_this_turn"
    Condition_HasAttachmentOfType = "has_attachment_of_type"
    Condition_HolomemOnStage = "holomem_on_stage"
    Condition_HolopowerAtLeast = "holopower_at_least"
    Condition_NotUsedOncePerGameEffect = "not_used_once_per_game_effect"
    Condition_NotUsedOncePerTurnEffect = "not_used_once_per_turn_effect"
    Condition_OpponentTurn = "opponent_turn"
    Condition_OshiIs = "oshi_is"
    Condition_PerformanceTargetHasDamageOverHp = "performance_target_has_damage_over_hp"
    Condition_PerformerIsCenter = "performer_is_center"
    Condition_PerformerIsColor = "performer_is_color"
    Condition_PerformerIsSpecificId = "performer_is_specific_id"
    Condition_PerformerHasAnyTag = "performer_has_any_tag"
    Condition_PlayedSupportThisTurn = "played_support_this_turn"
    Condition_SelfHasCheer = "self_has_cheer"
    Condition_SelfHasCheerColor = "self_has_cheer_color"
    Condition_StageHasSpace = "stage_has_space"
    Condition_TargetColor = "target_color"
    Condition_TargetHasAnyTag = "target_has_any_tag"
    Condition_ThisCardIsCollab = "this_card_is_collab"
    Condition_TopDeckCardHasAnyTag = "top_deck_card_has_any_tag"


class TurnEffectType:
    TurnEffectType_CenterArtsBonus = "center_arts_bonus"

class EventType:
    EventType_AddTurnEffect = "add_turn_effect"
    EventType_Bloom = "bloom"
    EventType_BoostStat = "boost_stat"
    EventType_CheerStep = "cheer_step"
    EventType_Choice_SendCollabBack = "choice_send_collab_back"
    EventType_Collab = "collab"
    EventType_DamageDealt = "damage_dealt"
    EventType_Decision_Choice = "decision_choice"
    EventType_Decision_ChooseCards = "decision_choose_cards"
    EventType_Decision_ChooseHolomemForEffect = "decision_choose_holomem_for_effect"
    EventType_Decision_MainStep = "decision_main_step"
    EventType_Decision_OrderCards = "decision_order_cards"
    EventType_Decision_PerformanceStep = "decision_performance_step"
    EventType_Decision_SendCheer = "decision_send_cheer"
    EventType_Decision_SwapHolomemToCenter = "decision_choose_holomem_swap_to_center"
    EventType_DownedHolomem = "downed_holomem"
    EventType_Draw = "draw"
    EventType_EndTurn = "end_turn"
    EventType_ForceDieResult = "force_die_result"
    EventType_GameError = "game_error"
    EventType_GameOver = "game_over"
    EventType_GameStartInfo = "game_start_info"
    EventType_GenerateHolopower = "generate_holopower"
    EventType_InitialPlacementBegin = "initial_placement_begin"
    EventType_InitialPlacementPlaced = "initial_placement_placed"
    EventType_InitialPlacementReveal = "initial_placement_reveal"
    EventType_MainStepStart = "main_step_start"
    EventType_ModifyHP = "modify_hp"
    EventType_MoveCard = "move_card"
    EventType_MoveAttachedCard = "move_attached_card"
    EventType_MulliganDecision = "mulligan_decision"
    EventType_MulliganReveal = "mulligan_reveal"
    EventType_OshiSkillActivation = "oshi_skill_activation"
    EventType_PerformanceStepStart = "performance_step_start"
    EventType_PerformArt = "perform_art"
    EventType_PlaySupportCard = "play_support_card"
    EventType_ResetStepActivate = "reset_step_activate"
    EventType_ResetStepChooseNewCenter = "reset_step_choose_new_center"
    EventType_ResetStepCollab = "reset_step_collab"
    EventType_RestoreHP = "restore_hp"
    EventType_RevealCards = "reveal_cards"
    EventType_RollDie = "roll_die"
    EventType_ShuffleDeck = "shuffle_deck"
    EventType_TurnStart = "turn_start"

class GameOverReason:
    GameOverReason_NoHolomemsLeft = "no_holomems_left"
    GameOverReason_DeckEmptyDraw = "deck_empty_draw"
    GameOverReason_NoLifeLeft = "no_life_left"

class ArtStatBoosts:
    def __init__(self):
        self.power = 0
        self.bonus_life_loss = 0
        self.repeat_art = False

    def clear(self):
        self.power = 0
        self.bonus_life_loss = 0
        self.repeat_art = False

class DamageModifications:
    def __init__(self):
        self.prevented_damage = 0
        self.source_player = None

    def clear(self):
        self.prevented_damage = 0
        self.source_player = None

class AfterDamageState:
    def __init__(self):
        self.source_player : PlayerState = None
        self.source_card = None
        self.target_player : PlayerState = None
        self.target_card = None
        self.damage_dealt = 0

        self.nested_state = None

class DownHolomemState:
    def __init__(self):
        self.holomem_card = None

        self.nested_state = None

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
        "cheer_ids": List[str],
    }

    MainStepBeginPerformance = "mainstep_begin_performance"
    MainStepBeginPerformanceFields = {}

    MainStepEndTurn = "mainstep_end_turn"
    MainStepEndTurnFields = {}

    PerformanceStepUseArt = "performance_step_use_art"
    PerformanceStepUseArtFields = {
        "performer_id": str,
        "art_id": str,
        "target_id": str,
    }

    PerformanceStepEndTurn = "performance_step_end_turn"
    PerformanceStepEndTurnFields = {}

    EffectResolution_MoveCheerBetweenHolomems = "effect_resolution_move_cheer_between_holomems"
    EffectResolution_MoveCheerBetweenHolomemsFields = {
        # Dict of cheer and target ids.
        "placements": Dict[str, str],
    }

    EffectResolution_ChooseCardsForEffect = "effect_resolution_choose_card_for_effect"
    EffectResolution_ChooseCardsForEffectFields = {
        "card_ids": List[str],
    }

    EffectResolution_MakeChoice = "effect_resolution_make_choice"
    EffectResolution_MakeChoiceFields = {
        "choice_index": int,
    }

    EffectResolution_OrderCards = "effect_resolution_order_cards"
    EffectResolution_OrderCardsFields = {
        "card_ids": List[str],
    }

    Resign = "resign"
    ResignFields = {
    }

class EffectResolutionState:
    def __init__(self, effects, continuation, cards_to_cleanup = []):
        self.effects_to_resolve = deepcopy(effects)
        self.effect_resolution_continuation = continuation
        self.cards_to_cleanup = cards_to_cleanup

class PlayerState:
    def __init__(self, card_db:CardDatabase, player_info:Dict[str, Any], engine: 'GameEngine'):
        self.engine = engine
        self.player_id = player_info["player_id"]

        self.first_turn = True
        self.baton_pass_this_turn = False
        self.collabed_this_turn = False
        self.mulligan_completed = False
        self.mulligan_hand_valid = False
        self.mulligan_count = 0
        self.initial_placement_completed = False
        self.life = []
        self.hand = []
        self.archive = []
        self.backstage = []
        self.center = []
        self.collab = []
        self.holopower = []
        self.effects_used_this_turn = []
        self.effects_used_this_game = []
        self.used_limited_this_turn = False
        self.played_support_this_turn = False
        self.turn_effects = []
        self.set_next_die_roll = 0
        self.card_effects_used_this_turn = []
        self.block_movement_for_turn = False
        self.last_archived_count = 0

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
                generated_card = deepcopy(card)
                generated_card["owner_id"] = self.player_id
                generated_card["game_card_id"] = self.player_id + "_" + str(card_number)
                generated_card["played_this_turn"] = False
                generated_card["bloomed_this_turn"] = False
                generated_card["attached_cheer"] = []
                generated_card["attached_support"] = []
                generated_card["stacked_cards"] = []
                generated_card["damage"] = 0
                generated_card["resting"] = False
                generated_card["rest_extra_turn"] = False
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
                generated_card = deepcopy(card)
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

    def shuffle_hand_to_deck(self):
        while len(self.hand) > 0:
            self.move_card(self.hand[0]["game_card_id"], "deck", hidden_info=True)
        self.shuffle_deck()

    def shuffle_deck(self):
        self.engine.shuffle_list(self.deck)
        shuffle_event = {
            "event_type": EventType.EventType_ShuffleDeck,
            "shuffling_player_id": self.player_id,
        }
        self.engine.broadcast_event(shuffle_event)

    def shuffle_cheer_deck(self):
        self.engine.shuffle_list(self.cheer_deck)

    def matches_oshi_color(self, colors):
        for color in colors:
            if color in self.oshi_card["colors"]:
                return True
        return False

    def matches_stage_holomems_color(self, colors):
        for card in self.get_holomem_on_stage():
            for color in colors:
                if color in card["colors"]:
                    return True
        return False

    def can_archive_from_hand(self, amount, condition_source):
        return self.get_can_archive_from_hand_count(condition_source) >= amount

    def get_can_archive_from_hand_count(self, condition_source):
        available_to_archive = len(self.hand)
        if "special_hand_archive_skill_per_turn" in self.oshi_card and self.oshi_card["special_hand_archive_skill_per_turn"] == "executivesorder":
            if condition_source == "holomem_red" and not self.has_used_once_per_turn_effect("executivesorder"):
                # Lui can use holopower as well.
                available_to_archive += len(self.holopower)
        return available_to_archive

    def get_and_reset_last_archived_count(self):
        last_archived_count = self.last_archived_count
        self.last_archived_count = 0
        return last_archived_count

    def can_move_front_stage(self):
        return not self.block_movement_for_turn

    def get_accepted_bloom_for_card(self, card):
        accepted_bloom_levels = []
        if card["card_type"] == "holomem_debut":
            accepted_bloom_levels = [1]
        elif card["card_type"] == "holomem_bloom":
            current_bloom_level = card["bloom_level"]
            accepted_bloom_levels = [current_bloom_level, current_bloom_level+1]

        if "bloom_level_skip" in card:
            meets_req = False
            if "bloom_level_skip_requirement" in card:
                match card["bloom_level_skip_requirement"]:
                    case "3lifeorless":
                        meets_req = len(self.life) <= 3
            if meets_req:
                accepted_bloom_levels.append(card["bloom_level_skip"])
        return accepted_bloom_levels

    def record_card_effect_used_this_turn(self, card_id):
        if card_id not in self.card_effects_used_this_turn:
            self.card_effects_used_this_turn.append(card_id)

    def has_used_card_effect_this_turn(self, card_id):
        return card_id in self.card_effects_used_this_turn

    def record_effect_used_this_turn(self, effect_id):
        if effect_id not in self.effects_used_this_turn:
            self.effects_used_this_turn.append(effect_id)

    def has_used_once_per_turn_effect(self, effect_id):
        return effect_id in self.effects_used_this_turn

    def record_effect_used_this_game(self, effect_id):
        if effect_id not in self.effects_used_this_game:
            self.effects_used_this_game.append(effect_id)

    def has_used_once_per_game_effect(self, effect_id):
        return effect_id in self.effects_used_this_game

    def get_effects_at_timing(self, timing, card, timing_source_requirement = ""):
        effects = []
        for oshi_effect in self.oshi_card.get("effects", []):
            if oshi_effect["timing"] == timing:
                if "timing_source_requirement" in oshi_effect and oshi_effect["timing_source_requirement"] != timing_source_requirement:
                    continue
                effects.append(oshi_effect)
        add_ids_to_effects(effects, self.player_id, "oshi")

        turn_effects = filter_effects_at_timing(self.turn_effects, timing)
        add_ids_to_effects(turn_effects, self.player_id, "")
        effects.extend(turn_effects)

        for holomem in self.get_holomem_on_stage():
            if "gift_effects" in holomem:
                gift_effects = filter_effects_at_timing(holomem["gift_effects"], timing)
                add_ids_to_effects(gift_effects, self.player_id, holomem["game_card_id"])
                effects.extend(gift_effects)

        if card and card["card_type"] not in ["support", "oshi"]:
            for attached_card in card["attached_support"]:
                attached_effects = attached_card.get("attached_effects", [])
                for attached_effect in attached_effects:
                    if attached_effect["timing"] == timing:
                        if "timing_source_requirement" in attached_effect and attached_effect["timing_source_requirement"] != timing_source_requirement:
                            continue
                        add_ids_to_effects([attached_effect], self.player_id, attached_card["game_card_id"])
                        effects.append(attached_effect)
        return effects


    def get_cheer_ids_on_holomems(self):
        cheer_ids = []
        for card in self.get_holomem_on_stage():
            for attached_card in card["attached_cheer"]:
                if is_card_cheer(attached_card):
                    cheer_ids.append(attached_card["game_card_id"])
        return cheer_ids

    def get_cheer_on_each_holomem(self, exclude_empty_members = False):
        cheer = {}
        for card in self.get_holomem_on_stage():
            cheer[card["game_card_id"]] = [attached_card["game_card_id"] for attached_card in card["attached_cheer"]]
            if exclude_empty_members and len(cheer[card["game_card_id"]]) == 0:
                del cheer[card["game_card_id"]]
        return cheer

    def get_holomems_with_cheer(self):
        holomems = []
        for card in self.get_holomem_on_stage():
            if card["attached_cheer"]:
                holomems.append(card["game_card_id"])
        return holomems

    def is_cheer_on_holomem(self, cheer_id, target_id):
        holomem_card, _, _ = self.find_card(target_id)
        if holomem_card:
            for attached_card in holomem_card["attached_cheer"]:
                if attached_card["game_card_id"] == cheer_id:
                    return True
        return False

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

    def get_holomems_with_attachment(self, attachment_id):
        for card in self.get_holomem_on_stage():
            if attachment_id in ids_from_cards(card["attached_cheer"] + card["attached_support"]):
                return [card]
        return []

    def is_center_holomem(self, card_id):
        return card_id in ids_from_cards(self.center)

    def get_zone_name(self, zone):
        match zone:
            case self.hand: return "hand"
            case self.archive: return "archive"
            case self.backstage: return "backstage"
            case self.center: return "center"
            case self.collab: return "collab"
            case self.deck: return "deck"
            case self.cheer_deck: return "cheer_deck"
            case self.holopower: return "holopower"
            case _: return "unknown"

    def find_card(self, card_id):
        zones = [self.hand, self.archive, self.backstage, self.center, self.collab, self.deck, self.cheer_deck, self.holopower]
        for zone in zones:
            for card in zone:
                if card["game_card_id"] == card_id:
                    zone_name = self.get_zone_name(zone)
                    return card, zone, zone_name
        for card in self.engine.floating_cards:
            if card["game_card_id"] == card_id:
                return card, self.engine.floating_cards, "floating"
        # Card, Zone, Zone Name
        return None, None, None

    def find_and_remove_card(self, card_id):
        card, zone, zone_name = self.find_card(card_id)
        if card and zone:
            zone.remove(card)
        return card, zone, zone_name

    def move_card(self, card_id, to_zone, zone_card_id="", hidden_info=False, add_to_bottom=False, no_events=False):
        card, _, from_zone_name = self.find_and_remove_card(card_id)
        if not card:
            card, previous_holder_id = self.find_and_remove_attached(card_id)
            from_zone_name = previous_holder_id
        if to_zone == "center":
            self.center.append(card)
        elif to_zone == "collab":
            self.collab.append(card)
        elif to_zone == "backstage":
            self.backstage.append(card)
        elif to_zone == "cheer_deck":
            self.cheer_deck.append(card)
            self.engine.shuffle_list(self.cheer_deck)
        elif to_zone == "hand":
            self.hand.append(card)
        elif to_zone == "holomem":
            holomem_card, _, _ = self.find_card(zone_card_id)
            attach_card(card, holomem_card)
        elif to_zone == "holopower":
            self.holopower.insert(0, card)
        elif to_zone == "deck":
            if add_to_bottom:
                self.deck.append(card)
            else:
                self.deck.insert(0, card)
        elif to_zone == "archive":
            if add_to_bottom:
                self.archive.append(card)
            else:
                self.archive.insert(0, card)

        if to_zone in ["center", "backstage", "collab", "holomem"] and from_zone_name in ["hand", "deck"]:
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
        if not no_events:
            self.engine.broadcast_event(move_card_event)

    def active_resting_cards(self):
        # For each card in the center, backstage, and collab zones, check if they are resting.
        # If so, set resting to false.
        activated_card_ids = []
        for card in self.get_holomem_on_stage():
            if is_card_resting(card):
                if card["rest_extra_turn"]:
                    card["rest_extra_turn"] = False
                else:
                    card["resting"] = False
                    activated_card_ids.append(card["game_card_id"])
        return activated_card_ids

    def on_my_turn_end(self):
        self.first_turn = False
        self.block_movement_for_turn = False

    def clear_every_turn_effects(self):
        self.baton_pass_this_turn = False
        self.collabed_this_turn = False
        self.turn_effects = []
        self.used_limited_this_turn = False
        self.played_support_this_turn = False
        self.effects_used_this_turn = []
        self.card_effects_used_this_turn = []
        for card in self.get_holomem_on_stage():
            card["used_art_this_turn"] = False
            card["played_this_turn"] = False
            card["bloomed_this_turn"] = False

    def reset_collab(self):
        # For all cards in collab, move them back to backstage and rest them.
        rested_card_ids = []
        moved_backstage_card_ids = []
        for card in self.collab:
            card["resting"] = True
            rested_card_ids.append(card["game_card_id"])

        if self.can_move_front_stage():
            for card in self.collab:
                self.backstage.append(card)
                moved_backstage_card_ids.append(card["game_card_id"])
            self.collab = []

        return rested_card_ids, moved_backstage_card_ids

    def return_collab(self):
        # For all cards in collab, move them back to backstage and rest them.
        collab_card_ids = ids_from_cards(self.collab)
        for card_id in collab_card_ids:
            self.move_card(card_id, "backstage")

    def bloom(self, bloom_card_id, target_card_id, continuation):
        bloom_card, _, bloom_from_zone_name = self.find_and_remove_card(bloom_card_id)
        target_card, zone, _ = self.find_and_remove_card(target_card_id)

        bloom_card["stacked_cards"].append(target_card)
        # Add any stacked cards on the target to this too.
        bloom_card["stacked_cards"] += target_card["stacked_cards"]
        target_card["stacked_cards"] = []

        bloom_card["attached_cheer"] += target_card["attached_cheer"]
        target_card["attached_cheer"] = []
        bloom_card["attached_support"] += target_card["attached_support"]
        target_card["attached_support"] = []

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

        # Handle any bloom effects.
        if "bloom_effects" in bloom_card:
            effects = deepcopy(bloom_card["bloom_effects"])
            add_ids_to_effects(effects, self.player_id, bloom_card_id)
            self.engine.begin_resolving_effects(effects, continuation)
        else:
            continuation()

    def generate_holopower(self, amount, skip_event=False):
        for _ in range(amount):
            self.holopower.insert(0, self.deck.pop(0))
        if not skip_event:
            generate_hp_event = {
                "event_type": EventType.EventType_GenerateHolopower,
                "generating_player_id": self.player_id,
                "holopower_generated": amount,
            }
            self.engine.broadcast_event(generate_hp_event)

    def collab_action(self, collab_card_id, continuation):
        # Move the card and generate holopower.
        collab_card, _, _ = self.find_and_remove_card(collab_card_id)
        self.collab.append(collab_card)
        self.collabed_this_turn = True
        self.generate_holopower(1, skip_event=True)

        collab_event = {
            "event_type": EventType.EventType_Collab,
            "collab_player_id": self.player_id,
            "collab_card_id": collab_card_id,
            "holopower_generated": 1,
        }
        self.engine.broadcast_event(collab_event)

        # Handle collab effects.
        collab_effects = deepcopy(collab_card["collab_effects"]) if "collab_effects" in collab_card else []
        add_ids_to_effects(collab_effects, self.player_id, collab_card_id)
        self.engine.begin_resolving_effects(collab_effects, continuation)

    def spend_holopower(self, amount):
        for _ in range(amount):
            top_holopower_id = self.holopower[0]["game_card_id"]
            self.move_card(top_holopower_id, "archive")

    def get_oshi_action_effects(self, skill_id):
        action = next(action for action in self.oshi_card["actions"] if action["skill_id"] == skill_id)
        return deepcopy(action["effects"])

    def find_and_remove_attached(self, attached_id):
        previous_holder_id = None
        found_card = None
        for card in self.get_holomem_on_stage():
            if attached_id in ids_from_cards(card["attached_cheer"]):
                # Remove the cheer.
                found_card = next(card for card in card["attached_cheer"] if card["game_card_id"] == attached_id)
                previous_holder_id = card["game_card_id"]
                card["attached_cheer"].remove(found_card)
                break
            if attached_id in ids_from_cards(card["attached_support"]):
                # Remove the support.
                found_card = next(card for card in card["attached_support"] if card["game_card_id"] == attached_id)
                previous_holder_id = card["game_card_id"]
                card["attached_support"].remove(found_card)
                break
            if attached_id in ids_from_cards(card["stacked_cards"]):
                # Remove the stacked card.
                found_card = next(card for card in card["stacked_cards"] if card["game_card_id"] == attached_id)
                previous_holder_id = card["game_card_id"]
                card["stacked_cards"].remove(found_card)
                break
        if not previous_holder_id:
            # Check the life deck.
            if attached_id in ids_from_cards(self.life):
                found_card = next(card for card in self.life if card["game_card_id"] == attached_id)
                self.life.remove(found_card)
                previous_holder_id = "life"
            # And the archive.
            elif attached_id in ids_from_cards(self.archive):
                found_card = next(card for card in self.archive if card["game_card_id"] == attached_id)
                self.archive.remove(found_card)
                previous_holder_id = "archive"
            # And the cheer deck.
            elif attached_id in ids_from_cards(self.cheer_deck):
                found_card = next(card for card in self.cheer_deck if card["game_card_id"] == attached_id)
                self.cheer_deck.remove(found_card)
                previous_holder_id = "cheer_deck"
        return found_card, previous_holder_id

    def find_and_remove_support(self, support_id):
        previous_holder_id = None
        for card in self.get_holomem_on_stage():
            if support_id in ids_from_cards(card["attached_support"]):
                # Remove the support card.
                support_card = next(card for card in card["attached_support"] if card["game_card_id"] == support_id)
                previous_holder_id = card["game_card_id"]
                card["attached_support"].remove(support_card)
                break
        return support_card, previous_holder_id

    def move_cheer_between_holomems(self, placements):
        for cheer_id, target_id in placements.items():
            # Find and remove the cheer from its current spot.
            if target_id == "archive":
                self.archive_attached_cards([cheer_id])
            else:
                cheer_card, previous_holder_id = self.find_and_remove_attached(cheer_id)
                if cheer_card:
                    # Attach to the target.
                    target_card, _, _ = self.find_card(target_id)
                    target_card["attached_cheer"].append(cheer_card)

                    move_cheer_event = {
                        "event_type": EventType.EventType_MoveAttachedCard,
                        "owning_player_id": self.player_id,
                        "from_holomem_id": previous_holder_id,
                        "to_holomem_id": target_card["game_card_id"],
                        "attached_id": cheer_id,
                    }
                    self.engine.broadcast_event(move_cheer_event)

    def archive_attached_cards(self, attached_ids):
        for attached_id in attached_ids:
            attached_card, previous_holder_id = self.find_and_remove_attached(attached_id)
            if attached_card:
                self.archive.insert(0, attached_card)
                move_attached_event = {
                    "event_type": EventType.EventType_MoveAttachedCard,
                    "owning_player_id": self.player_id,
                    "from_holomem_id": previous_holder_id,
                    "to_holomem_id": "archive",
                    "attached_id": attached_id,
                }
                self.engine.broadcast_event(move_attached_event)

    def archive_holomem_from_play(self, card_id):
        card, _, _ = self.find_and_remove_card(card_id)
        attached_cheer = card["attached_cheer"]
        attached_support = card["attached_support"]
        stacked_cards = card["stacked_cards"]

        to_archive = attached_cheer + attached_support + stacked_cards

        for extra_card in to_archive:
            self.archive.insert(0, extra_card)
        self.archive.insert(0, card)

        return ids_from_cards(to_archive)

    def return_holomem_to_hand(self, card_id, include_stacked_holomem = False):
        returning_card, _, _ = self.find_and_remove_card(card_id)
        attached_cheer = returning_card["attached_cheer"]
        attached_support = returning_card["attached_support"]
        stacked_cards = returning_card["stacked_cards"]

        archived_ids = []
        hand_ids = []

        to_archive = attached_cheer + attached_support
        to_hand = [returning_card] # Make sure to grab the actual card itself.
        self.hand.append(returning_card)

        if include_stacked_holomem:
            to_hand += stacked_cards
        else:
            to_archive += stacked_cards

        for card in to_archive:
            self.archive.insert(0, card)
        for card in to_hand:
            self.hand.append(card)
        archived_ids = ids_from_cards(to_archive)
        hand_ids = ids_from_cards(to_hand)

        return archived_ids, hand_ids

    def swap_center_with_back(self, back_id):
        if len(self.center) == 0:
            return

        self.move_card(self.center[0]["game_card_id"], "backstage")
        self.move_card(back_id, "center")

    def add_turn_effect(self, turn_effect):
        self.turn_effects.append(turn_effect)

    def set_holomem_hp(self, card_id, target_hp):
        card, _, _ = self.find_card(card_id)
        if card["damage"] < card["hp"] - target_hp:
            previous_damage = card["damage"]
            card["damage"] = card["hp"] - target_hp
            modify_hp_event = {
                "event_type": EventType.EventType_ModifyHP,
                "target_player_id": self.player_id,
                "card_id": card_id,
                "damage_done": card["damage"] - previous_damage,
                "new_damage": card["damage"],
            }
            self.engine.broadcast_event(modify_hp_event)

    def restore_holomem_hp(self, card_id, amount):
        card, _, _ = self.find_card(card_id)
        healed_amount = 0
        if amount == "all":
            healed_amount = card["damage"]
        else:
            healed_amount = min(amount, card["damage"])
        if healed_amount > 0:
            card["damage"] -= healed_amount
            modify_hp_event = {
                "event_type": EventType.EventType_RestoreHP,
                "target_player_id": self.player_id,
                "card_id": card_id,
                "healed_amount": healed_amount,
                "new_damage": card["damage"],
            }
            self.engine.broadcast_event(modify_hp_event)

def ids_from_cards(cards):
    return [card["game_card_id"] for card in cards]

def replace_field_in_conditions(effect, field_id, replacement_value):
    if "conditions" in effect:
        conditions = effect["conditions"]
        for condition in conditions:
            if field_id in condition:
                condition[field_id] = replacement_value

def is_card_resting(card):
    return "resting" in card and card["resting"]

def add_ids_to_effects(effects, player_id, card_id):
    for effect in effects:
        effect["player_id"] = player_id
        if card_id:
            effect["source_card_id"] = card_id

def get_owner_id_from_card_id(card_id):
    return card_id.split("_")[0]

def art_requirement_met(card, art):
    attached_cheer_cards = [attached_card for attached_card in card["attached_cheer"] if is_card_cheer(attached_card)]

    white_cheer = 0
    green_cheer = 0
    blue_cheer = 0
    red_cheer = 0

    for attached_cheer_card in attached_cheer_cards:
        if "white" in attached_cheer_card["colors"]:
            white_cheer += 1
        elif "green" in attached_cheer_card["colors"]:
            green_cheer += 1
        elif "blue" in attached_cheer_card["colors"]:
            blue_cheer += 1
        elif "red" in attached_cheer_card["colors"]:
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
    card_type = attaching_card["card_type"]
    if card_type == "cheer":
        target_card["attached_cheer"].append(attaching_card)
    else:
        target_card["attached_support"].append(attaching_card)

def is_card_limited(card):
    return "limited" in card and card["limited"]

def is_card_mascot(card):
    return "sub_type" in card and card["sub_type"] == "mascot"

def is_card_event(card):
    return "sub_type" in card and card["sub_type"] == "event"

def is_card_tool(card):
    return "sub_type" in card and card["sub_type"] == "tool"

def is_card_item(card):
    return "sub_type" in card and card["sub_type"] == "item"

def is_card_cheer(card):
    return card["card_type"] == "cheer"

def filter_effects_at_timing(effects, timing):
    return deepcopy([effect for effect in effects if effect["timing"] == timing])

class GameEngine:
    def __init__(self,
        card_db:CardDatabase,
        game_type : str,
        player_infos : List[Dict[str, Any]],
    ):
        self.phase = GamePhase.Initializing
        self.game_first_turn = True
        self.card_db = card_db
        self.latest_events = []
        self.current_decision = None
        self.effect_resolution_state = None
        self.test_random_override = None
        self.turn_number = 0
        self.floating_cards = []
        self.down_holomem_state : DownHolomemState = None
        self.last_die_value = 0
        self.archive_count_required = 0
        self.remove_downed_holomems_to_hand = False
        self.after_damage_state : AfterDamageState = None
        self.last_chosen_cards = []
        self.last_card_count = 0

        self.damage_modifications = DamageModifications()
        self.performance_artstatboosts = ArtStatBoosts()
        self.performance_performing_player = None
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

    def set_random_test_hook(self, random_override):
        self.test_random_override = random_override

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

    def is_game_over(self):
        return self.phase == GamePhase.GameOver

    def find_card(self, game_card_id):
        for player_state in self.player_states:
            card, _, _ = player_state.find_card(game_card_id)
            if not card:
                for holomem in player_state.get_holomem_on_stage():
                    for attachment in holomem["attached_support"]:
                        if attachment["game_card_id"] == game_card_id:
                            card = attachment
                            return card
                    for cheer in holomem["attached_cheer"]:
                        if cheer["game_card_id"] == game_card_id:
                            card = cheer
                            return card
                    for stacked in holomem["stacked_cards"]:
                        if stacked["game_card_id"] == game_card_id:
                            card = stacked
                            return card
            else:
                return card
        if not card:
            raise Exception(f"Card not found: {game_card_id}")

    def begin_game(self):
        # Set the seed.
        self.random_gen = random.Random(self.seed)
        if self.test_random_override:
            self.random_gen = self.test_random_override

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
                "opponent_id": self.other_player(player_id).player_id,
                "game_card_map": self.all_game_cards_map,
            })

        # Draw starting hands
        for player_state in self.player_states:
            player_state.draw(STARTING_HAND_SIZE)

        self.phase = GamePhase.Mulligan
        self.active_player_id = self.starting_player_id

        self.handle_mulligan_phase()

    def handle_mulligan_phase(self):
        # Are both players done mulliganing?
        # If so, move on to the next phase.
        if all(player_state.mulligan_completed for player_state in self.player_states):
            self.process_forced_mulligans()
            self.begin_initial_placement()
        else:
            active_player = self.get_player(self.active_player_id)
            if active_player.mulligan_count == 0:
                # Tell the active player we're waiting on them to mulligan.
                decision_event = {
                    "event_type": EventType.EventType_MulliganDecision,
                    "desired_response": GameAction.Mulligan,
                    "active_player": self.active_player_id,
                }
                self.broadcast_event(decision_event)
            else:
                raise Exception("Unexpected: Player has already mulliganed.")

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
        self.send_initial_placement_event()

    def send_initial_placement_event(self):
        active_player = self.get_player(self.active_player_id)
        debut_options = []
        spot_options = []
        for card in active_player.hand:
            if card["card_type"] == "holomem_debut":
                debut_options.append(card["game_card_id"])
            elif card["card_type"] == "holomem_spot":
                spot_options.append(card["game_card_id"])

        decision_event = {
            "event_type": EventType.EventType_InitialPlacementBegin,
            "desired_response": GameAction.InitialPlacement,
            "active_player": self.active_player_id,
            "debut_options": debut_options,
            "spot_options": spot_options,
            "hidden_info_player": self.active_player_id,
            "hidden_info_fields": ["debut_options", "spot_options"],
            "hidden_info_erase": ["debut_options", "spot_options"],
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
                "event_type": EventType.EventType_InitialPlacementReveal,
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
            self.send_initial_placement_event()

    def begin_player_turn(self):
        self.phase = GamePhase.PlayerTurn
        active_player = self.get_player(self.active_player_id)

        # Send a start turn event.
        self.turn_number += 1
        start_event = {
            "event_type": EventType.EventType_TurnStart,
            "active_player": self.active_player_id,
            "turn_count": self.turn_number,
        }
        self.broadcast_event(start_event)

        # Reset Step
        if not active_player.first_turn:
            # 1. Activate resting cards.
            activated_cards = active_player.active_resting_cards()
            activation_event = {
                "event_type": EventType.EventType_ResetStepActivate,
                "active_player": self.active_player_id,
                "activated_card_ids": activated_cards,
            }
            self.broadcast_event(activation_event)

            # 2. Move and rest collab.
            rested_cards, moved_backstage_cards = active_player.reset_collab()
            reset_collab_event = {
                "event_type": EventType.EventType_ResetStepCollab,
                "active_player": self.active_player_id,
                "rested_card_ids": rested_cards,
                "moved_backstage_ids": moved_backstage_cards,
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
                        "event_type": EventType.EventType_ResetStepChooseNewCenter,
                        "desired_response": GameAction.ChooseNewCenter,
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
            self.end_game(loser_id=active_player.player_id, reason_id=GameOverReason.GameOverReason_DeckEmptyDraw)
            return

        active_player.draw(1)

        ## Cheer Step
        # Get the top cheer card id and send a decision.
        # Any holomem in center/collab/backstage can be the target.
        if len(active_player.cheer_deck) > 0:
            top_cheer_card_id = active_player.cheer_deck[0]["game_card_id"]
            target_options = ids_from_cards(active_player.center + active_player.collab + active_player.backstage)

            decision_event = {
                "event_type": EventType.EventType_CheerStep,
                "desired_response": GameAction.PlaceCheer,
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
                        "action_type": GameAction.MainStepPlaceHolomem,
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

                accepted_bloom_levels = active_player.get_accepted_bloom_for_card(mem_card)
                if accepted_bloom_levels:
                    for card in active_player.hand:
                        if "bloom_blocked" in card and card["bloom_blocked"]:
                            continue
                        if card["card_type"] == "holomem_bloom" and card["bloom_level"] in accepted_bloom_levels:
                            # Check the names of the bloom card, at last one must match a name from the base card.
                            if any(name in card["holomem_names"] for name in mem_card["holomem_names"]):
                                # Check the damage, if the bloom version would die, you can't.
                                if mem_card["damage"] < card["hp"]:
                                    available_actions.append({
                                        "action_type": GameAction.MainStepBloom,
                                        "card_id": card["game_card_id"],
                                        "target_id": mem_card["game_card_id"],
                                    })

        # C. Collab
        # Can't have collabed this turn.
        # Must have a card in deck to move to holopower.
        # Collab spot must be empty!
        # Must have a non-resting backstage card.
        if not active_player.collabed_this_turn and len(active_player.deck) > 0 and len(active_player.collab) == 0:
            for card in active_player.backstage:
                if not is_card_resting(card):
                    available_actions.append({
                        "action_type": GameAction.MainStepCollab,
                        "card_id": card["game_card_id"],
                    })

        # D. Use Oshi skills.
        for action in active_player.oshi_card["actions"]:
            skill_id = action["skill_id"]
            if action["limit"] == "once_per_turn" and active_player.has_used_once_per_turn_effect(skill_id):
                continue

            if action["limit"] == "once_per_game" and active_player.has_used_once_per_game_effect(skill_id):
                continue

            skill_cost = action["cost"]
            if skill_cost > len(active_player.holopower):
                continue

            available_actions.append({
                "action_type": GameAction.MainStepOshiSkill,
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
                    if not self.are_conditions_met(active_player, card["game_card_id"], card["play_conditions"]):
                        continue

                play_requirements = {}
                if "play_requirements" in card:
                    play_requirements = card["play_requirements"]

                cheer_on_each_mem = active_player.get_cheer_on_each_holomem(exclude_empty_members=True)
                available_actions.append({
                    "action_type": GameAction.MainStepPlaySupport,
                    "card_id": card["game_card_id"],
                    "play_requirements": play_requirements,
                    "cheer_on_each_mem": cheer_on_each_mem,
                })

        # F. Pass the baton
        # If center holomem is not resting, can swap with a back who is not resting by archiving Cheer.
        # Must be able to archive that much cheer from the center.
        if len(active_player.center) > 0:
            center_mem = active_player.center[0]
            cheer_on_mem = center_mem["attached_cheer"]
            baton_cost = center_mem["baton_cost"]
            if active_player.can_move_front_stage() and not active_player.baton_pass_this_turn and \
                not is_card_resting(center_mem) and len(cheer_on_mem) >= baton_cost:
                backstage_options = []
                for card in active_player.backstage:
                    if not is_card_resting(card):
                        backstage_options.append(card["game_card_id"])
                if backstage_options:
                    available_actions.append({
                        "action_type": GameAction.MainStepBatonPass,
                        "center_id": center_mem["game_card_id"],
                        "backstage_options": backstage_options,
                        "cost": baton_cost,
                        "available_cheer": ids_from_cards(cheer_on_mem),
                    })

        # G. Begin Performance
        if not (self.starting_player_id == active_player.player_id and active_player.first_turn):
            available_actions.append({
                "action_type": GameAction.MainStepBeginPerformance,
            })

        # H. End Turn
        available_actions.append({
            "action_type": GameAction.MainStepEndTurn,
        })

        return available_actions

    def send_main_step_actions(self):
        # Determine available actions.
        available_actions = self.get_available_mainstep_actions()

        decision_event = {
            "event_type": EventType.EventType_Decision_MainStep,
            "desired_response": GameAction.MainStepEndTurn,
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
        # Send a main step start event
        start_event = {
            "event_type": EventType.EventType_MainStepStart,
            "active_player": self.active_player_id,
        }
        self.broadcast_event(start_event)
        self.send_main_step_actions()

    def continue_main_step(self):
        self.send_main_step_actions()

    def end_player_turn(self):
        active_player = self.get_player(self.active_player_id)
        active_player.on_my_turn_end()
        other_player = self.other_player(self.active_player_id)
        active_player.clear_every_turn_effects()
        other_player.clear_every_turn_effects()

        # This is no longer the game's first turn.
        self.game_first_turn = False

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
        if len(available_actions) > 1:
            decision_event = {
                "event_type": EventType.EventType_Decision_PerformanceStep,
                "desired_response": GameAction.PerformanceStepEndTurn,
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
        else:
            # Can only end the turn, do it for them.
            self.end_player_turn()

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

            opponent_performers = self.other_player(self.active_player_id).get_holomem_on_stage(only_performers=True)
            if not opponent_performers:
                # We killed them all this turn.
                continue

            for art in performer["arts"]:
                if art_requirement_met(performer, art):
                    performer_position = "center" if active_player.is_center_holomem(performer["game_card_id"]) else "collab"
                    valid_targets = ids_from_cards(opponent_performers)
                    if "target_condition" in art:
                        match art["target_condition"]:
                            case "center_only":
                                valid_targets = ids_from_cards(self.other_player(self.active_player_id).center)

                    if len(valid_targets) > 0:
                        available_actions.append({
                            "action_type": GameAction.PerformanceStepUseArt,
                            "performer_id": performer["game_card_id"],
                            "performer_position": performer_position,
                            "art_id": art["art_id"],
                            "power": art["power"],
                            "art_effects": art.get("art_effects", []),
                            "valid_targets": valid_targets,
                        })

        # End Performance
        available_actions.append({
            "action_type": GameAction.PerformanceStepEndTurn,
        })

        return available_actions

    def begin_performance_step(self):
        # Send a start performance event.
        start_event = {
            "event_type": EventType.EventType_PerformanceStepStart,
            "active_player": self.active_player_id,
        }
        self.broadcast_event(start_event)
        self.continue_performance_step()

    def continue_performance_step(self):
        if self.performance_artstatboosts.repeat_art and self.performance_target_card["damage"] < self.performance_target_card["hp"]:
            self.begin_perform_art(
                self.performance_performer_card["game_card_id"],
                self.performance_art["art_id"],
                self.performance_target_card["game_card_id"],
                self.continue_performance_step
            )
        else:
            self.performance_artstatboosts.clear()
            self.send_performance_step_actions()

    def begin_perform_art(self, performer_id, art_id, target_id, continuation):
        player = self.get_player(self.active_player_id)
        performer, _, _ = player.find_card(performer_id)
        performer["used_art_this_turn"] = True
        target, _, _ = self.other_player(self.active_player_id).find_card(target_id)
        art = next(art for art in performer["arts"] if art["art_id"] == art_id)

        self.performance_artstatboosts = ArtStatBoosts()
        self.performance_performing_player = player
        self.performance_performer_card = performer
        self.performance_target_card = target
        self.performance_art = art
        self.performance_continuation = continuation

        # Get any before effects and resolve them.
        art_effects = filter_effects_at_timing(art.get("art_effects", []), "before_art")
        add_ids_to_effects(art_effects, player.player_id, performer_id)
        card_effects = player.get_effects_at_timing("before_art", performer)
        all_effects = card_effects + art_effects
        self.begin_resolving_effects(all_effects, self.continue_perform_art)

    def continue_perform_art(self):
        # Now all before effects have been resolved.
        # Actually do the art.
        total_power = self.performance_art["power"]
        total_power += self.performance_artstatboosts.power
        target_owner = self.get_player(self.performance_target_card["owner_id"])
        is_special_damage = "special" in self.performance_art and self.performance_art["special"]

        art_event = {
            "event_type": EventType.EventType_PerformArt,
            "active_player": self.active_player_id,
            "performer_id": self.performance_performer_card["game_card_id"],
            "art_id": self.performance_art["art_id"],
            "target_id": self.performance_target_card["game_card_id"],
            "target_player": target_owner.player_id,
            "power": total_power,
        }
        self.broadcast_event(art_event)
        active_player = self.get_player(self.active_player_id)

        # Deal damage.
        art_kill_effects = self.performance_art.get("on_kill_effects", [])
        add_ids_to_effects(art_kill_effects, self.active_player_id, self.performance_performer_card["game_card_id"])
        self.deal_damage(active_player, target_owner, self.performance_performer_card, self.performance_target_card, total_power, is_special_damage, False, art_kill_effects, self.performance_continuation)

    def deal_damage(self, dealing_player : PlayerState, target_player : PlayerState, dealing_card, target_card, damage, special, prevent_life_loss, art_kill_effects, continuation):
        if target_card["damage"] >= target_card["hp"]:
            # Already dead somehow!
            # Just call the continuation, you don't get to kill them twice.
            continuation()
            return

        target_card["damage"] += damage

        self.damage_modifications = DamageModifications()
        self.damage_modifications.source_player = dealing_player
        on_damage_effects = target_player.get_effects_at_timing("on_take_damage", target_card)
        self.begin_resolving_effects(on_damage_effects, lambda :
            self.continue_deal_damage(dealing_player, target_player, dealing_card, target_card, damage, special, prevent_life_loss, art_kill_effects, continuation)
        )

    def restore_holomem_hp(self, target_player : PlayerState, target_card_id, amount, continuation):
        target_player.restore_holomem_hp(target_card_id, amount)
        target_card, _, _ = target_player.find_card(target_card_id)
        on_restore_effects = target_player.get_effects_at_timing("on_restore_hp", target_card)
        self.begin_resolving_effects(on_restore_effects, continuation)

    def continue_deal_damage(self, dealing_player : PlayerState, target_player : PlayerState, dealing_card, target_card, damage, special, prevent_life_loss, art_kill_effects, continuation):
        if self.damage_modifications.prevented_damage:
            # Recalculate the damage based on prevented damage.
            target_card["damage"] -= damage
            damage = max(0, damage - self.damage_modifications.prevented_damage)
            target_card["damage"] += damage
        self.damage_modifications.clear()

        # Damage is decided here, so play the event.
        damage_event = {
            "event_type": EventType.EventType_DamageDealt,
            "target_id": target_card["game_card_id"],
            "target_player": target_player.player_id,
            "damage": damage,
            "special": special,
        }
        self.broadcast_event(damage_event)

        after_deal_damage_effects = dealing_player.get_effects_at_timing("after_deal_damage", dealing_card)
        nested_state = None
        if self.after_damage_state:
            nested_state = self.after_damage_state
        self.after_damage_state = AfterDamageState()
        self.after_damage_state.nested_state = nested_state
        self.after_damage_state.source_player = dealing_player
        self.after_damage_state.source_card = dealing_card
        self.after_damage_state.target_card = target_card
        self.after_damage_state.target_player = target_player
        self.after_damage_state.damage_dealt = damage

        self.begin_resolving_effects(after_deal_damage_effects, lambda :
            self.after_deal_damage_effects(dealing_player, target_player, dealing_card, target_card, damage, special, prevent_life_loss, art_kill_effects, continuation)
        )

    def after_deal_damage_effects(self, dealing_player : PlayerState, target_player : PlayerState, dealing_card, target_card, damage, special, prevent_life_loss, art_kill_effects, continuation):
        self.after_damage_state = self.after_damage_state.nested_state
        died = target_card["damage"] >= target_card["hp"]

        if died:
            self.begin_down_holomem(dealing_player, target_player, dealing_card, target_card, art_kill_effects, lambda :
                self.complete_deal_damage(target_player, target_card, damage, special, prevent_life_loss, died, continuation))
        else:
            # Continue processing the damage.
            self.complete_deal_damage(target_player, target_card, damage, special, prevent_life_loss, died, continuation)

    def complete_deal_damage(self, target_player : PlayerState, target_card, damage, special, prevent_life_loss, died, continuation):
        if died:
            self.process_downed_holomem(target_player, target_card, prevent_life_loss, continuation)
        else:
            continuation()

    def begin_down_holomem(self, dealing_player : PlayerState, target_player : PlayerState, dealing_card, target_card, arts_kill_effects, continuation):
        player_kill_effects = dealing_player.get_effects_at_timing("on_kill", dealing_card)
        down_effects = target_player.get_effects_at_timing("on_down", target_card)
        all_death_effects = arts_kill_effects + player_kill_effects + down_effects
        down_info = DownHolomemState()
        down_info.nested_state = self.down_holomem_state
        self.down_holomem_state = down_info
        self.down_holomem_state.holomem_card = target_card
        self.begin_resolving_effects(all_death_effects, continuation)

    def down_holomem(self, dealing_player : PlayerState, target_player : PlayerState, dealing_card, target_card, prevent_life_loss, continuation):
        self.begin_down_holomem(dealing_player, target_player, dealing_card, target_card, [], lambda :
            self.process_downed_holomem(target_player, target_card, prevent_life_loss, continuation)
        )

    def process_downed_holomem(self, target_player, target_card, prevent_life_loss, continuation):
        self.down_holomem_state = self.down_holomem_state.nested_state
        game_over = False
        game_over_reason = ""
        life_to_distribute = []
        life_lost = 0
        archived_ids = []
        hand_ids = []

        # Move all attached and stacked cards and the card itself to the archive.
        if self.remove_downed_holomems_to_hand:
            archived_ids, hand_ids = target_player.return_holomem_to_hand(target_card["game_card_id"], include_stacked_holomem=True)
            self.remove_downed_holomems_to_hand = False
        else:
            archived_ids = target_player.archive_holomem_from_play(target_card["game_card_id"])
        life_lost = 1
        if "down_life_cost" in target_card:
            life_lost = target_card["down_life_cost"]

        life_lost += self.performance_artstatboosts.bonus_life_loss

        if prevent_life_loss:
            life_lost = 0

        current_life = len(target_player.life)
        if life_lost >= current_life:
            game_over = True
            game_over_reason = GameOverReason.GameOverReason_NoLifeLeft
        elif len(target_player.get_holomem_on_stage()) == 0:
            game_over = True
            game_over_reason = GameOverReason.GameOverReason_NoHolomemsLeft

        if not game_over:
            life_to_distribute = ids_from_cards(target_player.life[:life_lost])

        # Sent the down event.
        down_event = {
            "event_type": EventType.EventType_DownedHolomem,
            "target_id": target_card["game_card_id"],
            "target_player": target_player.player_id,
            "life_lost": life_lost,
            "life_loss_prevented": prevent_life_loss,
            "game_over": game_over,
            "archived_ids": archived_ids,
            "hand_ids": hand_ids,
        }
        self.broadcast_event(down_event)

        if game_over:
            self.end_game(loser_id=target_player.player_id, reason_id=game_over_reason)
        elif life_to_distribute:
            # Tell the owner to distribute this life amongst their holomems.
            remaining_holomems = ids_from_cards(target_player.get_holomem_on_stage())
            cheer_on_each_mem = target_player.get_cheer_on_each_holomem()
            decision_event = {
                "event_type": EventType.EventType_Decision_SendCheer,
                "desired_response": GameAction.EffectResolution_MoveCheerBetweenHolomems,
                "effect_player_id": target_player.player_id,
                "amount_min": len(life_to_distribute),
                "amount_max": len(life_to_distribute),
                "from_zone": "life",
                "to_zone": "holomem",
                "from_options": life_to_distribute,
                "to_options": remaining_holomems,
                "cheer_on_each_mem": cheer_on_each_mem,
            }
            self.broadcast_event(decision_event)
            self.set_decision({
                "decision_type": DecisionType.DecisionEffect_MoveCheerBetweenHolomems,
                "decision_player": target_player.player_id,
                "amount_min": len(life_to_distribute),
                "amount_max": len(life_to_distribute),
                "available_cheer": life_to_distribute,
                "available_targets": remaining_holomems,
                "continuation": continuation,
            })
        else:
            continuation()

    def begin_resolving_effects(self, effects, continuation, cards_to_cleanup = []):
        effect_continuation = continuation
        if self.effect_resolution_state:
            # There is already an effects resolution going down.
            # The current resolution will continue after this one.
            outer_resolution_state = self.effect_resolution_state
            def new_continuation():
                # Reset the previous effect resolution state before calling the continuation.
                self.effect_resolution_state = outer_resolution_state
                continuation()
            effect_continuation = new_continuation
        self.effect_resolution_state = EffectResolutionState(effects, effect_continuation, cards_to_cleanup)
        self.continue_resolving_effects()

    def continue_resolving_effects(self):
        if not self.effect_resolution_state.effects_to_resolve:
            for cleanup_card in self.effect_resolution_state.cards_to_cleanup:
                # The card may have been removed from play by some effect (like attaching).
                if cleanup_card in self.floating_cards:
                    self.floating_cards.remove(cleanup_card)
                    owner = self.get_player(cleanup_card["owner_id"])
                    owner.archive.insert(0, cleanup_card)
                    cleanup_event = {
                        "event_type": EventType.EventType_MoveCard,
                        "moving_player_id": owner.player_id,
                        "from_zone": "floating",
                        "to_zone": "archive",
                        "zone_card_id": "",
                        "card_id": cleanup_card["game_card_id"],
                    }
                    self.broadcast_event(cleanup_event)

            continuation = self.effect_resolution_state.effect_resolution_continuation
            self.effect_resolution_state = None
            if not self.is_game_over():
                continuation()
            return

        passed_on_continuation = False
        while len(self.effect_resolution_state.effects_to_resolve) > 0 and not self.current_decision:
            effect = self.effect_resolution_state.effects_to_resolve.pop(0)
            effect_player_id = effect["player_id"]
            effect_player = self.get_player(effect_player_id)
            if "conditions" not in effect or self.are_conditions_met(effect_player, effect["source_card_id"], effect["conditions"]):
                # Add any "and" effects to the front of the queue.
                if "and" in effect:
                    and_effects = effect["and"]
                    add_ids_to_effects(and_effects, effect_player_id, effect.get("source_card_id", None))
                    self.effect_resolution_state.effects_to_resolve = and_effects + self.effect_resolution_state.effects_to_resolve
                passed_on_continuation = self.do_effect(effect_player, effect)
                if passed_on_continuation:
                    return
            else:
                # Failed conditions, add any negative condition effects to the front of the queue.
                if "negative_condition_effects" in effect:
                    negative_effects = effect["negative_condition_effects"]
                    add_ids_to_effects(negative_effects, effect_player_id, effect.get("source_card_id", None))
                    self.effect_resolution_state.effects_to_resolve = negative_effects + self.effect_resolution_state.effects_to_resolve

        if not self.current_decision:
            self.continue_resolving_effects()

    def are_conditions_met(self, effect_player: PlayerState, source_card_id, conditions):
        for condition in conditions:
           if not self.is_condition_met(effect_player, source_card_id, condition):
               return False
        return True

    def is_condition_met(self, effect_player: PlayerState, source_card_id, condition):
        match condition["condition"]:
            case Condition.Condition_AttachedTo:
                required_member_name = condition["required_member_name"]
                required_bloom_levels = condition.get("required_bloom_levels", [])
                # Determine if source_card_id is attached to a holomem with the required name.
                source_card = self.find_card(source_card_id)
                owner_player = self.get_player(source_card["owner_id"])
                holomems = owner_player.get_holomem_on_stage()
                for holomem in holomems:
                    if source_card_id in [card["game_card_id"] for card in holomem["attached_support"]]:
                        if required_member_name in holomem["holomem_names"]:
                            if not required_bloom_levels or holomem.get("bloom_level", -1) in required_bloom_levels:
                                return True
                return False
            case Condition.Condition_BloomTargetIsDebut:
                bloom_card, _, _ = effect_player.find_card(source_card_id)
                # Bloom target is always in the 0 slot.
                target_card = bloom_card["stacked_cards"][0]
                return target_card["card_type"] == "holomem_debut"
            case Condition.Condition_CanArchiveFromHand:
                amount_min = condition.get("amount_min", 1)
                condition_source = condition["condition_source"]
                return effect_player.can_archive_from_hand(amount_min, condition_source)
            case Condition.Condition_CanMoveFrontStage:
                return effect_player.can_move_front_stage()
            case Condition.Condition_CardsInHand:
                amount_min = condition.get("amount_min", -1)
                amount_max = condition.get("amount_max", -1)
                if amount_max == -1:
                    amount_max = UNLIMITED_SIZE
                return amount_min <= len(effect_player.hand) <= amount_max
            case Condition.Condition_CenterIsColor:
                if len(effect_player.center) == 0:
                    return False
                condition_colors = condition["condition_colors"]
                center_colors = effect_player.center[0]["colors"]
                if any(color in center_colors for color in condition_colors):
                    return True
            case Condition.Condition_CenterHasAnyTag:
                valid_tags = condition["condition_tags"]
                if len(effect_player.center) == 0:
                    return False
                center_card = effect_player.center[0]
                for tag in center_card["tags"]:
                    if tag in valid_tags:
                        return True
                return False
            case Condition.Condition_CheerInPlay:
                amount_min = condition["amount_min"]
                amount_max = condition["amount_max"]
                if amount_max == -1:
                    amount_max = UNLIMITED_SIZE
                return amount_min <= len(effect_player.get_cheer_ids_on_holomems()) <= amount_max
            case Condition.Condition_ChosenCardHasTag:
                if len(self.last_chosen_cards) == 0:
                    return False
                chosen_card_id = self.last_chosen_cards[0]
                chosen_card = self.find_card(chosen_card_id)
                valid_tags = condition["condition_tags"]
                return any(tag in chosen_card["tags"] for tag in valid_tags)
            case Condition.Condition_CollabWith:
                required_member_name = condition["required_member_name"]
                holomems = effect_player.get_holomem_on_stage(only_performers=True)
                return any(required_member_name in holomem["holomem_names"] for holomem in holomems)
            case Condition.Condition_DamageAbilityIsColor:
                condition_color = condition["condition_color"]
                include_oshi_ability = condition.get("include_oshi_ability", False)
                damage_source = self.after_damage_state.source_card
                if damage_source["card_type"] == "support":
                    # Find the owner card.
                    holomems = self.after_damage_state.source_player.get_holomems_with_attachment(damage_source["game_card_id"])
                    if holomems:
                        damage_source = holomems[0]
                elif damage_source["card_type"] == "oshi":
                    return include_oshi_ability
                return condition_color in damage_source["colors"]
            case Condition.Condition_DamagedHolomemIsBackstage:
                return self.after_damage_state.target_card in self.after_damage_state.target_player.backstage
            case Condition.Condition_DamagedHolomemIsCenterOrCollab:
                return self.after_damage_state.target_card in self.after_damage_state.target_player.center + self.after_damage_state.target_player.collab
            case Condition.Condition_DamageSourceIsOpponent:
                return self.damage_modifications.source_player.player_id != effect_player.player_id
            case Condition.Condition_DownedCardBelongsToOpponent:
                source_card = self.find_card(source_card_id)
                owner_player = self.get_player(source_card["owner_id"])
                return owner_player.player_id != self.down_holomem_state.holomem_card["owner_id"]
            case Condition.Condition_DownedCardIsColor:
                downed_card = self.down_holomem_state.holomem_card
                condition_color = condition["condition_color"]
                return condition_color in downed_card["colors"]
            case Condition.Condition_EffectCardIdNotUsedThisTurn:
                return not effect_player.has_used_card_effect_this_turn(source_card_id)
            case Condition.Condition_HasAttachmentOfType:
                attachment_type = condition["condition_type"]
                card, _, _ = effect_player.find_card(source_card_id)
                for attachment in card["attached_support"]:
                    if "sub_type" in attachment and attachment["sub_type"] == attachment_type:
                        return True
                return False
            case Condition.Condition_HolomemOnStage:
                required_member_name = condition["required_member_name"]
                holomems = effect_player.get_holomem_on_stage()
                return any(required_member_name in holomem["holomem_names"] for holomem in holomems)
            case Condition.Condition_HolopowerAtLeast:
                amount = condition["amount"]
                return len(effect_player.holopower) >= amount
            case Condition.Condition_NotUsedOncePerGameEffect:
                condition_effect_id = condition["condition_effect_id"]
                return not effect_player.has_used_once_per_game_effect(condition_effect_id)
            case Condition.Condition_NotUsedOncePerTurnEffect:
                condition_effect_id = condition["condition_effect_id"]
                return not effect_player.has_used_once_per_turn_effect(condition_effect_id)
            case Condition.Condition_OpponentTurn:
                return self.active_player_id != effect_player.player_id
            case Condition.Condition_OshiIs:
                required_member_name = condition["required_member_name"]
                return required_member_name == effect_player.oshi_card["oshi_name"]
            case Condition.Condition_PerformanceTargetHasDamageOverHp:
                amount = condition["amount"]
                return self.performance_target_card["damage"] >= self.performance_target_card["hp"] + amount
            case Condition.Condition_PerformerIsCenter:
                if len(self.performance_performing_player.center) == 0:
                    return False
                return self.performance_performing_player.center[0]["game_card_id"] == self.performance_performer_card["game_card_id"]
            case Condition.Condition_PerformerIsColor:
                condition_colors = condition["condition_colors"]
                for color in self.performance_performer_card["colors"]:
                    if color in condition_colors:
                        return True
                return False
            case Condition.Condition_PerformerIsSpecificId:
                required_id = condition["required_id"]
                return self.performance_performer_card["game_card_id"] == required_id
            case Condition.Condition_PerformerHasAnyTag:
                valid_tags = condition["condition_tags"]
                for tag in self.performance_performer_card["tags"]:
                    if tag in valid_tags:
                        return True
                return False
            case Condition.Condition_PlayedSupportThisTurn:
                return effect_player.played_support_this_turn
            case Condition.Condition_SelfHasCheer:
                amount_min = condition["amount_min"]
                source_card, _, _ = effect_player.find_card(source_card_id)
                if source_card:
                    return amount_min <= len(source_card["attached_cheer"])
                return False
            case Condition.Condition_SelfHasCheerColor:
                condition_colors = condition["condition_colors"]
                source_card, _, _ = effect_player.find_card(source_card_id)
                if source_card:
                    for cheer in source_card["attached_cheer"]:
                        if any(color in cheer["colors"] for color in condition_colors):
                            return True
                return False
            case Condition.Condition_StageHasSpace:
                return len(effect_player.get_holomem_on_stage()) < MAX_MEMBERS_ON_STAGE
            case Condition.Condition_TargetColor:
                color_requirement = condition["color_requirement"]
                return color_requirement in self.performance_target_card["colors"]
            case Condition.Condition_TargetHasAnyTag:
                valid_tags = condition["condition_tags"]
                for tag in self.performance_target_card["tags"]:
                    if tag in valid_tags:
                        return True
                return False
            case Condition.Condition_ThisCardIsCollab:
                if len(effect_player.collab) == 0:
                    return False
                return effect_player.collab[0]["game_card_id"] == source_card_id
            case Condition.Condition_TopDeckCardHasAnyTag:
                valid_tags = condition["condition_tags"]
                if len(effect_player.deck) == 0:
                    return False
                top_card = effect_player.deck[0]
                for tag in top_card["tags"]:
                    if tag in valid_tags:
                        return True
                return False
            case _:
                raise NotImplementedError(f"Unimplemented condition: {condition['condition']}")
        return False

    def do_effect(self, effect_player : PlayerState, effect):
        effect_player_id = effect_player.player_id
        if "pre_effects" in effect:
            # Do any do pre_effects right away (Assumption: no decisions/sub effects).
            do_before_effects = effect["pre_effects"]
            add_ids_to_effects(do_before_effects, effect_player_id, effect.get("source_card_id", None))
            for do_before in do_before_effects:
                self.do_effect(effect_player, do_before)

        passed_on_continuation = False
        match effect["effect_type"]:
            case EffectType.EffectType_AddTurnEffect:
                effect["turn_effect"]["source_card_id"] = effect["source_card_id"]
                effect_player.add_turn_effect(effect["turn_effect"])
                event = {
                    "event_type": EventType.EventType_AddTurnEffect,
                    "effect_player_id": effect_player_id,
                    "turn_effect": effect["turn_effect"],
                }
                self.broadcast_event(event)
            case EffectType.EffectType_AddTurnEffectForHolomem:
                holomem_targets = ids_from_cards(effect_player.get_holomem_on_stage())
                turn_effect_copy = deepcopy(effect["turn_effect"])
                turn_effect_copy["source_card_id"] = effect["source_card_id"]
                if len(holomem_targets) == 1:
                    replace_field_in_conditions(turn_effect_copy, "required_id", holomem_targets[0])
                    effect_player.add_turn_effect(turn_effect_copy)
                    event = {
                        "event_type": EventType.EventType_AddTurnEffect,
                        "effect_player_id": effect_player_id,
                        "turn_effect": turn_effect_copy,
                    }
                    self.broadcast_event(event)
                else:
                    # Ask the player to choose one.
                    decision_event = {
                        "event_type": EventType.EventType_Decision_ChooseHolomemForEffect,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "cards_can_choose": holomem_targets,
                        "effect": effect,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": holomem_targets,
                        "cards_can_choose": holomem_targets,
                        "amount_min": 1,
                        "amount_max": 1,
                        "turn_effect": turn_effect_copy,
                        "effect_resolution": self.handle_add_turn_effect_for_holomem,
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_AfterArchiveCheerCheck:
                previous_archive_count = effect["previous_archive_count"]
                current_archive_count = len(effect_player.archive)
                ability_source = effect["ability_source"]
                if previous_archive_count < current_archive_count:
                    # The player archived some amount of cheer.
                    after_archive_effects = effect_player.get_effects_at_timing("after_archive_cheer", None, ability_source)
                    self.begin_resolving_effects(after_archive_effects, self.continue_resolving_effects)
                    passed_on_continuation = True
            case EffectType.EffectType_ArchiveCheerFromHolomem:
                amount = effect["amount"]
                from_zone = effect["from"]
                target_holomems = []
                ability_source = effect["ability_source"]
                match from_zone:
                    case "self":
                        source_card, _, _ = effect_player.find_card(effect["source_card_id"])
                        target_holomems.append(source_card)
                cheer_options = []
                for holomem in target_holomems:
                    cheer_options += ids_from_cards(holomem["attached_cheer"])
                after_archive_check_effect = {
                    "player_id": effect_player_id,
                    "effect_type": EffectType.EffectType_AfterArchiveCheerCheck,
                    "effect_player_id": effect_player_id,
                    "previous_archive_count": len(effect_player.archive),
                    "ability_source": ability_source
                }
                self.add_effects_to_front([after_archive_check_effect])
                if amount == len(cheer_options):
                    # Do it immediately.
                    effect_player.archive_attached_cards(cheer_options)
                else:
                    choose_event = {
                        "event_type": EventType.EventType_Decision_ChooseCards,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "all_card_seen": cheer_options,
                        "cards_can_choose": cheer_options,
                        "from_zone": "holomem",
                        "to_zone": "archive",
                        "amount_min": amount,
                        "amount_max": amount,
                        "reveal_chosen": True,
                        "remaining_cards_action": "nothing",
                    }
                    self.broadcast_event(choose_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": cheer_options,
                        "cards_can_choose": cheer_options,
                        "from_zone": "holomem",
                        "to_zone": "archive",
                        "amount_min": amount,
                        "amount_max": amount,
                        "reveal_chosen": True,
                        "remaining_cards_action": "nothing",
                        "source_card_id": effect["source_card_id"],
                        "effect_resolution": self.handle_choose_cards_result,
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_ArchiveFromHand:
                amount = effect["amount"]
                ability_source = effect["ability_source"]
                self.archive_count_required = amount
                before_archive_effects = effect_player.get_effects_at_timing("before_archive", None, ability_source)
                def archive_hand_continuation():
                    if self.archive_count_required > 0:
                        # Ask the player to pick cards from their hand to archive.
                        cards_can_choose = ids_from_cards(effect_player.hand)
                        choose_event = {
                            "event_type": EventType.EventType_Decision_ChooseCards,
                            "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                            "effect_player_id": effect_player_id,
                            "all_card_seen": cards_can_choose,
                            "cards_can_choose": cards_can_choose,
                            "from_zone": "hand",
                            "to_zone": "archive",
                            "amount_min": self.archive_count_required,
                            "amount_max": self.archive_count_required,
                            "reveal_chosen": True,
                            "remaining_cards_action": "nothing",
                            "hidden_info_player": effect_player_id,
                            "hidden_info_fields": ["all_card_seen", "cards_can_choose"],
                        }
                        self.broadcast_event(choose_event)
                        self.set_decision({
                            "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                            "decision_player": effect_player_id,
                            "all_card_seen": cards_can_choose,
                            "cards_can_choose": cards_can_choose,
                            "from_zone": "hand",
                            "to_zone": "archive",
                            "amount_min": self.archive_count_required,
                            "amount_max": self.archive_count_required,
                            "reveal_chosen": True,
                            "remaining_cards_action": "nothing",
                            "source_card_id": effect["source_card_id"],
                            "effect_resolution": self.handle_choose_cards_result,
                            "continuation": self.continue_resolving_effects,
                        })
                    else:
                        self.continue_resolving_effects()
                self.begin_resolving_effects(before_archive_effects, archive_hand_continuation)
                passed_on_continuation = True
            case EffectType.EffectType_ArchiveFromHandVariable:
                pass
            case EffectType.EffectType_AttachCardToHolomem:
                source_card_id = effect["source_card_id"]
                continuation = self.continue_resolving_effects
                if "continuation" in effect:
                    # This effect can be called from elsewhere, so use special continuations
                    # if they were added on.
                    continuation = effect["continuation"]
                holomem_targets = effect_player.get_holomem_on_stage()
                to_limitation = effect.get("to_limitation", "")
                to_limitation_colors = effect.get("to_limitation_colors", [])
                match to_limitation:
                    case "color_in":
                        holomem_targets = [holomem for holomem in holomem_targets \
                            if any(color in holomem["colors"] for color in to_limitation_colors)]
                if len(holomem_targets) > 0:
                    attach_effect = {
                        "effect_type": EffectType.EffectType_AttachCardToHolomem_Internal,
                        "effect_player_id": effect_player.player_id,
                        "card_id": source_card_id,
                        "card_ids": [], # Filled in by the decision.
                        "to_limitation": to_limitation,
                        "to_limitation_colors": to_limitation_colors
                    }
                    add_ids_to_effects([attach_effect], effect_player.player_id, source_card_id)
                    decision_event = {
                        "event_type": EventType.EventType_Decision_ChooseHolomemForEffect,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player.player_id,
                        "cards_can_choose": ids_from_cards(holomem_targets),
                        "effect": attach_effect,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player.player_id,
                        "all_card_seen": ids_from_cards(holomem_targets),
                        "cards_can_choose": ids_from_cards(holomem_targets),
                        "amount_min": 1,
                        "amount_max": 1,
                        "effect_to_run": attach_effect,
                        "effect_resolution": self.handle_run_single_effect,
                        "continuation": continuation,
                    })
                else:
                    continuation()
                    passed_on_continuation = True
            case EffectType.EffectType_AttachCardToHolomem_Internal:
                card_to_attach_id = effect["card_id"]
                card_to_attach = None
                card_to_attach, _, _ = effect_player.find_card(card_to_attach_id)
                target_holomem_id = effect["card_ids"][0]
                target_holomem, _, _ = effect_player.find_card(target_holomem_id)
                if card_to_attach["card_type"] == "support" and card_to_attach["sub_type"] in ["mascot", "tool"]:
                    # You can only have 1 of each attached mascot/tool, so if they have one attached,
                    # then move it to archive.
                    for attached_support in target_holomem["attached_support"]:
                        if attached_support["sub_type"] == card_to_attach["sub_type"]:
                            effect_player.archive_attached_cards([attached_support["game_card_id"]])
                            break
                effect_player.move_card(card_to_attach_id, "holomem", target_holomem_id)
            case EffectType.EffectType_BlockOpponentMovement:
                other_player = self.other_player(effect_player_id)
                other_player.block_movement_for_turn = True
            case EffectType.EffectType_Choice:
                choice = deepcopy(effect["choice"])
                if "choice_populate_amount_x" in effect:
                    match effect["choice_populate_amount_x"]:
                        case "equal_to_last_damage":
                            for option in choice:
                                if "amount" in option and option["amount"] == "X":
                                    option["amount"] = self.after_damage_state.damage_dealt
                add_ids_to_effects(choice, effect_player_id, effect.get("source_card_id", None))
                self.send_choice_to_player(effect_player_id, choice)
            case EffectType.EffectType_ChooseCards:
                from_zone = effect["from"]
                destination = effect["destination"]
                look_at = effect["look_at"]
                amount_min = effect["amount_min"]
                amount_max = effect["amount_max"]
                requirement = effect.get("requirement", None)
                requirement_bloom_levels = effect.get("requirement_bloom_levels", [])
                requirement_buzz_blocked = effect.get("requirement_buzz_blocked", False)
                requirement_names = effect.get("requirement_names", [])
                requirement_tags = effect.get("requirement_tags", [])
                requirement_id = effect.get("requirement_id", "")
                requirement_match_oshi_color = effect.get("requirement_match_oshi_color", False)
                reveal_chosen = effect.get("reveal_chosen", False)
                remaining_cards_action = effect["remaining_cards_action"]
                after_choose_effect = effect.get("after_choose_effect", None)
                requirement_details = {
                    "requirement": requirement,
                    "requirement_bloom_levels": requirement_bloom_levels,
                    "requirement_buzz_blocked": requirement_buzz_blocked,
                    "requirement_names": requirement_names,
                    "requirement_tags": requirement_tags,
                    "requirement_id": requirement_id,
                    "requirement_match_oshi_color": requirement_match_oshi_color,
                }

                cards_to_choose_from = []
                match from_zone:
                    case "archive":
                        cards_to_choose_from = effect_player.archive
                    case "cheer_deck":
                        cards_to_choose_from = effect_player.cheer_deck
                    case "deck":
                        cards_to_choose_from = effect_player.deck
                    case "hand":
                        cards_to_choose_from = effect_player.hand
                    case "holopower":
                        cards_to_choose_from = effect_player.holopower

                # If look_at is -1, look at all cards.
                if look_at == -1:
                    look_at = len(cards_to_choose_from)

                # If look_at is greater than the number of cards, look at as many as you can.
                look_at = min(look_at, len(cards_to_choose_from))

                cards_to_choose_from = cards_to_choose_from[:look_at]
                cards_can_choose = cards_to_choose_from
                if requirement:
                    match requirement:
                        case "color_in":
                            requirement_colors = effect.get("requirement_colors", [])
                            cards_can_choose = [card for card in cards_can_choose if any(color in card["colors"] for color in requirement_colors)]
                        case "color_matches_holomems":
                            # Only include cards that match the colors of the holomems on stage.
                            cards_can_choose = [card for card in cards_can_choose if effect_player.matches_stage_holomems_color(card["colors"])]
                        case "specific_card":
                            cards_can_choose = [card for card in cards_can_choose if card["card_id"] == requirement_id]
                        case "holomem":
                            cards_can_choose = [card for card in cards_can_choose if card["card_type"] in ["holomem_bloom", "holomem_debut", "holomem_spot" ]]
                        case "holomem_bloom":
                            cards_can_choose = [card for card in cards_can_choose if card["card_type"] == "holomem_bloom"]
                        case "holomem_debut":
                            cards_can_choose = [card for card in cards_can_choose if card["card_type"] == "holomem_debut"]
                        case "holomem_debut_or_bloom":
                            cards_can_choose = [card for card in cards_can_choose if card["card_type"] in ["holomem_bloom", "holomem_debut"]]
                        case "holomem_named":
                            # Only include cards that have a name in the requirement_names list.
                            cards_can_choose = [card for card in cards_can_choose \
                                if "holomem_names" in card and any(name in card["holomem_names"] for name in requirement_names)]
                        case "limited":
                            # only include cards that are limited
                            cards_can_choose = [card for card in cards_can_choose if is_card_limited(card)]
                        case "item":
                            # Only include cards that are items.
                            cards_can_choose = [card for card in cards_can_choose if is_card_item(card)]
                        case "mascot":
                            # Only include cards that are mascots.
                            cards_can_choose = [card for card in cards_can_choose if is_card_mascot(card)]
                        case "tool":
                            # Only include cards that are tools.
                            cards_can_choose = [card for card in cards_can_choose if is_card_tool(card)]
                        case "event":
                            # Only include cards that are events.
                            cards_can_choose = [card for card in cards_can_choose if is_card_event(card)]
                        case "cheer":
                            # Only include cards that are cheer.
                            cards_can_choose = [card for card in cards_can_choose if is_card_cheer(card)]

                    # Exclude any based on bloom level.
                    if requirement_bloom_levels:
                        cards_can_choose = [card for card in cards_can_choose if "bloom_level" not in card or card["bloom_level"] in requirement_bloom_levels]

                    # Exclude any buzz if required.
                    if requirement_buzz_blocked:
                        cards_can_choose = [card for card in cards_can_choose if "buzz" not in card or not card["buzz"]]

                    # Restrict to only tagged cards.
                    if requirement_tags:
                        cards_can_choose = [card for card in cards_can_choose if any(tag in card["tags"] for tag in requirement_tags)]

                    # Restrict to oshi color.
                    if requirement_match_oshi_color:
                        cards_can_choose = [card for card in cards_can_choose if effect_player.matches_oshi_color(card["colors"])]

                if len(cards_can_choose) < amount_min:
                    amount_min = len(cards_can_choose)

                choose_event = {
                    "event_type": EventType.EventType_Decision_ChooseCards,
                    "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                    "effect_player_id": effect_player_id,
                    "all_card_seen": ids_from_cards(cards_to_choose_from),
                    "cards_can_choose": ids_from_cards(cards_can_choose),
                    "from_zone": from_zone,
                    "to_zone": destination,
                    "amount_min": amount_min,
                    "amount_max": amount_max,
                    "reveal_chosen": reveal_chosen,
                    "remaining_cards_action": remaining_cards_action,
                    "hidden_info_player": effect_player_id,
                    "hidden_info_fields": ["all_card_seen", "cards_can_choose"],
                    "requirement_details": requirement_details,
                }
                self.broadcast_event(choose_event)
                self.set_decision({
                    "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                    "decision_player": effect_player_id,
                    "all_card_seen": ids_from_cards(cards_to_choose_from),
                    "cards_can_choose": ids_from_cards(cards_can_choose),
                    "from_zone": from_zone,
                    "to_zone": destination,
                    "to_limitation": effect.get("to_limitation", ""),
                    "to_limitation_colors": effect.get("to_limitation_colors", []),
                    "amount_min": amount_min,
                    "amount_max": amount_max,
                    "reveal_chosen": reveal_chosen,
                    "remaining_cards_action": remaining_cards_action,
                    "after_choose_effect": after_choose_effect,
                    "source_card_id": effect["source_card_id"],
                    "effect_resolution": self.handle_choose_cards_result,
                    "continuation": self.continue_resolving_effects,
                })
            case EffectType.EffectType_DealDamage:
                special = effect.get("special", False)
                target = effect["target"]
                opponent = effect.get("opponent", False)
                amount = effect["amount"]
                prevent_life_loss = effect.get("prevent_life_loss", False)
                source_player = self.get_player(effect_player_id)
                target_player = effect_player
                if opponent:
                    target_player = self.other_player(effect_player_id)
                source_holomem_card, _, _ = source_player.find_card(effect["source_card_id"])
                if effect["source_card_id"] == "oshi":
                    source_holomem_card = source_player.oshi_card
                elif not source_holomem_card:
                    # Assume this is an attachment, find it on the holomem.
                    for holomem in source_player.get_holomem_on_stage():
                        for attachment in holomem["attached_support"]:
                            if attachment["game_card_id"] == effect["source_card_id"]:
                                source_holomem_card = holomem
                                break
                target_cards = []
                match target:
                    case "backstage":
                        target_cards = target_player.backstage
                    case "center":
                        target_cards = target_player.center
                    case "collab":
                        target_cards = target_player.collab
                    case "center_or_collab":
                        target_cards = target_player.center + target_player.collab
                    case "holomem":
                        target_cards = target_player.get_holomem_on_stage()
                    case "self":
                        target_cards = [source_holomem_card]
                    case _:
                        raise NotImplementedError("Only center is supported for now.")

                # Filter out any target cards that already have damage over their hp.
                target_cards = [card for card in target_cards if card["damage"] < card["hp"]]
                if len(target_cards) == 0:
                    pass
                elif len(target_cards) == 1:
                    self.deal_damage(source_player, target_player, source_holomem_card, target_cards[0], amount, special, prevent_life_loss, [], self.continue_resolving_effects)
                    passed_on_continuation = True
                else:
                    # Player gets to choose.
                    # Choose holomem for effect.
                    target_options = ids_from_cards(target_cards)
                    decision_event = {
                        "event_type": EventType.EventType_Decision_ChooseHolomemForEffect,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "cards_can_choose": target_options,
                        "effect": effect,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": target_options,
                        "cards_can_choose": target_options,
                        "amount_min": 1,
                        "amount_max": 1,
                        "effect_resolution": self.handle_deal_damage_to_holomem,
                        "effect": effect,
                        "source_card": source_holomem_card,
                        "target_player": target_player,
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_DownHolomem:
                target = effect["target"]
                required_damage = effect["required_damage"]
                prevent_life_loss = effect.get("prevent_life_loss", False)
                source_player = self.get_player(effect_player_id)
                target_player = self.other_player(effect_player_id)
                source_holomem_card, _, _ = source_player.find_card(effect["source_card_id"])
                if effect["source_card_id"] == "oshi":
                    source_holomem_card = source_player.oshi_card
                elif not source_holomem_card:
                    # Assume this is an attachment, find it on the holomem.
                    for holomem in source_player.get_holomem_on_stage():
                        for attachment in holomem["attached_support"]:
                            if attachment["game_card_id"] == effect["source_card_id"]:
                                source_holomem_card = holomem
                                break

                target_cards = []
                match target:
                    case "backstage":
                        target_cards = target_player.backstage
                    case "center":
                        target_cards = target_player.center
                    case "collab":
                        target_cards = target_player.collab
                    case "center_or_collab":
                        target_cards = target_player.center + target_player.collab
                    case "holomem":
                        target_cards = target_player.get_holomem_on_stage()
                    case _:
                        raise NotImplementedError("Missing target type")
                # Restrict to the required damage
                target_cards = [card for card in target_cards if card["damage"] >= required_damage]
                if len(target_cards) == 0:
                    pass
                elif len(target_cards) == 1:
                    self.down_holomem(source_player, target_player, source_holomem_card, target_cards[0], prevent_life_loss, self.continue_resolving_effects)
                    passed_on_continuation = True
                else:
                    # Player gets to choose.
                    # Choose holomem for effect.
                    target_options = ids_from_cards(target_cards)
                    decision_event = {
                        "event_type": EventType.EventType_Decision_ChooseHolomemForEffect,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "cards_can_choose": target_options,
                        "effect": effect,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": target_options,
                        "cards_can_choose": target_options,
                        "amount_min": 1,
                        "amount_max": 1,
                        "effect_resolution": self.handle_down_holomem,
                        "effect": effect,
                        "source_card": source_holomem_card,
                        "target_player": target_player,
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_Draw:
                amount = effect["amount"]
                if str(amount) == "last_card_count":
                    amount = self.last_card_count
                    self.last_card_count = 0
                if amount > 0:
                    target_player = effect_player
                    if effect.get("opponent", False):
                        target_player = self.other_player(effect_player_id)
                    target_player.draw(amount)
            case EffectType.EffectType_ForceDieResult:
                die_result = effect["die_result"]
                effect_player.set_next_die_roll = die_result
            case EffectType.EffectType_GenerateChoiceTemplate:
                template_choice = effect["template_choice"]
                starts_at = effect["starts_at"]
                ends_at = effect["ends_at"]
                usage_count_restriction = effect["usage_count_restriction"]
                can_pass = effect.get("can_pass", False)
                max_count = ends_at
                multi_value = effect.get("multi_value", 1)
                match ends_at:
                    case "archive_count_required":
                        max_count = self.archive_count_required
                        # Check to see if the starts_at and pass have to change.
                        holopower_available = len(effect_player.holopower)
                        cards_in_hand = len(effect_player.hand)
                        must_pay_with_holo = self.archive_count_required - cards_in_hand
                        if must_pay_with_holo > 0:
                            starts_at = max(starts_at, must_pay_with_holo)
                            can_pass = False
                match usage_count_restriction:
                    case "available_archive_from_hand":
                        ability_source = effect["ability_source"]
                        max_count = min(max_count, effect_player.get_can_archive_from_hand_count(ability_source))
                    case "holopower":
                        max_count = min(len(effect_player.holopower), max_count)
                choices = []
                for i in range(starts_at, max_count + 1):
                    # Populate the "amount": "X"/"multiX" fields.
                    new_choice = deepcopy(template_choice)
                    if "amount" in new_choice:
                        match new_choice["amount"]:
                            case "multiX":
                                new_choice["amount"] = i * multi_value
                            case "X":
                                new_choice["amount"] = i
                    if "cost" in new_choice:
                        match new_choice["cost"]:
                            case "X":
                                new_choice["cost"] = i
                    if "pre_effects" in new_choice:
                        for pre_effect in new_choice["pre_effects"]:
                            if "amount" in pre_effect:
                                match pre_effect["amount"]:
                                    case "multiX":
                                        pre_effect["amount"] = i * multi_value
                                    case "X":
                                        pre_effect["amount"] = i
                    if "and" in new_choice:
                        for and_effect in new_choice["and"]:
                            if "amount" in and_effect:
                                match and_effect["amount"]:
                                    case "multiX":
                                        and_effect["amount"] = i * multi_value
                                    case "X":
                                        and_effect["amount"] = i
                    choices.append(new_choice)
                if can_pass:
                    choices.append({ "effect_type": EffectType.EffectType_Pass })
                # Now do this as a choice effect.
                add_ids_to_effects(choices, effect_player_id, effect.get("source_card_id", None))
                if len(choices) == 1:
                    # There is no choice, the player has to do the effect.
                    self.do_effect(effect_player, choices[0])
                else:
                    self.send_choice_to_player(effect_player_id, choices)
            case EffectType.EffectType_GenerateHolopower:
                amount = effect["amount"]
                effect_player.generate_holopower(amount)
            case EffectType.EffectType_OshiActivation:
                skill_id = effect["skill_id"]
                oshi_skill_event = {
                    "event_type": EventType.EventType_OshiSkillActivation,
                    "oshi_player_id": effect_player.player_id,
                    "skill_id": skill_id,
                }
                self.broadcast_event(oshi_skill_event)
            case EffectType.EffectType_MoveCheerBetweenHolomems:
                amount = effect["amount"]
                available_cheer = effect_player.get_cheer_ids_on_holomems()
                available_targets = ids_from_cards(effect_player.get_holomem_on_stage())
                cheer_on_each_mem = effect_player.get_cheer_on_each_holomem()
                if len(available_targets) > 0:
                    decision_event = {
                        "event_type": EventType.EventType_Decision_SendCheer,
                        "desired_response": GameAction.EffectResolution_MoveCheerBetweenHolomems,
                        "effect_player_id": effect_player_id,
                        "amount_min": amount,
                        "amount_max": amount,
                        "from_zone": "holomem",
                        "to_zone": "holomem",
                        "from_options": available_cheer,
                        "to_options": available_targets,
                        "cheer_on_each_mem": cheer_on_each_mem,
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
            case EffectType.EffectType_OrderCards:
                for_opponent = effect.get("opponent", False)
                from_zone = effect["from"]
                to_zone = effect["destination"]
                bottom = effect.get("bottom", False)
                order_player = effect_player
                if for_opponent:
                    order_player = self.other_player(effect_player_id)
                cards_to_order = []
                match from_zone:
                    case "hand":
                        cards_to_order = ids_from_cards(order_player.hand)
                self.last_card_count = len(cards_to_order)
                self.choose_cards_cleanup_remaining(order_player.player_id, cards_to_order, "order_on_bottom", from_zone, to_zone,
                    self.continue_resolving_effects
                )
                passed_on_continuation = True
            case EffectType.EffectType_Pass:
                pass
            case EffectType.EffectType_PerformanceLifeLostIncrease:
                amount = effect["amount"]
                self.performance_artstatboosts.bonus_life_loss += amount
            case EffectType.EffectType_PlaceHolomem:
                card_id = effect["card_id"]
                to_zone = effect["location"]
                effect_player.move_card(card_id, to_zone)
            case EffectType.EffectType_PowerBoost:
                amount = effect["amount"]
                multiplier = 1
                if "multiplier" in effect:
                    match effect["multiplier"]:
                        case "last_die_value":
                            multiplier = self.last_die_value
                amount *= multiplier
                self.performance_artstatboosts.power += amount
                self.send_boost_event(self.performance_performer_card["game_card_id"], "power", amount)
            case EffectType.EffectType_PowerBoostPerBackstage:
                per_amount = effect["amount"]
                backstage_mems = len(effect_player.backstage)
                total = per_amount * backstage_mems
                self.performance_artstatboosts.power += total
                self.send_boost_event(self.performance_performer_card["game_card_id"], "power", total)
            case EffectType.EffectType_PowerBoostPerHolomem:
                per_amount = effect["amount"]
                holomems = effect_player.get_holomem_on_stage()
                if "has_tag" in effect:
                    holomems = [holomem for holomem in holomems if effect["has_tag"] in holomem["tags"]]
                total = per_amount * len(holomems)
                self.performance_artstatboosts.power += total
                self.send_boost_event(self.performance_performer_card["game_card_id"], "power", total)
            case EffectType.EffectType_PowerBoostPerStacked:
                per_amount = effect["amount"]
                stacked_cards = self.performance_performer_card.get("stacked_cards", [])
                stacked_holomems = [card for card in stacked_cards if card["card_type"] in ["holomem_debut", "holomem_bloom", "holomem_spot"]]
                total = per_amount * len(stacked_holomems)
                self.performance_artstatboosts.power += total
                self.send_boost_event(self.performance_performer_card["game_card_id"], "power", total)
            case EffectType.EffectType_RecordEffectCardIdUsedThisTurn:
                effect_player.record_card_effect_used_this_turn(effect["source_card_id"])
            case EffectType.EffectType_RecordUsedOncePerGameEffect:
                effect_player.record_effect_used_this_game(effect["effect_id"])
            case EffectType.EffectType_RecordUsedOncePerTurnEffect:
                effect_player.record_effect_used_this_turn(effect["effect_id"])
            case EffectType.EffectType_RecoverDownedHolomemCards:
                self.remove_downed_holomems_to_hand = True
            case EffectType.EffectType_ReduceDamage:
                amount = effect["amount"]
                if str(amount) == "all":
                    amount_num = 9999
                else:
                    amount_num = amount
                self.damage_modifications.prevented_damage += amount_num
                self.send_boost_event("", "damage_prevented", amount)
            case EffectType.EffectType_ReduceRequiredArchiveCount:
                amount = effect["amount"]
                self.archive_count_required -= amount
            case EffectType.EffectType_RepeatArt:
                self.performance_artstatboosts.repeat_art = True
            case EffectType.EffectType_RestoreHp:
                target = effect["target"]
                amount = effect["amount"]
                limitation = effect.get("limitation", "")
                limitation_colors = effect.get("limitation_colors", [])
                target_options = []
                match target:
                    case "center":
                        target_options = ids_from_cards(effect_player.center)
                    case "holomem":
                        holomems = effect_player.get_holomem_on_stage()
                        match limitation:
                            case "color_in":
                                holomems = [holomem for holomem in holomems if any(color in holomem["colors"] for color in limitation_colors)]
                        target_options = ids_from_cards(holomems)
                    case "self":
                        target_options = [effect["source_card_id"]]
                if len(target_options) == 0:
                    pass
                elif len(target_options) == 1:
                    # 1 target, so just do the effect.
                    self.restore_holomem_hp(effect_player, target_options[0], amount, self.continue_resolving_effects)
                    passed_on_continuation = True
                else:
                    # Choose holomem for effect.
                    decision_event = {
                        "event_type": EventType.EventType_Decision_ChooseHolomemForEffect,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "cards_can_choose": target_options,
                        "effect": effect,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": target_options,
                        "cards_can_choose": target_options,
                        "amount_min": 1,
                        "amount_max": 1,
                        "effect_resolution": self.handle_restore_hp_for_holomem,
                        "effect_amount": amount,
                        "continuation": self.continue_resolving_effects,
                    })
            case EffectType.EffectType_RevealTopDeck:
                if len(effect_player.deck) > 0:
                    top_card = effect_player.deck[0]
                    reveal_event = {
                        "event_type": EventType.EventType_RevealCards,
                        "effect_player_id": effect_player_id,
                        "card_ids": [top_card["game_card_id"]],
                        "source": "topdeck"
                    }
                    self.broadcast_event(reveal_event)
            case EffectType.EffectType_RollDie:
                # Put the actual roll in front on the queue, but
                # check afterwards to see if we should add any more effects up front.
                rolldie_internal_effect = deepcopy(effect)
                rolldie_internal_effect["effect_type"] = EffectType.EffectType_RollDie_Internal
                # Remove the and effects because they were already processed.
                rolldie_internal_effect["and"] = []
                self.add_effects_to_front([rolldie_internal_effect])

                # When we roll a die, check if there are any choices to be made like oshi abilities.
                ability_effects = effect_player.get_effects_at_timing("before_die_roll", "", effect["source"])
                if ability_effects:
                    self.add_effects_to_front(ability_effects)
            case EffectType.EffectType_RollDie_ChooseResult:
                choice_info = {
                    "specific_options": ["1", "2", "3", "4", "5", "6"],
                }
                min_choice = 0
                max_choice = 5
                decision_event = {
                    "event_type": EventType.EventType_ForceDieResult,
                    "desired_response": GameAction.EffectResolution_MakeChoice,
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
                    "resolution_func": self.handle_force_die_result,
                    "continuation": self.continue_resolving_effects,
                })
            case EffectType.EffectType_RollDie_Internal:
                die_effects = effect["die_effects"]
                rigged = False
                if effect_player.set_next_die_roll:
                    die_result = effect_player.set_next_die_roll
                    effect_player.set_next_die_roll = 0
                    rigged = True
                else:
                    die_result = self.random_gen.randint(1, 6)
                self.last_die_value = die_result

                die_event = {
                    "event_type": EventType.EventType_RollDie,
                    "effect_player_id": effect_player_id,
                    "die_result": die_result,
                    "rigged": rigged,
                }
                self.broadcast_event(die_event)
                effects_to_resolve = []
                for die_effects_option in die_effects:
                    activate_on_values = die_effects_option["activate_on_values"]
                    if die_result in activate_on_values:
                        effects_to_resolve = die_effects_option["effects"]
                        break
                if effects_to_resolve:
                    # Push these effects onto the front of the effect list.
                    add_ids_to_effects(effects_to_resolve, effect_player_id, effect["source_card_id"])
                    self.add_effects_to_front(effects_to_resolve)

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
                to_limitation_tags = effect.get("to_limitation_tags", [])
                multi_to = effect.get("multi_to", False)

                # Determine options
                from_options = []
                to_options = []

                match from_zone:
                    case "archive":
                        # Get archive cheer cards.
                        relevant_archive_cards = [card for card in effect_player.archive if is_card_cheer(card)]
                        if from_limitation:
                            match from_limitation:
                                case "color_in":
                                    from_options = [card for card in relevant_archive_cards if any(color in card["colors"] for color in from_limitation_colors)]
                                case _:
                                    raise NotImplementedError(f"Unimplemented from limitation: {from_limitation}")
                        else:
                            from_options = relevant_archive_cards
                        from_options = ids_from_cards(from_options)
                    case "cheer_deck":
                        # Cheer deck is from top.
                        if len(effect_player.cheer_deck) > 0:
                            from_options = [effect_player.cheer_deck[0]]
                        from_options = ids_from_cards(from_options)
                    case "downed_holomem":
                        holomem = self.down_holomem_state.holomem_card
                        if from_limitation:
                            match from_limitation:
                                case "color_in":
                                    from_options = [card for card in holomem["attached_cheer"] \
                                        if any(color in card["colors"] for color in from_limitation_colors)]
                                case _:
                                    from_options = holomem["attached_cheer"]
                        from_options = ids_from_cards(from_options)
                    case "holomem":
                        from_options = effect_player.get_cheer_ids_on_holomems()
                    case "opponent_holomem":
                        opponent = self.other_player(effect_player_id)
                        holomem_options = opponent.get_holomem_on_stage()
                        if from_limitation:
                            match from_limitation:
                                case "center":
                                    holomem_options = opponent.center
                                case _:
                                    raise NotImplementedError(f"Unimplemented from limitation: {from_limitation}")
                        for holomem in holomem_options:
                            from_options.extend(holomem["attached_cheer"])
                        from_options = ids_from_cards(from_options)
                    case _:
                        raise NotImplementedError(f"Unimplemented from zone: {from_zone}")

                match to_zone:
                    case "archive":
                        to_options = ["archive"]
                    case "holomem":
                        if to_limitation:
                            match to_limitation:
                                case "attached_owner":
                                    source_card = self.find_card(effect["source_card_id"])
                                    owner_player = self.get_player(source_card["owner_id"])
                                    to_options = owner_player.get_holomems_with_attachment(effect["source_card_id"])
                                case "color_in":
                                    to_options = [card for card in effect_player.get_holomem_on_stage() if any(color in card["colors"] for color in to_limitation_colors)]
                                case "backstage":
                                    to_options = effect_player.backstage
                                case "center":
                                    to_options = effect_player.center
                                case "center_or_collab":
                                    to_options = effect_player.center + effect_player.collab
                                case "tag_in":
                                    to_options = [card for card in effect_player.get_holomem_on_stage() if any(tag in card["tags"] for tag in to_limitation_tags)]
                                case _:
                                    raise NotImplementedError(f"Unimplemented to limitation: {to_limitation}")
                            to_options = ids_from_cards(to_options)
                        else:
                            to_options = ids_from_cards(effect_player.get_holomem_on_stage())
                    case "this_holomem":
                        to_options = [effect["source_card_id"]]
                if str(amount_min) == "all":
                    amount_min = len(from_options)
                if str(amount_max) == "all":
                    amount_max = len(from_options)

                if from_zone == "downed_holomem":
                    # Can't give it to the dead holomem.
                    to_options.remove(self.down_holomem_state.holomem_card["game_card_id"])

                if len(to_options) == 0 or len(from_options) == 0:
                    # No effect.
                    pass
                elif len(to_options) == 1 and len(from_options) == 1 and amount_min == len(from_options) and amount_max == amount_min:
                    # Do it automatically.
                    placements = {}
                    for from_id in from_options:
                        placements[from_id] = to_options[0]
                    # Do both players as the cheer could be opponent targeted.
                    effect_player.move_cheer_between_holomems(placements)
                    opponent = self.other_player(effect_player.player_id)
                    opponent.move_cheer_between_holomems(placements)
                else:
                    if len(from_options) < amount_min:
                        # If there's less cheer than the min, do as many as you can.
                        amount_min = len(from_options)

                    if from_zone == "opponent_holomem":
                        opponent = self.other_player(effect_player_id)
                        cheer_on_each_mem = opponent.get_cheer_on_each_holomem()
                    else:
                        cheer_on_each_mem = effect_player.get_cheer_on_each_holomem()
                    decision_event = {
                        "event_type": EventType.EventType_Decision_SendCheer,
                        "desired_response": GameAction.EffectResolution_MoveCheerBetweenHolomems,
                        "effect_player_id": effect_player_id,
                        "amount_min": amount_min,
                        "amount_max": amount_max,
                        "from_zone": from_zone,
                        "from_limitation": from_limitation,
                        "from_limitation_colors": from_limitation_colors,
                        "to_zone": to_zone,
                        "to_limitation": to_limitation,
                        "to_limitation_colors": to_limitation_colors,
                        "from_options": from_options,
                        "to_options": to_options,
                        "cheer_on_each_mem": cheer_on_each_mem,
                        "multi_to": multi_to,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_MoveCheerBetweenHolomems,
                        "decision_player": effect_player_id,
                        "amount_min": amount_min,
                        "amount_max": amount_max,
                        "available_cheer": from_options,
                        "available_targets": to_options,
                        "multi_to": multi_to,
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
                    max_choice = 1
                    decision_event = {
                        "event_type": EventType.EventType_Choice_SendCollabBack,
                        "desired_response": GameAction.EffectResolution_MakeChoice,
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
            case EffectType.EffectType_SetCenterHP:
                amount = effect["amount"]
                is_opponent = "opponent" in effect and effect["opponent"]
                affected_player = effect_player
                if is_opponent:
                    affected_player = self.other_player(effect_player_id)
                if len(affected_player.center) > 0:
                    affected_player.set_holomem_hp(affected_player.center[0]["game_card_id"], amount)
            case EffectType.EffectType_ShuffleHandToDeck:
                effect_player.shuffle_hand_to_deck()
            case EffectType.EffectType_SpendHolopower:
                amount = effect["amount"]
                effect_player.spend_holopower(amount)
                if "oshi_skill_id" in effect:
                    oshi_skill_event = {
                        "event_type": EventType.EventType_OshiSkillActivation,
                        "oshi_player_id": effect_player.player_id,
                        "skill_id": effect["oshi_skill_id"],
                    }
                    self.broadcast_event(oshi_skill_event)
            case EffectType.EffectType_SwitchCenterWithBack:
                target_player = effect_player
                swap_opponent_cards = "opponent" in effect and effect["opponent"]
                skip_resting = effect.get("skip_resting", False)
                if swap_opponent_cards:
                    target_player = self.other_player(effect_player_id)
                available_backstage_ids = []
                for card in target_player.backstage:
                    if skip_resting and card["resting"]:
                        continue
                    available_backstage_ids.append(card["game_card_id"])
                if len(available_backstage_ids) == 0 or (not swap_opponent_cards and not target_player.can_move_front_stage()):
                    # No effect.
                    pass
                elif len(available_backstage_ids) == 1:
                    # Do it right away.
                    target_player.swap_center_with_back(available_backstage_ids[0])
                else:
                    # Ask for a decision.
                    decision_event = {
                        "event_type": EventType.EventType_Decision_SwapHolomemToCenter,
                        "desired_response": GameAction.EffectResolution_ChooseCardsForEffect,
                        "effect_player_id": effect_player_id,
                        "cards_can_choose": available_backstage_ids,
                        "swap_opponent_cards": swap_opponent_cards,
                    }
                    self.broadcast_event(decision_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_ChooseCardsForEffect,
                        "decision_player": effect_player_id,
                        "all_card_seen": available_backstage_ids,
                        "cards_can_choose": available_backstage_ids,
                        "amount_min": 1,
                        "amount_max": 1,
                        "effect_resolution": self.handle_holomem_swap,
                        "continuation": self.continue_resolving_effects,
                    })
            case _:
                raise NotImplementedError(f"Unimplemented effect type: {effect['effect_type']}")

        return passed_on_continuation

    def add_effects_to_front(self, new_effects):
        self.effect_resolution_state.effects_to_resolve = new_effects + self.effect_resolution_state.effects_to_resolve

    def send_choice_to_player(self, effect_player_id, choice):
        min_choice = 0
        max_choice = len(choice) - 1
        decision_event = {
            "event_type": EventType.EventType_Decision_Choice,
            "desired_response": GameAction.EffectResolution_MakeChoice,
            "effect_player_id": effect_player_id,
            "choice": choice,
            "min_choice": min_choice,
            "max_choice": max_choice,
        }
        self.broadcast_event(decision_event)
        self.set_decision({
            "decision_type": DecisionType.DecisionChoice,
            "decision_player": effect_player_id,
            "choice": choice,
            "min_choice": min_choice,
            "max_choice": max_choice,
            "resolution_func": self.handle_choice_effects,
            "continuation": self.continue_resolving_effects,
        })

    def end_game(self, loser_id, reason_id):
        if not self.is_game_over():
            self.phase = GamePhase.GameOver

            gameover_event = {
                "event_type": EventType.EventType_GameOver,
                "loser_id": loser_id,
                "winner_id": self.other_player(loser_id).player_id,
                "reason_id": reason_id,
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

    def perform_mulligan(self, player: PlayerState, forced):
        if forced:
            revealed_card_ids = ids_from_cards(player.hand)
            mulligan_reveal_event = {
                "event_type": EventType.EventType_MulliganReveal,
                "active_player": player.player_id,
                "revealed_card_ids": revealed_card_ids,
            }
            self.broadcast_event(mulligan_reveal_event)

        # Do the mulligan reshuffle/drawing.
        player.mulligan()

    def process_forced_mulligans(self):
        # If the player has no debut holomems, they must mulligan.
        for player in self.player_states:
            while not player.mulligan_hand_valid:
                # If the player has a debut holomem, they are done.
                if any(card["card_type"] == "holomem_debut" for card in player.hand):
                    player.mulligan_hand_valid = True
                else:
                    self.perform_mulligan(player, forced=True)


    def make_error_event(self, player_id:str, error_id:str, error_message:str):
        return {
            "event_player_id": player_id,
            "event_type": EventType.EventType_GameError,
            "error_id": error_id,
            "error_message": error_message,
        }

    def validate_action_fields(self, action_data:dict, expected_fields:dict):
        for field_name, field_type in expected_fields.items():
            if field_name not in action_data:
                return False
            # If the field type is the list typing.
            if hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                element_type = field_type.__args__[0]
                if not isinstance(action_data[field_name], list) or not all(isinstance(item, element_type) for item in action_data[field_name]):
                    return False
             # Check for dict type with specific key and value types
            elif hasattr(field_type, '__origin__') and field_type.__origin__ == dict:
                key_type, value_type = field_type.__args__
                if not isinstance(action_data[field_name], dict) or not all(isinstance(k, key_type) and isinstance(v, value_type) for k, v in action_data[field_name].items()):
                    logger.info(f"Field {field_name} is not of type {field_type}")
                    return False
        return True

    def handle_game_message(self, player_id:str, action_type:str, action_data: dict):
        logger.info("Processing game message %s from player %s" % (action_type, player_id))
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
            case GameAction.MainStepBatonPass:
                self.handle_main_step_baton_pass(player_id, action_data)
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
            case GameAction.EffectResolution_ChooseCardsForEffect:
                self.handle_effect_resolution_choose_cards_for_effect(player_id, action_data)
            case GameAction.EffectResolution_MakeChoice:
                self.handle_effect_resolution_make_choice(player_id, action_data)
            case GameAction.EffectResolution_OrderCards:
                self.handle_effect_resolution_order_cards(player_id, action_data)
            case GameAction.Resign:
                self.handle_player_resign(player_id)
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
            self.perform_mulligan(player_state, forced=False)
        player_state.mulligan_completed = True
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

        if len(backstage_holomem_card_ids) > MAX_MEMBERS_ON_STAGE - 1:
            self.send_event(self.make_error_event(player_id, "invalid_backstage", "Too many cards for initial placement."))
            return False

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
        player_state.move_card(center_holomem_card_id, "center", no_events=True)
        for card_id in backstage_holomem_card_ids:
            player_state.move_card(card_id, "backstage", no_events=True)

        player_state.initial_placement_completed = True

        # Broadcast the event.
        placement_event = {
            "event_type": EventType.EventType_InitialPlacementPlaced,
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
            if action["action_type"] == GameAction.MainStepPlaceHolomem and action["card_id"] == chosen_card_id:
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
            if action["action_type"] == GameAction.MainStepBloom and action["card_id"] == chosen_card_id and action["target_id"] == target_id:
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
        player.bloom(card_id, target_id, continuation)

    def validate_main_step_collab(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepCollabFields):
            return False

        chosen_card_id = action_data["card_id"]
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == GameAction.MainStepCollab and action["card_id"] == chosen_card_id:
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
        if not isinstance(player_id, str):
            self.send_event(self.make_error_event(player_id, "invalid_player", "Invalid player id."))
            return False

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
            if action["action_type"] == GameAction.MainStepOshiSkill and action["skill_id"] == skill_id:
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

        action_effects = player.get_oshi_action_effects(skill_id)
        add_ids_to_effects(action_effects, player_id, "oshi")
        self.begin_resolving_effects(action_effects, continuation)

    def validate_main_step_play_support(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepPlaySupportFields):
            return False

        player = self.get_player(player_id)
        chosen_card_id = action_data["card_id"]
        action_found = None
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == GameAction.MainStepPlaySupport and action["card_id"] == chosen_card_id:
                action_found = action
                break
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        if "play_requirements" in action_found:
            # All fields in play_requirements must exist in action_data.
            for required_field_name, required_field_info in action_found["play_requirements"].items():
                if required_field_name not in action_data:
                    self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
                    return False

                passed_in_data = action_data[required_field_name]
                if required_field_info["type"] == "list":
                    if not isinstance(passed_in_data, list) or len(passed_in_data) != required_field_info["length"]:
                        self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
                        return False

                    if required_field_info["content_type"] == "cheer_in_play":
                        # Validate that all items in the list are cheer cards on holomems.
                        validated = True
                        for cheer_id in passed_in_data:
                            if not isinstance(cheer_id, str):
                                validated = False
                                break
                            if cheer_id not in player.get_cheer_ids_on_holomems():
                                validated = False
                                break

                        # The list must also be unique.
                        if len(set(passed_in_data)) != len(passed_in_data):
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
        card, _, _ = player.find_card(card_id)

        # Send an event showing the card being played.
        play_event = {
            "event_type": EventType.EventType_PlaySupportCard,
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
            player.archive_attached_cards(cheer_to_archive_from_play)

        # Begin resolving the card effects.
        player.played_support_this_turn = True
        if is_card_limited(card):
            player.used_limited_this_turn = True

        card_effects = card["effects"]
        add_ids_to_effects(card_effects, player.player_id, card_id)
        self.floating_cards.append(card)
        self.begin_resolving_effects(card_effects, continuation, [card])

    def validate_main_step_baton_pass(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepBatonPassFields):
            return False

        card_id = action_data["card_id"]
        cheer_ids = action_data["cheer_ids"]
        # The card must be in the options in the available action.
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == GameAction.MainStepBatonPass and card_id in action["backstage_options"]:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
            return False

        # Validate that there is enough cheer in the cheer ids and the cheer are all on the center.
        player = self.get_player(player_id)
        center_mem = player.center[0]
        baton_cost = center_mem["baton_cost"]
        if len(cheer_ids) < baton_cost:
            self.send_event(self.make_error_event(player_id, "invalid_cheer", "Not enough cheer to pass the baton."))
            return False
        # Validate uniqueness of cheer.
        if len(set(cheer_ids)) != len(cheer_ids):
            self.send_event(self.make_error_event(player_id, "invalid_cheer", "Duplicate cheer to pass."))
            return False
        for cheer_id in cheer_ids:
            if not player.is_cheer_on_holomem(cheer_id, player.center[0]["game_card_id"]):
                self.send_event(self.make_error_event(player_id, "invalid_cheer", "Invalid cheer to pass."))
                return False

        return True

    def handle_main_step_baton_pass(self, player_id:str, action_data:dict):
        if not self.validate_main_step_baton_pass(player_id, action_data):
            return

        player = self.get_player(player_id)
        new_center_id = action_data["card_id"]
        cheer_to_archive_ids = action_data["cheer_ids"]
        player.archive_attached_cards(cheer_to_archive_ids)
        player.swap_center_with_back(new_center_id)
        player.baton_pass_this_turn = True

        continuation = self.clear_decision()
        continuation()

    def validate_main_step_begin_performance(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionMainStep, GameAction.MainStepBeginPerformanceFields):
            return False

        # Ensure this action is in the available actions.
        action_found = False
        for action in self.current_decision["available_actions"]:
            if action["action_type"] == GameAction.MainStepBeginPerformance:
                action_found = True
        if not action_found:
            self.send_event(self.make_error_event(player_id, "invalid_action", "Invalid action."))
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
            if action["action_type"] == GameAction.PerformanceStepUseArt and action["performer_id"] == performer_id and action["art_id"] == art_id:
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

        # If the cheer is already on that holomem, then it is invalid.
        player = self.get_player(player_id)
        for cheer_id, target_id in placements.items():
            if target_id == "archive":
                continue
            if player.is_cheer_on_holomem(cheer_id, target_id):
                self.send_event(self.make_error_event(player_id, "invalid_target", "Cheer already on target."))
                return False

        if "multi_to" not in self.current_decision:
            # There should only be one target.
            if len(set(placements.values())) != 1:
                self.send_event(self.make_error_event(player_id, "invalid_target", "Multiple targets chosen."))
                return False

        return True

    def handle_effect_resolution_move_cheer_between_holomems(self, player_id:str, action_data:dict):
        if not self.validate_move_cheer_between_holomems(player_id, action_data):
            return

        player = self.get_player(player_id)
        placements = action_data["placements"]
        player.move_cheer_between_holomems(placements)
        # Could be opponent, so just try on them too.
        # All cards have unique ids so it should be fine.
        opponent = self.other_player(player_id)
        opponent.move_cheer_between_holomems(placements)

        continuation = self.clear_decision()
        continuation()

    def validate_choose_cards_for_effect(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionEffect_ChooseCardsForEffect, GameAction.EffectResolution_ChooseCardsForEffectFields):
            return False

        chosen_cards = action_data["card_ids"]
        for card_id in chosen_cards:
            if card_id not in self.current_decision["cards_can_choose"]:
                self.send_event(self.make_error_event(player_id, "invalid_card", "Invalid card choice."))
                return False
        # Check the amounts against amount_min/max
        if len(chosen_cards) < self.current_decision["amount_min"] or len(chosen_cards) > self.current_decision["amount_max"]:
            self.send_event(self.make_error_event(player_id, "invalid_amount", "Invalid amount of cards chosen."))
            return False
        # Check for dupes.
        if len(set(chosen_cards)) != len(chosen_cards):
            self.send_event(self.make_error_event(player_id, "invalid_card", "Duplicate cards chosen."))
            return False

        return True

    def handle_effect_resolution_choose_cards_for_effect(self, player_id:str, action_data:dict):
        if not self.validate_choose_cards_for_effect(player_id, action_data):
            return

        decision_info_copy = self.current_decision.copy()
        continuation = self.clear_decision()

        chosen_cards = action_data["card_ids"]
        resolution = decision_info_copy["effect_resolution"]
        resolution(decision_info_copy, player_id, chosen_cards, continuation)

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

        decision_info_copy = self.current_decision.copy()
        continuation = self.clear_decision()
        resolution_func(decision_info_copy, player_id, choice_index, continuation)

    def validate_effect_resolution_order_cards(self, player_id:str, action_data:dict):
        if not self.validate_decision_base(player_id, action_data, DecisionType.DecisionEffect_OrderCards, GameAction.EffectResolution_OrderCardsFields):
            return False

        card_ids = action_data["card_ids"]
        # Ensure length matches the decision cards and they are unique.
        if len(card_ids) != len(self.current_decision["card_ids"]) or len(set(card_ids)) != len(card_ids):
            self.send_event(self.make_error_event(player_id, "invalid_cards", "Invalid cards for ordering."))
            return False

        return True

    def handle_effect_resolution_order_cards(self, player_id:str, action_data:dict):
        if not self.validate_effect_resolution_order_cards(player_id, action_data):
            return

        player = self.get_player(player_id)
        card_ids = action_data["card_ids"]
        to_zone = self.current_decision["to_zone"]
        bottom = self.current_decision["bottom"]

        # The cards are in the order they should be put at that location.
        for card_id in card_ids:
            player.move_card(card_id, to_zone, zone_card_id="", hidden_info=True, add_to_bottom=bottom)

        continuation = self.clear_decision()
        continuation()


    def handle_holomem_swap(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        card_id = card_ids[0]
        owner_id = get_owner_id_from_card_id(card_id)
        owner = self.get_player(owner_id)
        owner.swap_center_with_back(card_id)

        continuation()

    def handle_add_turn_effect_for_holomem(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        effect_player = self.get_player(performing_player_id)
        holomem_target = card_ids[0]
        turn_effect = decision_info_copy["turn_effect"]
        replace_field_in_conditions(turn_effect, "required_id", holomem_target)
        effect_player.add_turn_effect(turn_effect)
        event = {
            "event_type": EventType.EventType_AddTurnEffect,
            "effect_player_id": performing_player_id,
            "turn_effect": turn_effect,
        }
        self.broadcast_event(event)

        continuation()

    def handle_deal_damage_to_holomem(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        effect = decision_info_copy["effect"]
        source_player = self.get_player(performing_player_id)
        source_card = decision_info_copy["source_card"]
        target_player = decision_info_copy["target_player"]
        target_card, _, _ = target_player.find_card(card_ids[0])
        self.deal_damage(source_player, target_player, source_card, target_card, effect["amount"], \
            effect.get("special", False), effect.get("prevent_life_loss", False), [], continuation
        )

    def handle_down_holomem(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        effect = decision_info_copy["effect"]
        source_player = self.get_player(performing_player_id)
        source_card = decision_info_copy["source_card"]
        target_player = decision_info_copy["target_player"]
        target_card, _, _ = target_player.find_card(card_ids[0])
        self.down_holomem(source_player, target_player, source_card, target_card,
            effect.get("prevent_life_loss", False), continuation
        )

    def handle_restore_hp_for_holomem(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        effect_player = self.get_player(performing_player_id)
        holomem_target = card_ids[0]
        hp_to_restore = decision_info_copy["effect_amount"]
        self.restore_holomem_hp(effect_player, holomem_target, hp_to_restore, continuation)

    def handle_run_single_effect(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        effect_player = self.get_player(performing_player_id)
        effect = decision_info_copy["effect_to_run"]
        effect["card_ids"] = card_ids
        # Assumption here is no conditions and no decisions after.
        self.do_effect(effect_player, effect)
        continuation()

    def handle_choose_cards_result(self, decision_info_copy, performing_player_id:str, card_ids:List[str], continuation):
        from_zone = decision_info_copy["from_zone"]
        to_zone = decision_info_copy["to_zone"]
        reveal_chosen = decision_info_copy["reveal_chosen"]
        remaining_cards_action = decision_info_copy["remaining_cards_action"]
        all_card_seen = decision_info_copy["all_card_seen"]
        source_card_id = decision_info_copy["source_card_id"]
        remaining_card_ids = [card_id for card_id in all_card_seen if card_id not in card_ids]

        player = self.get_player(performing_player_id)

        self.last_chosen_cards = card_ids
        if len(card_ids) > 0 and "after_choose_effect" in decision_info_copy and decision_info_copy["after_choose_effect"]:
            # Queue this effect.
            after_effects = [decision_info_copy["after_choose_effect"].copy()]
            add_ids_to_effects(after_effects, performing_player_id, source_card_id)
            self.add_effects_to_front(after_effects)

        # Deal with chosen cards.
        if to_zone == "holomem" and len(card_ids) > 0:
            to_limitation = decision_info_copy.get("to_limitation", "")
            to_limitation_colors = decision_info_copy.get("to_limitation_colors", [])
            # In this case, the user has to pick a target holomem.
            # Assume this is only a single card.
            attach_effect = {
                "effect_type": EffectType.EffectType_AttachCardToHolomem,
                "source_card_id": card_ids[0],
                "to_limitation": to_limitation,
                "to_limitation_colors": to_limitation_colors,
                "continuation": lambda :
                    # Finish the cleanup of the remaining cards.
                    self.choose_cards_cleanup_remaining(performing_player_id, remaining_card_ids, remaining_cards_action, from_zone, from_zone, continuation),
            }
            self.do_effect(player, attach_effect)
        elif to_zone == "stage":
            # Determine possible options (backstage, center, collab) depending on what's open.
            choice = [
            ]
            choice.append({
                "effect_type": EffectType.EffectType_PlaceHolomem,
                "player_id": performing_player_id,
                "source_card_id": "",
                "location": "backstage",
                "card_id": card_ids[0],
            })
            if len(player.center) == 0:
                choice.append({
                    "effect_type": EffectType.EffectType_PlaceHolomem,
                    "player_id": performing_player_id,
                    "source_card_id": "",
                    "location": "center",
                    "card_id": card_ids[0],
                })
            if len(player.collab) == 0:
                choice.append({
                    "effect_type": EffectType.EffectType_PlaceHolomem,
                    "player_id": performing_player_id,
                    "source_card_id": "",
                    "location": "collab",
                    "card_id": card_ids[0],
                })

            if len(choice) == 1:
                # Must be backstage.
                to_zone = "backstage"
                for card_id in card_ids:
                    player.move_card(card_id, to_zone, zone_card_id="", hidden_info=not reveal_chosen)
                self.choose_cards_cleanup_remaining(performing_player_id, remaining_card_ids, remaining_cards_action, from_zone, from_zone, continuation)
            else:
                decision_event = {
                    "event_type": EventType.EventType_Decision_Choice,
                    "desired_response": GameAction.EffectResolution_MakeChoice,
                    "effect_player_id": player.player_id,
                    "choice": choice,
                    "min_choice": 0,
                    "max_choice": len(choice) - 1,
                }
                self.broadcast_event(decision_event)
                self.set_decision({
                    "decision_type": DecisionType.DecisionChoice,
                    "decision_player": player.player_id,
                    "choice": choice,
                    "min_choice": 0,
                    "max_choice": len(choice) - 1,
                    "resolution_func": self.handle_choice_effects,
                    "continuation": lambda :
                        self.choose_cards_cleanup_remaining(performing_player_id, remaining_card_ids, remaining_cards_action, from_zone, from_zone, continuation)
                })
        else:
            for card_id in card_ids:
                player.move_card(card_id, to_zone, zone_card_id="", hidden_info=not reveal_chosen)
            self.choose_cards_cleanup_remaining(performing_player_id, remaining_card_ids, remaining_cards_action, from_zone, from_zone, continuation)

    def choose_cards_cleanup_remaining(self, performing_player_id, remaining_card_ids, remaining_cards_action, from_zone, to_zone, continuation):
        player = self.get_player(performing_player_id)
        # Deal with unchosen cards.
        if remaining_card_ids:
            match remaining_cards_action:
                case "nothing":
                    pass
                case "shuffle":
                    if from_zone == "deck":
                        # The cards weren't moved out, so just shuffle.
                        player.shuffle_deck()
                    elif from_zone == "cheer_deck":
                        player.shuffle_cheer_deck()
                    else:
                        raise NotImplementedError(f"Unimplemented shuffle zone action: {from_zone}")
                case "order_on_bottom":
                    order_cards_event = {
                        "event_type": EventType.EventType_Decision_OrderCards,
                        "desired_response": GameAction.EffectResolution_OrderCards,
                        "effect_player_id": performing_player_id,
                        "card_ids": remaining_card_ids,
                        "from_zone": from_zone,
                        "to_zone": to_zone,
                        "bottom": True,
                        "hidden_info_player": performing_player_id,
                        "hidden_info_fields": ["card_ids"],
                    }
                    self.broadcast_event(order_cards_event)
                    self.set_decision({
                        "decision_type": DecisionType.DecisionEffect_OrderCards,
                        "decision_player": performing_player_id,
                        "card_ids": remaining_card_ids,
                        "from_zone": from_zone,
                        "to_zone": to_zone,
                        "bottom": True,
                        "continuation": continuation,
                    })
                case _:
                    raise NotImplementedError(f"Unimplemented remaining cards action: {remaining_cards_action}")

        if not self.current_decision:
            continuation()

    def handle_choice_return_collab(self, decision_info_copy, player_id, choice_index, continuation):
        # 0 is pass, 1 is okay
        if choice_index == 1:
            player = self.get_player(player_id)
            player.return_collab()

        continuation()

    def handle_force_die_result(self, decision_info_copy, player_id, choice_index, continuation):
        # 0-5 is die result 1-6
        player = self.get_player(player_id)
        player.set_next_die_roll = choice_index + 1
        continuation()

    def handle_choice_effects(self, decision_info_copy, player_id, choice_index, continuation):
        chosen_effect = decision_info_copy["choice"][choice_index]
        self.begin_resolving_effects([chosen_effect], continuation)

    def handle_player_resign(self, player_id):
        self.end_game(player_id, "resign")