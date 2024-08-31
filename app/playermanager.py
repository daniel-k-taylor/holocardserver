from fastapi import WebSocket
from typing import Dict

class Player:
    def __init__(self, player_id: str, websocket: WebSocket):
        self.player_id = player_id
        self.websocket = websocket
        self.connected = True
        self.current_game_room = None

        self.oshi_id = None
        self.deck = []
        self.cheer_deck = []

    def save_deck_info(self, oshi_id: str, deck: Dict[str, int], cheer_deck: Dict[str, int]):
        self.oshi_id = oshi_id
        self.deck = deck
        self.cheer_deck = cheer_deck

    def get_player_game_info(self):
        return {
            "player_id": self.player_id,
            "oshi_id": self.oshi_id,
            "deck": self.deck,
            "cheer_deck": self.cheer_deck
        }

class PlayerManager:
    def __init__(self):
        self.active_players = {}

    def add_player(self, player_id: str, websocket: WebSocket):
        self.active_players[player_id] = Player(player_id, websocket)
        return self.active_players[player_id]

    def remove_player(self, player_id: str):
        if player_id in self.active_players:
            del self.active_players[player_id]

    def get_player(self, player_id: str) -> Player:
        return self.active_players.get(player_id)
