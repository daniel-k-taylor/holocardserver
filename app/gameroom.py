import json
from typing import List
from app.playermanager import Player
from app.gameengine import GameEngine
from app.card_database import CardDatabase

class GameRoom:
    def __init__(self, room_id : str, players : List[Player], game_type : str):
        self.room_id = room_id
        self.players = players
        self.game_type = game_type
        self.cleanup_room = False
        for player in self.players:
            player.current_game_room = self

    def start(self, card_db: CardDatabase):
        player_ids = [player.player_id for player in self.players]
        self.engine = GameEngine(
            card_db=card_db,
            previous_state=None,
            player_ids=player_ids,
            game_type=self.game_type
        )

        events = self.engine.begin_game()
        self.send_events(events)

    def send_events(self, events):
        for event in events:
            for player in self.players:
                if player.connected and player.player_id == event["event_player_id"]:
                    player.websocket.send_json({
                        "message_type": "game_event",
                        "event_data": event
                    })

    def handle_game_message(self, player: Player, action_type:str, action_data: dict):
        # Pass the message to the game engine.
        events = self.engine.handle_game_message(player.player_id, action_type, action_data)

        # Send events to players.
        self.send_events(events)

    def is_game_over(self):
        return self.cleanup_room

    def handle_player_disconnect(self, player : Player):
        player.connected = False
        all_players_disconnected = all([not player.connected for player in self.players])
        if all_players_disconnected:
            self.cleanup_room = True