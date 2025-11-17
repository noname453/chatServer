import asyncio
import websockets
import os
import http

# This set will store all connected client websockets
CONNECTED_CLIENTS = set()

async def health_check(connection, request):
    """
    This function handles incoming HTTP requests before they become WebSockets.
    Render sends 'HEAD' or 'GET' requests to check if the app is running.
    We answer these with a simple '200 OK' so Render knows we are alive.
    """
    if request.path == "/healthz" or request.method == "HEAD":
        return http.HTTPStatus.OK, [], b"OK\n"
    # Return None to tell the library: "This isn't a health check, proceed with WebSocket handshake"
    return None

async def handler(websocket):
    """
    Handle a new client connection.
    """
    print(f"New client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            
            # improved broadcasting: send to everyone EXCEPT the sender
            # We verify the client is still in the set before sending
            other_clients = {client for client in CONNECTED_CLIENTS if client != websocket}
            
            if other_clients:
                # websockets.broadcast is much more stable than writing our own loop
                websockets.broadcast(other_clients, message)
                
    except websockets.exceptions.ConnectionClosed:
        print("A client disconnected")
    finally:
        CONNECTED_CLIENTS.discard(websocket)

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}...")
    
    # We add 'process_request=health_check' to handle the Render pings
    async with websockets.serve(handler, "0.0.0.0", port, process_request=health_check):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())