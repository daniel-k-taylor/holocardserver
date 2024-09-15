from typing import Dict
from app.gameengine import EventType, GameAction
import random
import logging

logger = logging.getLogger(__name__)

DefaultAIDeck = {
    "deck_id": "starter_azki",
    "oshi_id": "hSD01-002",
    "deck": {
        "hSD01-003": 4,
        "hSD01-004": 3,
        "hSD01-005": 3,
        "hSD01-006": 2,
        "hSD01-007": 2,
        "hSD01-008": 4,
        "hSD01-009": 3,
        "hSD01-010": 3,
        "hSD01-011": 2,
        "hSD01-012": 2,
        "hSD01-013": 2,
        "hSD01-014": 2,
        "hSD01-015": 2,
        "hSD01-016": 3,
        "hSD01-017": 3,
        "hSD01-018": 3,
        "hSD01-019": 3,
        "hSD01-020": 2,
        "hSD01-021": 2
    },
    "cheer_deck": {
        "hY01-001": 10,
        "hY02-001": 10
    }
}


class AIPlayer:

    def __init__(self, player_id: str):
        self.player_id = player_id
        self.connected = True

        self.oshi_id = None
        self.deck = []
        self.cheer_deck = []

        self.event_handlers = {
            EventType.EventType_AddTurnEffect: self._handle_event_ignore,
            EventType.EventType_Bloom: self._handle_event_ignore,
            EventType.EventType_BoostStat: self._handle_event_ignore,
            EventType.EventType_CheerStep: self._handle_cheer_step,
            EventType.EventType_Choice_SendCollabBack: self._handle_choice,
            EventType.EventType_Collab: self._handle_event_ignore,
            EventType.EventType_DamageDealt: self._handle_event_ignore,
            EventType.EventType_Decision_Choice: self._handle_choice,
            EventType.EventType_Decision_ChooseCards: self._handle_choose_cards,
            EventType.EventType_Decision_MainStep: self._handle_main_step,
            EventType.EventType_Decision_OrderCards: self._handle_order_cards,
            EventType.EventType_Decision_PerformanceStep: self._handle_performance_step,
            EventType.EventType_Decision_SendCheer: self._handle_send_cheer,
            EventType.EventType_Decision_SwapHolomemToCenter: self._handle_swap_holomem_to_center,
            EventType.EventType_Draw: self._handle_event_ignore,
            EventType.EventType_EndTurn: self._handle_event_ignore,
            EventType.EventType_ForceDieResult: self._handle_choice,
            EventType.EventType_GameError: self._handle_event_ignore,
            EventType.EventType_GameOver: self._handle_event_ignore,
            EventType.EventType_GameStartInfo: self._handle_event_ignore,
            EventType.EventType_InitialPlacementBegin: self._handle_initial_placement_begin,
            EventType.EventType_InitialPlacementPlaced: self._handle_event_ignore,
            EventType.EventType_InitialPlacementReveal: self._handle_event_ignore,
            EventType.EventType_MainStepStart: self._handle_event_ignore,
            EventType.EventType_MoveCard: self._handle_event_ignore,
            EventType.EventType_MoveAttachedCard: self._handle_event_ignore,
            EventType.EventType_MulliganDecision: self._handle_mulligan_decision,
            EventType.EventType_MulliganReveal: self._handle_event_ignore,
            EventType.EventType_OshiSkillActivation: self._handle_event_ignore,
            EventType.EventType_PerformanceStepStart: self._handle_event_ignore,
            EventType.EventType_PerformArt: self._handle_event_ignore,
            EventType.EventType_PlaySupportCard: self._handle_event_ignore,
            EventType.EventType_ResetStepActivate: self._handle_event_ignore,
            EventType.EventType_ResetStepChooseNewCenter: self._handle_choose_new_center,
            EventType.EventType_ResetStepCollab: self._handle_event_ignore,
            EventType.EventType_RollDie: self._handle_event_ignore,
            EventType.EventType_ShuffleDeck: self._handle_event_ignore,
            EventType.EventType_TurnStart: self._handle_event_ignore,
        }

    def set_deck(self, deck_info : dict):
        self.oshi_id = deck_info["oshi_id"]
        self.deck = deck_info["deck"]
        self.cheer_deck = deck_info["cheer_deck"]

    def get_player_game_info(self):
        return {
            "player_id": self.player_id,
            "oshi_id": self.oshi_id,
            "deck": self.deck,
            "cheer_deck": self.cheer_deck
        }

    def ai_process_events(self, events):
        # Process game events and issue actions.
        ai_performing_action = False
        ai_action_type = None
        ai_action_data = None

        for event in events:
            # Only look at events meant for me.
            if self.player_id == event["event_player_id"]:
                event_type = event["event_type"]
                if event_type in self.event_handlers:
                    ai_performing_action, ai_action_type, ai_action_data = self.event_handlers[event_type](event)
                else:
                    logger.error(f"AI: Unhandled event type: {event_type}")

        return ai_performing_action, {
            "action_type": ai_action_type,
            "action_data": ai_action_data
        }

    def _handle_event_ignore(self, _event):
        return False, None, None

    def _handle_cheer_step(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        cheer_to_place = event["cheer_to_place"]
        target_options = event["options"]
        placements = {}
        for cheer_id in cheer_to_place:
            placements[cheer_id] = target_options[0]

        return True, event["desired_response"], {
            "placements": placements
        }

    def _handle_choice(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        min_choice = event["min_choice"]
        max_choice = event["max_choice"]

        return True, event["desired_response"], {
            "choice_index": min_choice
        }

    def _handle_choose_cards(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        all_card_seen = event["all_card_seen"]
        cards_can_choose = event["cards_can_choose"]
        amount_min = event["amount_min"]
        amount_max = event["amount_max"]
        desired_card_count = min(amount_max, len(cards_can_choose))

        card_ids = []
        for i in range(desired_card_count):
            card_ids.append(cards_can_choose[i])

        return True, event["desired_response"], {
            "card_ids": card_ids
        }

    def _handle_main_step(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        available_actions = event["available_actions"]

        # Split available actions by action type.
        all_actions = {}
        all_actions[GameAction.MainStepPlaceHolomem] = [action for action in available_actions if action["action_type"] == GameAction.MainStepPlaceHolomem]
        all_actions[GameAction.MainStepBloom] = [action for action in available_actions if action["action_type"] == GameAction.MainStepBloom]
        all_actions[GameAction.MainStepCollab] = [action for action in available_actions if action["action_type"] == GameAction.MainStepCollab]
        all_actions[GameAction.MainStepOshiSkill] = [action for action in available_actions if action["action_type"] == GameAction.MainStepOshiSkill]
        all_actions[GameAction.MainStepPlaySupport] = [action for action in available_actions if action["action_type"] == GameAction.MainStepPlaySupport]
        all_actions[GameAction.MainStepBatonPass] = [action for action in available_actions if action["action_type"] == GameAction.MainStepBatonPass]
        all_actions[GameAction.MainStepBeginPerformance] = [action for action in available_actions if action["action_type"] == GameAction.MainStepBeginPerformance]

        chosen_action = GameAction.MainStepEndTurn
        card_id = None
        target_id = None
        skill_id = None
        play_requirements = None
        if all_actions[GameAction.MainStepPlaceHolomem]:
            # Just try to place all mems
            chosen_action = GameAction.MainStepPlaceHolomem
            card_id = all_actions[GameAction.MainStepPlaceHolomem][0]["card_id"]
        elif all_actions[GameAction.MainStepBloom]:
            # Always bloom if we can.
            chosen_action = GameAction.MainStepBloom
            card_id = all_actions[GameAction.MainStepBloom][0]["card_id"]
            target_id = all_actions[GameAction.MainStepBloom][0]["target_id"]
        elif all_actions[GameAction.MainStepCollab]:
            # Always collab if we can.
            chosen_action = GameAction.MainStepCollab
            # Pick a random one though.
            collab_index = random.randint(0, len(all_actions[GameAction.MainStepCollab]) - 1)
            card_id = all_actions[GameAction.MainStepCollab][collab_index]["card_id"]
        elif all_actions[GameAction.MainStepOshiSkill]:
            # Always oshi skill if we can.
            chosen_action = GameAction.MainStepOshiSkill
            # Start with the 2nd skill since it's the once per game.
            skill_id = all_actions[GameAction.MainStepOshiSkill][-1]["skill_id"]
        elif all_actions[GameAction.MainStepPlaySupport]:
            # Always play all support cards.
            chosen_action = GameAction.MainStepPlaySupport
            play_support_action = all_actions[GameAction.MainStepPlaySupport][0]
            card_id = play_support_action["card_id"]
            if "play_requirements" in play_support_action and play_support_action["play_requirements"]:
                cheer_on_each_mem = play_support_action["cheer_on_each_mem"]
                all_cheer = []
                for holomem in cheer_on_each_mem:
                    all_cheer.extend(cheer_on_each_mem[holomem])
                for requirement_name in play_support_action["play_requirements"]:
                    requirement_detail = play_support_action["play_requirements"][requirement_name]
                    length = requirement_detail["length"]
                    content_type = requirement_detail["content_type"]
                    match requirement_name:
                        case "cheer_to_archive_from_play":
                            spent_cheer = []
                            for i in range(length):
                                spent_cheer.append(all_cheer[i])
                            play_requirements = {
                                requirement_name: spent_cheer
                            }
                        case _:
                            raise NotImplementedError("Unimplemented play requirement")

        # Skip baton pass for now.
        #elif all_actions[GameAction.MainStepBatonPass]:
        elif all_actions[GameAction.MainStepBeginPerformance]:
            # Always perform.
            chosen_action = GameAction.MainStepBeginPerformance
        else:
            # Just end turn.
            chosen_action = GameAction.MainStepEndTurn


        match chosen_action:
            case GameAction.MainStepPlaceHolomem:
                return True, GameAction.MainStepPlaceHolomem, {
                    "card_id": card_id,
                }
            case GameAction.MainStepBloom:
                return True, GameAction.MainStepBloom, {
                    "card_id": card_id,
                    "target_id": target_id,
                }
            case GameAction.MainStepCollab:
                return True, GameAction.MainStepCollab, {
                    "card_id": card_id,
                }
            case GameAction.MainStepOshiSkill:
                return True, GameAction.MainStepOshiSkill, {
                    "skill_id": skill_id,
                }
            case GameAction.MainStepPlaySupport:
                action_response = {
                    "card_id": card_id,
                }
                if play_requirements:
                    for req in play_requirements:
                        action_response[req] = play_requirements[req]
                return True, GameAction.MainStepPlaySupport, action_response
            case GameAction.MainStepBatonPass:
                return True, GameAction.MainStepBatonPass, {
                    "card_id": card_id,
                }
            case GameAction.MainStepBeginPerformance:
                return True, GameAction.MainStepBeginPerformance, {
                }
            case GameAction.MainStepEndTurn:
                return True, GameAction.MainStepEndTurn, {
                }
            case _:
                raise NotImplementedError("Unimplemented action")

    def _handle_move_cheer_between_holomems(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        amount_min = event["amount_min"]
        amount_max = event["amount_max"]
        available_cheer = event["available_cheer"]
        available_targets = event["available_targets"]
        cheer_on_each_mem = event["cheer_on_each_mem"]

        placements = {}
        for i in range(amount_min):
            cheer_to_send = available_cheer[i]
            for i in range(len(available_targets)):
                target = available_targets[i]
                if cheer_to_send not in cheer_on_each_mem[target]:
                    placements[cheer_to_send] = target
                    break

        return True, event["desired_response"], {
            "placements": placements
        }

    def _handle_order_cards(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        remaining_card_ids = event["card_ids"]

        return True, event["desired_response"], {
            "card_ids": remaining_card_ids
        }

    def _handle_performance_step(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        available_actions = event["available_actions"]

        # Split available actions by action type.
        all_actions = {}
        all_actions[GameAction.PerformanceStepUseArt] = [action for action in available_actions if action["action_type"] == GameAction.PerformanceStepUseArt]

        chosen_action = GameAction.PerformanceStepEndTurn
        performer_id = None
        art_id = None
        target_id = None
        if all_actions[GameAction.PerformanceStepUseArt]:
            # Do the last one, so we use the most powerful moves.
            chosen_action = GameAction.PerformanceStepUseArt
            performer_id = all_actions[GameAction.PerformanceStepUseArt][-1]["performer_id"]
            art_id = all_actions[GameAction.PerformanceStepUseArt][-1]["art_id"]
            target_id = all_actions[GameAction.PerformanceStepUseArt][-1]["valid_targets"][0]
        else:
            # Just end turn.
            chosen_action = GameAction.PerformanceStepEndTurn

        match chosen_action:
            case GameAction.PerformanceStepUseArt:
                return True, GameAction.PerformanceStepUseArt, {
                    "performer_id": performer_id,
                    "art_id": art_id,
                    "target_id": target_id,
                }
            case GameAction.PerformanceStepEndTurn:
                return True, GameAction.PerformanceStepEndTurn, {
                }
            case _:
                raise NotImplementedError("Unimplemented performance action")

    def _handle_send_cheer(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        amount_min = event["amount_min"]
        amount_max = event["amount_max"]
        from_options = event["from_options"]
        to_options = event["to_options"]
        cheer_on_each_mem = event["cheer_on_each_mem"]

        placements = {}
        for i in range(amount_min):
            cheer_to_send = from_options[i]
            for i in range(len(to_options)):
                target = to_options[i]
                if target not in cheer_on_each_mem or \
                cheer_to_send not in cheer_on_each_mem[target]:
                    placements[cheer_to_send] = target
                    break

        return True, event["desired_response"], {
            "placements": placements
        }

    def _handle_swap_holomem_to_center(self, event):
        if self.player_id != event["effect_player_id"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        cards_can_choose = event["cards_can_choose"]
        chosen = [cards_can_choose[0]]

        return True, event["desired_response"], {
            "card_ids": chosen
        }

    def _handle_initial_placement_begin(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        debut_options = event["debut_options"]
        spot_options = event["spot_options"]

        center = debut_options[0]
        backstage = []
        if len(debut_options) > 1:
            backstage = debut_options[1:] + spot_options
        # backstage has a max of 5, so only take 5
        backstage = backstage[:5]

        return True, event["desired_response"], {
            "center_holomem_card_id": center,
            "backstage_holomem_card_ids": backstage,
        }

    def _handle_mulligan_decision(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        return True, event["desired_response"], {
            "do_mulligan": False,
        }

    def _handle_choose_new_center(self, event):
        if self.player_id != event["active_player"]:
            # Skip events that aren't meant for me to act.
            return False, None, None

        center_options = event["center_options"]
        chosen_center = center_options[0]

        return True, event["desired_response"], {
            "new_center_card_id": chosen_center,
        }