from fastapi import WebSocket

# A manager that handles the ws connections and broadcasting data to the subscribed clients
class ConnectionManager:
  def __init__(self):
    self.active_connection: list[WebSocket] = []

  async def connect(self, websocket: WebSocket):
    await websocket.accept()
    self.active_connection.append(websocket)

  def disconnect(self, websocket: WebSocket):
    self.active_connection.remove(websocket)

  async def broadcast(self, data: dict):
    for connection in self.active_connection:
      await connection.send_json(data)

manager = ConnectionManager()
  