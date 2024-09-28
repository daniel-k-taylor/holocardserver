import json
import os
from typing import List
from app.playermanager import Player
from app.gameengine import GameEngine, GameAction, EventType
from app.card_database import CardDatabase
from app.aiplayer import AIPlayer, DefaultAIDeck
from app.dbaccess import upload_match_to_blob_storage
import logging
logger = logging.getLogger(__name__)

class GameRoom:
    def __init__(self, room_id : str, room_name : str, players : List[Player], game_type : str, queue_name : str):
        self.room_id = room_id
        self.room_name = room_name
        self.players = players
        self.observers : List[Player] = []
        self.ai_player = None
        self.game_type = game_type
        self.queue_name = queue_name
        self.cleanup_room = False
        for player in self.players:
            player.current_game_room = self

    def is_ai_game(self):
        return self.game_type == "ai"

    def get_room_name(self):
        return self.room_name

    def get_room_info(self):
        return {
            "room_id": self.room_id,
            "room_name": self.room_name,
            "queue_name": self.queue_name,
            "game_type": self.game_type,
            "players": [player.get_public_player_info() for player in self.players],
        }

    async def start(self, card_db: CardDatabase):
        logger.info("GAME: Starting game!")
        player_info = [player.get_player_game_info() for player in self.players]
        if self.is_ai_game():
            self.ai_player = AIPlayer(player_id="aiplayer" + self.players[0].player_id)
            self.ai_player.set_deck(DefaultAIDeck)
            player_info.append(self.ai_player.get_player_game_info())

        self.engine = GameEngine(
            card_db=card_db,
            player_infos=player_info,
            game_type=self.game_type
        )

        self.engine.begin_game()
        events = self.engine.grab_events()
        await self.send_events(events)
        observer_events = self.engine.grab_observer_events()
        await self.send_observer_events(observer_events)

        if self.is_ai_game():
            # In case the AI has to mulligan first!
            ai_performing_action, ai_action = self.ai_player.ai_process_events(events)
            #logger.info("AI Action: %s %s" % (ai_performing_action, ai_action))
            if ai_performing_action:
                player_id = self.ai_player.player_id
                action_type = ai_action["action_type"]
                action_data = ai_action["action_data"]

                await self.handle_game_message(player_id, action_type, action_data)

    async def send_events(self, events):
        for event in events:
            for player in self.players:
                if player.connected and player.player_id == event["event_player_id"]:
                    await player.send_game_event(event)

    async def send_observer_events(self, events):
        for event in events:
            for player in self.observers:
                if player.connected:
                    await player.send_game_event(event)

    async def handle_game_message(self, player_id: str, action_type:str, action_data: dict):
        for observer in self.observers:
            if player_id == observer.player_id:
                # Assume any message from an observer is them leaving.
                observer.current_game_room = None
                self.observers.remove(observer)
                return

        done_processing = False
        while not done_processing:
            self.engine.handle_game_message(player_id, action_type, action_data)
            events = self.engine.grab_events()
            await self.send_events(events)
            observer_events = self.engine.grab_observer_events()
            await self.send_observer_events(observer_events)
            if self.is_ai_game():
                ai_performing_action, ai_action = self.ai_player.ai_process_events(events)
                #logger.info("AI Action: %s %s" % (ai_performing_action, ai_action))
                if ai_performing_action:
                    player_id = self.ai_player.player_id
                    action_type = ai_action["action_type"]
                    action_data = ai_action["action_data"]
                else:
                    done_processing = True
            else:
                done_processing = True

        if self.engine.is_game_over():
            logger.info("ROOM: %s Game over!" % self.room_id)
            if not self.is_ai_game() and not os.getenv("DONT_UPLOAD_MATCHES"):
                match_data = self.engine.get_match_log()
                if match_data["turn_number"] >= 0:
                    match_data["queue_name"] = self.queue_name
                    upload_match_to_blob_storage(match_data)
            self.cleanup_room = True

    def is_ready_for_cleanup(self):
        return self.cleanup_room

    async def join_as_observer(self, player: Player):
        self.observers.append(player)
        player.current_game_room = self

        await self.observer_request_next_events(player, 0)

    async def observer_request_next_events(self, player: Player, starting_event_index):
        events = self.engine.get_observer_catchup_events()

        # Only send the next 50 events.
        ending_event_index = starting_event_index + 50
        for event in events[starting_event_index:ending_event_index]:
            await player.send_game_event(event)

        # If this is the end, send the catch up event.
        if ending_event_index >= len(events):
            await player.send_game_event({"event_type": EventType.EventType_ObserverCaughtUp})


    async def handle_player_quit(self, player: Player):
        await self.handle_game_message(player.player_id, GameAction.Resign, {})

    async def handle_player_disconnect(self, player : Player):
        await self.handle_game_message(player.player_id, GameAction.Resign, {})

        # TODO: Reconnect logic.
        # all_players_disconnected = all([not player.connected for player in self.players])
        # if all_players_disconnected:
        #     self.cleanup_room = True