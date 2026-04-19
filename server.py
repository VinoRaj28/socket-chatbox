# server.py
import asyncio
import websockets
import json
from datetime import datetime

clients = set()
nicknames = {}

async def broadcast(message, sender_nickname=None):
    """Broadcast message to all connected clients"""
    if clients:
        for client in clients:
            try:
                await client.send(message)
            except:
                pass

async def handle_client(websocket):
    """Handle each client connection"""
    nickname = None
    try:
        # Wait for client to send a nickname
        initial_message = await websocket.recv()
        data = json.loads(initial_message)
        nickname = data.get('nickname', 'Anonymous')
        
        clients.add(websocket)
        nicknames[websocket] = nickname
        
        # Announce user joined
        join_message = json.dumps({
            'type': 'system',
            'message': f'{nickname} joined the chat!',
            'timestamp': datetime.now().isoformat()
        })
        await broadcast(join_message)
        
        # Handle incoming messages
        async for message in websocket:
            data = json.loads(message)
            chat_message = json.dumps({
                'type': 'message',
                'nickname': nickname,
                'message': data.get('message', ''),
                'timestamp': datetime.now().isoformat()
            })
            await broadcast(chat_message)
            
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client on disconnect
        if websocket in clients:
            clients.remove(websocket)
        if websocket in nicknames:
            nickname = nicknames[websocket]
            del nicknames[websocket]
            leave_message = json.dumps({
                'type': 'system',
                'message': f'{nickname} left the chat!',
                'timestamp': datetime.now().isoformat()
            })
            await broadcast(leave_message)

async def main():
    """Start the WebSocket server"""
    async with websockets.serve(handle_client, '0.0.0.0', 8765):
        print("WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())