import asyncio
import websockets
import json

azure_url = "wss://holocard-hwdegne5cse4hrfy.eastus-01.azurewebsites.net/ws"
local_url = "ws://localhost:8000/ws"

async def test_websocket():
    uri = azure_url
    async with websockets.connect(uri) as websocket:
        # Send a message
        request_data = {
            "message_type": "join_server",
        }
        await websocket.send(json.dumps(request_data))
        print("Message sent to server.")

        # Wait for a response
        response = await websocket.recv()
        print(f"Response from server: {response}")

        # Send another message
        request_data = {
            "message_type": "join_matchmaking_queue",
            "custom_game": False,
            "queue_name": "main_matchmaking",
            "game_type": "versus",
        }
        await websocket.send(json.dumps(request_data))
        print("Second message sent to server.")

        # Wait for another response
        response = await websocket.recv()
        print(f"Response from server: {response}")

# Run the test script
asyncio.get_event_loop().run_until_complete(test_websocket())
