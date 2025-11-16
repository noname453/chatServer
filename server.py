import asyncio
import websockets
import os

# This set will store all connected client websockets
CONNECTED_CLIENTS = set()

async def handler(websocket):
    """
    Handle a new client connection.
    """
    print(f"New client connected: {websocket.remote_address}")
    # Add the new client to our set
    CONNECTED_CLIENTS.add(websocket)
    
    try:
        # This loop runs forever for each client
        # It waits for a message and then processes it
        async for message in websocket:
            print(f"Received message from {websocket.remote_address}: {message}")
            
            # We want to send this message to all *other* clients
            clients_to_send = [client for client in CONNECTED_CLIENTS if client != websocket]
            
            # If there are other clients, send the message
            if clients_to_send:
                # This creates a list of tasks to run concurrently
                await asyncio.wait([client.send(message) for client in clients_to_send])
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        # When the client disconnects (or an error occurs), remove them
        CONNECTED_CLIENTS.remove(websocket)

async def main():
    """
    Start the WebSocket server.
    """
    # Get the port from the environment variable (for deployment)
    # Default to 8080 for local testing
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Starting WebSocket server on port {port}...")
    
    # "0.0.0.0" means it will listen on all available network interfaces
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # This runs the server forever

if __name__ == "__main__":
    asyncio.run(main())