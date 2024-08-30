from dataclasses import dataclass
from typing import Any, Dict
import json

@dataclass
class Message:
    message_type: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

# Server Outbound Messages
@dataclass
class ServerInfoMessage(Message):
    queue_info: Dict[str, Any]


# Server Inbound Messages
@dataclass
class JoinServerMessage(Message):
    pass

@dataclass
class JoinMatchmakingQueueMessage(Message):
    custom_game: bool
    queue_name: str
    game_type: str

@dataclass
class GameActionMessage(Message):
    action_type: str

def parse_message(json_data: str) -> Message:
    data = json.loads(json_data)
    message_type = data.get("message_type")

    match message_type:
        case "join_server":
            return JoinServerMessage(**data)
        case "join_matchmaking_queue":
            return JoinMatchmakingQueueMessage(**data)
        case "game_action":
            return GameActionMessage(**data)
        case _:
            raise ValueError(f"Unknown message type: {json_data}")
