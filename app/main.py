# entrypoint of the application

from fastapi import FastAPI
from app.pubsub_setup import setup_pubsub
from app.db import create_tables
from app.redis_client import redis_client
from app.schemas import OrderRequest, OrderResponse
from uuid import uuid4
from app.db import AsyncSessionLocal
from app.models import Order
from app.publisher import publish_order
from app.subscribers.inventory import start_inventory_subscriber
from app.subscribers.notification import start_notification_subscriber
from app.subscribers.analytics import start_analytics_subscriber
from app.subscribers.status_relay import start_status_relay
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from app.ws_manager import manager

# Create app instance
app = FastAPI()

# Startup handling
@app.on_event("startup")
async def startup():
  setup_pubsub()
  await create_tables()
  await redis_client.ping()
  start_inventory_subscriber()
  start_notification_subscriber()
  start_analytics_subscriber()
  loop = asyncio.get_event_loop()
  start_status_relay(loop, manager)
  print("Startup Completed")

@app.get("/")
async def root():
  return {"status": "ok"}

@app.post("/order", response_model=OrderResponse)
async def place_order(body: OrderRequest):
  order_id = str(uuid4())

  # Writing to postgres first
  async with AsyncSessionLocal() as session:
    async with session.begin():
      session.add(Order(
        order_id=order_id,
        item=body.item,
        inventory_status="pending",
        notification_status="pending",
        analytics_status="pending"
      ))

  # publish to the pubsub
  publish_order({
    "order_id": order_id,
    "item": body.item,
    "quantity": body.quantity
  })

  # increment redis counter
  await redis_client.incr("stats:orders_total")

  return OrderResponse(
    order_id=order_id,
    item=body.item,
    status="pending"
  )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await manager.connect(websocket=websocket)
  try:
    while True:
      await websocket.receive_text()
  except WebSocketDisconnect:
    manager.disconnect(websocket=websocket)
