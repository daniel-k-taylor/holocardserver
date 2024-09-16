import os
from fastapi import WebSocket
from typing import Dict
from app.message_types import ServerInfoMessage
import random

def generate_username(num_results=1):
    directory_path = os.path.dirname(__file__)
    adjectives, nouns = [], []
    with open(os.path.join(directory_path, 'data', 'adjectives.txt'), 'r') as file_adjective:
        with open(os.path.join(directory_path, 'data', 'nouns.txt'), 'r') as file_noun:
            for line in file_adjective:
                adjectives.append(line.strip())
            for line in file_noun:
                nouns.append(line.strip())

    usernames = []
    for _ in range(num_results):
        adjective = random.choice(adjectives).capitalize()
        noun = random.choice(nouns).capitalize()
        num = str(random.randrange(10))
        usernames.append(adjective + noun + num)

    return usernames

class Player:
    def __init__(self, player_id: str, websocket: WebSocket):
        self.player_id = player_id
        self.websocket = websocket
        self.connected = True
        self.current_game_room = None
        self.username = generate_username(1)[0]
        self.queue_name = ""

        self.oshi_id = None
        self.deck = []
        self.cheer_deck = []

    def save_deck_info(self, oshi_id: str, deck: Dict[str, int], cheer_deck: Dict[str, int]):
        self.oshi_id = oshi_id
        self.deck = deck
        self.cheer_deck = cheer_deck

    def get_username(self):
        return self.username

    def set_queue(self, queue_name: str):
        self.queue_name = queue_name

    def get_player_game_info(self):
        return {
            "player_id": self.player_id,
            "username": self.username,
            "oshi_id": self.oshi_id,
            "deck": self.deck,
            "cheer_deck": self.cheer_deck
        }

    def get_public_player_info(self):
        return {
            "player_id": self.player_id,
            "username": self.username,
            "game_room": self.current_game_room.get_room_name() if self.current_game_room else "Lobby",
            "queue": self.queue_name,
        }

    async def send_game_event(self, event):
        await self.websocket.send_json({
            "message_type": "game_event",
            "event_data": event
        })

class PlayerManager:
    def __init__(self):
        self.active_players : Dict[str, Player] = {}

    def add_player(self, player_id: str, websocket: WebSocket):
        self.active_players[player_id] = Player(player_id, websocket)
        return self.active_players[player_id]

    def remove_player(self, player_id: str):
        if player_id in self.active_players:
            del self.active_players[player_id]

    def get_player(self, player_id: str) -> Player:
        return self.active_players.get(player_id)

    def get_players_info(self):
        return [player.get_public_player_info() for player in self.active_players.values()]

    async def broadcast_server_info(self, queue_info):
        players_info = self.get_players_info()
        failed_players = []
        for player in self.active_players.values():
            message = ServerInfoMessage(
                message_type="server_info",
                queue_info=queue_info,
                players_info=players_info,
                your_id=player.player_id,
                your_username=player.get_username()
            )

            try:
                await player.websocket.send_json(message.as_dict())
            except:
                failed_players.append(player.player_id)

        # Remove any players we can't contact anymore.
        for player_id in failed_players:
            self.remove_player(player_id)