from app.gameroom import GameRoom
from app.playermanager import Player
import uuid
import logging
logger = logging.getLogger(__name__)

GameTypeInfo = {
    "ai": {
        "required_players": 1,
    },
    "versus": {
        "required_players": 2,
    },
}

REQUIRED_PLAYERS = 2

def get_queue_friendly_name(queue_name):
    match queue_name:
        case "main_matchmaking_normal":
            return "In Queue"
        case "main_matchmaking_ai":
            return "AI"
        case _:
            return queue_name

class MatchQueue:
    def __init__(self, queue_name : str, game_type: str, permanent_queue : bool):
        self.players = []
        self.queue_name = queue_name
        self.game_type = game_type
        self.permanent_queue = permanent_queue

    def add_player(self, player: Player):
        self.players.append(player)
        player.set_queue(get_queue_friendly_name(self.queue_name))

        # If there are enough players, start a match
        if len(self.players) >= GameTypeInfo[self.game_type]["required_players"]:
            for p in self.players:
                p.set_queue("")
            room = self.create_match()
            self.players = []
            return room
        return None

    def remove_player(self, player: str):
        player.set_queue("")
        self.players.remove(player)

    def create_match(self):
        room_id = str(uuid.uuid4())
        match self.queue_name:
            case "main_matchmaking_normal":
                room_name = "Match_%s" % room_id
            case "main_matchmaking_ai":
                room_name = "AI"
            case _:
                room_name = "Custom_" + self.queue_name
        logger.info("Creating match with ID: %s" % room_id)
        return GameRoom(
            room_id=room_id,
            room_name=room_name,
            players=self.players,
            game_type=self.game_type
        )

class Matchmaking:
    def __init__(self):
        main_queue = MatchQueue("main_matchmaking_normal", permanent_queue=True, game_type="versus")
        ai_queue = MatchQueue("main_matchmaking_ai", permanent_queue=True, game_type="ai")
        self.all_queues = [main_queue, ai_queue]

    def is_game_type_valid(self, game_type: str):
        return game_type in GameTypeInfo

    def get_player_queue(self, player: Player):
        for queue in self.all_queues:
            if player in queue.players:
                return queue.queue_name
        return None

    def add_player_to_queue(self, player: Player, queue_name: str, custom_game: bool, game_type: str):
        for queue in self.all_queues:
            if queue.queue_name == queue_name:
                room = queue.add_player(player)
                if room:
                    if not queue.permanent_queue:
                        self.all_queues.remove(queue)
                    return room
                return None

        if custom_game:
            # The user is creating a new custom game.
            new_queue = MatchQueue(queue_name, game_type=game_type, permanent_queue=False)
            room = new_queue.add_player(player)
            if room:
                return room
            else:
                self.all_queues.append(new_queue)
        return None

    def remove_player_from_queue(self, player: Player):
        for queue in self.all_queues:
            if player in queue.players:
                queue.remove_player(player)
                if not queue.permanent_queue and len(queue.players) == 0:
                    self.all_queues.remove(queue)

    def get_queue_info(self):
        queue_info = []
        for queue in self.all_queues:
            queue_info.append({
                "queue_name": queue.queue_name,
                "permanent_queue": queue.permanent_queue,
                "game_type": queue.game_type,
                "players_count": len(queue.players),
            })
        return queue_info