import asyncio
import websockets
import json

azure_url = "wss://holocard-hwdegne5cse4hrfy.eastus-01.azurewebsites.net/ws"
local_url = "ws://localhost:8000/ws"

async def listen(ws):
    """Listen for incoming messages and print them."""
    print("Starting listening thread.")
    while True:
        try:
            message = await ws.recv()
            print(f"Received: {message}")
        except websockets.ConnectionClosed:
            print("Connection closed.")
            break
        except Exception as e:
            print(f"Error while receiving message: {e}")
            break
    print("Exiting")

async def get_input():
    """Asynchronously get input from the user."""
    return await asyncio.to_thread(input)

async def send(ws):
    """Send messages manually."""
    while True:
        try:
            message = await get_input()
            if message == "start":
                print("Joining Server.")
                request_data = {
                    "message_type": "join_server",
                }
                message = json.dumps(request_data)
            elif message == "queue":
                print("Queuing up.")
                request_data = {
                    "message_type": "join_matchmaking_queue",
                    "custom_game": False,
                    "queue_name": "main_matchmaking_normal",
                    "game_type": "versus",
                }
                message = json.dumps(request_data)
            await ws.send(message)
        except websockets.ConnectionClosed:
            print("Connection closed.")
            break

async def main():
    uri = local_url
    async with websockets.connect(uri) as ws:
        # Create and start listening and sending tasks
        listen_task = asyncio.create_task(listen(ws))
        send_task = asyncio.create_task(send(ws))

        # Run both tasks until the connection closes
        await asyncio.gather(listen_task, send_task)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
