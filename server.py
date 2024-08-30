from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from matchmaking import Matchmaking
import json
import message_types
from playermanager import PlayerManager
import uuid

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

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

player_manager = PlayerManager()
matchmaking = Matchmaking()

def get_server_info_message() -> message_types.ServerInfoMessage:
    return message_types.ServerInfoMessage(
        message_type="server_info",
        queue_info=matchmaking.get_queue_info()
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    player_id = uuid.uuid4()
    player = player_manager.get_player(player_id)
    if player is None:
        player_manager.add_player(player_id, websocket)
    else:
        player.websocket = websocket

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = message_types.parse_message(data)
                if isinstance(message, message_types.JoinServerMessage):
                    await manager.send_message(get_server_info_message().to_json())

                elif isinstance(message, message_types.JoinMatchmakingQueueMessage):
                    match = matchmaking.add_player_to_queue(
                        player=player,
                        queue_name=message.queue_name,
                        custom_game=message.custom_game,
                        game_type=message.game_type,
                    )

                    if match:
                        await manager.send_message("Match found!")

                    await manager.send_message(get_server_info_message().to_json())

                elif isinstance(message, message_types.GameActionMessage):
                    await manager.send_message("Unimplemented")

                else:
                    await manager.send_message(f"ERROR: Invalid message: {data}")
            except Exception as e:
                print("Error in message handling:", e)
                await manager.send_message(f"ERROR: Invalid JSON: {data}")
                continue
    except WebSocketDisconnect:
        matchmaking.remove_player_from_queue(player)
        manager.disconnect(websocket)
