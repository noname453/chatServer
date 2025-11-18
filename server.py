from aiohttp import web
import os

# Store connected clients
CONNECTED_CLIENTS = set()

async def handler(request):
    """
    This single function handles BOTH health checks and WebSocket connections.
    """
    # 1. Check if this is a WebSocket connection attempt
    if request.headers.get("Upgrade", "").lower() == "websocket":
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        print("Client connected")
        CONNECTED_CLIENTS.add(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    print(f"Received: {msg.data}")
                    # Broadcast to all other clients
                    for client in CONNECTED_CLIENTS:
                        if client != ws:
                            # aiohttp handles errors (like disconnected clients) gracefully here
                            await client.send_str(msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    print('ws connection closed with exception %s', ws.exception())

        finally:
            CONNECTED_CLIENTS.remove(ws)
            print("Client disconnected")
        
        return ws

    # 2. If it's NOT a WebSocket (e.g. Render health check), just return text
    else:
        return web.Response(text="Signaling Server is running!")

async def main():
    # Get the port from Render
    port = int(os.environ.get("PORT", 8080))
    
    app = web.Application()
    # Route all traffic ('/') to our handler function
    app.add_routes([web.get('/', handler)])
    
    return app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # aiohttp's way of starting the server
    web.run_app(main(), port=port)