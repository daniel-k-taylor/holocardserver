import json
from typing import List
from app.playermanager import Player
from app.gameengine import GameEngine, GameAction
from app.card_database import CardDatabase

class GameRoom:
    def __init__(self, room_id : str, players : List[Player], game_type : str):
        self.room_id = room_id
        self.players = players
        self.game_type = game_type
        self.cleanup_room = False
        for player in self.players:
            player.current_game_room = self

    async def start(self, card_db: CardDatabase):
        print("GAME: Starting game!")
        player_info = [player.get_player_game_info() for player in self.players]
        self.engine = GameEngine(
            card_db=card_db,
            player_infos=player_info,
            game_type=self.game_type
        )

        self.engine.begin_game()
        events = self.engine.grab_events()
        await self.send_events(events)

    async def send_events(self, events):
        for event in events:
            for player in self.players:
                if player.connected and player.player_id == event["event_player_id"]:
                    await player.websocket.send_json({
                        "message_type": "game_event",
                        "event_data": event
                    })

    async def handle_game_message(self, player_id: str, action_type:str, action_data: dict):
        self.engine.handle_game_message(player_id, action_type, action_data)
        events = self.engine.grab_events()
        await self.send_events(events)
        if self.engine.is_game_over():
            self.cleanup_room = True

    def is_ready_for_cleanup(self):
        return self.cleanup_room

    async def handle_player_quit(self, player: Player):
        await self.handle_game_message(player.player_id, GameAction.Resign, {})

    async def handle_player_disconnect(self, player : Player):
        await self.handle_game_message(player.player_id, GameAction.Resign, {})

        # TODO: Reconnect logic.
        # all_players_disconnected = all([not player.connected for player in self.players])
        # if all_players_disconnected:
        #     self.cleanup_room = True