from fastapi import WebSocket

class Player:
    def __init__(self, player_id: str, websocket: WebSocket):
        self.player_id = player_id
        self.websocket = websocket
        self.current_game_room = None

class PlayerManager:
    def __init__(self):
        self.active_players = {}

    def add_player(self, player_id: str, websocket: WebSocket):
        self.active_players[player_id] = Player(player_id, websocket)

    def remove_player(self, player_id: str):
        if player_id in self.active_players:
            del self.active_players[player_id]

    def get_player(self, player_id: str) -> Player:
        return self.active_players.get(player_id)
