import uuid
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.matchmaking import Matchmaking
import app.message_types as message_types
from app.playermanager import PlayerManager
from app.gameroom import GameRoom

app = FastAPI()

# Store connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message : message_types.Message):
        dict_message = message.as_dict()
        print("Broadcasting message:", dict_message)
        for connection in self.active_connections:
            print("Broadcast...")
            await connection.send_json(dict_message)

manager = ConnectionManager()

player_manager : PlayerManager = PlayerManager()
game_rooms : List[GameRoom] = []
matchmaking : Matchmaking = Matchmaking()

async def broadcast_server_info():
    message = message_types.ServerInfoMessage(
        message_type="server_info",
        queue_info=matchmaking.get_queue_info()
    )
    await manager.broadcast(message)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    player_id = uuid.uuid4()
    player = player_manager.get_player(player_id)
    if player:
        player.websocket = websocket
    else:
        player = player_manager.add_player(player_id, websocket)

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = message_types.parse_message(data)
            except Exception as e:
                print("Error in message parsing:", e, "\nMessage:", data)
                await websocket.send_text(f"ERROR: Invalid JSON: {data}")
                continue

            print(f"MESSAGE:", message.message_type)
            if isinstance(message, message_types.JoinServerMessage):
                await broadcast_server_info()

            elif isinstance(message, message_types.JoinMatchmakingQueueMessage):
                match = matchmaking.add_player_to_queue(
                    player=player,
                    queue_name=message.queue_name,
                    custom_game=message.custom_game,
                    game_type=message.game_type,
                )
                if match:
                    game_rooms.append(match)

                await broadcast_server_info()

            elif isinstance(message, message_types.GameActionMessage):
                if player.current_game_room and not player.current_game_room.is_game_over():
                    player.current_game_room.handle_game_action(player.player_id, message.action_type, message.action_data)
                else:
                    await websocket.send_text("ERROR: You are not in a game room.")
            else:
                await websocket.send_text(f"ERROR: Invalid message: {data}")

    except WebSocketDisconnect:
        print("Client disconnected.")
        matchmaking.remove_player_from_queue(player)
        for room in game_rooms:
            if player in room.players:
                room.handle_player_disconnect(player)
                if room.is_game_over():
                    game_rooms.remove(room)
                    break

        player_manager.remove_player(player_id)
        manager.disconnect(websocket)
        await broadcast_server_info()

