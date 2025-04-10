from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import ssl, json
import uvicorn, asyncio
from sentiments import get_sentiment
import datetime

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.active_users_by_id = {}
        self.active_users = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.active_users_by_id[client_id] = websocket
        self.active_users[client_id] = {'status': 'connected'}
        return json.dumps({"connections": list(self.active_users_by_id.keys()), "active_users": self.active_users})

    def disconnect(self, websocket: WebSocket, client_id: str):
        self.active_connections.remove(websocket)
        self.active_users[client_id] = {'status': 'disconnected'}

    
    def setActive(self, client_id: str):
        if client_id in self.active_users:
            self.active_users[client_id]['status'] = 'active'
        else:
            self.active_users[client_id] = {'status': 'active'}

    def setInactive(self, client_id: str):
        if client_id in self.active_users:
            self.active_users[client_id]['status'] = 'inactive'
        else:
            self.active_users[client_id] = {'status': 'inactive'}


    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, client_id: str, message: str):
        for connection in self.active_connections:
            try:
                # Essayer de parser le message comme JSON
                try:
                    message_obj = json.loads(message)
                except:
                    # Si le message n'est pas un JSON valide, le traiter comme une chaîne simple
                    message_obj = message
                
                # Créer l'objet de réponse
                response = {
                    "message": message_obj,
                    "connections": list(self.active_users_by_id.keys()),
                    "active_users": self.active_users
                }
                
                # Envoyer la réponse
                await connection.send_text(json.dumps(response))
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.active_connections.remove(connection)


    async def get_active_connections(self):
        return self.active_connections
    
    async def get_active_users(self):
        return self.active_users

manager = ConnectionManager()


@app.get("/")
async def get():
    return {"message": "CONNECTED TO YNOV SERVER"}

@app.get("/get_active_connections")
def get_active_connections():
    return json.dumps({"connections": list(manager.active_users_by_id.keys())})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1000)
                
                # Analyser le sentiment du message
                sentiment = get_sentiment(data)
                
                # Obtenir l'horodatage actuel
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                
                # Ajouter le sentiment au message personnel
                await manager.send_personal_message(f"You wrote: {data} (Sentiment: {sentiment})", websocket)
                
                # Créer un objet JSON avec le message, son sentiment, le pseudo et l'horodatage
                message_with_sentiment = json.dumps({
                    "text": data,
                    "sentiment": sentiment,
                    "username": client_id,
                    "timestamp": timestamp
                })
                
                # Diffuser le message avec le sentiment
                await manager.broadcast(client_id, message_with_sentiment)
                print(f"Received from {client_id}: {data} (Sentiment: {sentiment})")
            except asyncio.TimeoutError:
                print("Timeout. Checking connection status.")


    except WebSocketDisconnect:
       manager.disconnect(websocket, client_id)
       await manager.broadcast(client_id, json.dumps({"text": "left the chat", "username": client_id, "timestamp": datetime.datetime.now().strftime("%H:%M:%S")}))
    finally:
        await websocket.close()
        print("Cleaned up connection")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7890)