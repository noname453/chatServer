import asyncio
import websockets

async def receive_messages(websocket):
    """
    This function will run in the background, listening for messages
    from the server and printing them.
    """
    try:
        async for message in websocket:
            # We add a newline before the "Friend:" message
            # and then re-print the "You: " prompt for a clean CLI experience
            print(f"\nFriend: {message}")
            print("You: ", end="", flush=True)
            
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection to server lost.")

async def send_messages(websocket):
    """
    This function will run, waiting for you to type a message.
    """
    while True:
        # This is a special way to run a blocking function (like input())
        # in an async program without freezing everything.
        message = await asyncio.to_thread(input, "You: ")
        
        if message.lower() == 'exit':
            break
        
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            break

async def main():
    """
    Connect to the WebSocket server and start the send/receive tasks.
    """
    #
    # !!! IMPORTANT !!!
    # REPLACE THIS with your server's public URL
    # It will start with wss:// (secure websocket)
    # e.g., "wss://my-cool-chat.onrender.com"
    #
    uri = "wss://YOUR_SERVER_URL_GOES_HERE"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            print("Type your messages and press Enter. Type 'exit' to quit.")
            
            # Start both tasks. `asyncio.gather` runs them concurrently.
            receive_task = asyncio.create_task(receive_messages(websocket))
            send_task = asyncio.create_task(send_messages(websocket))
            
            await asyncio.gather(receive_task, send_task)
            
    except Exception as e:
        print(f"Could not connect to server: {e}")
        print("Please check the 'uri' variable in client.py")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")