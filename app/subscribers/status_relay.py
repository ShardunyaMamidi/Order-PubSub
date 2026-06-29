import json
import asyncio
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_STATUS_RELAY
from app.ws_manager import ConnectionManager

# Callback method
def make_relay_callback(loop, manager: ConnectionManager):
  def callback(message):
    update = json.loads(message.data.decode("utf-8"))
    asyncio.run_coroutine_threadsafe(
      manager.broadcast(update),
      loop
    )
    message.ack()
  return callback

# Start the subscriber
def start_status_relay(loop, manager: ConnectionManager):
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_STATUS_RELAY)
  callback = make_relay_callback(loop=loop, manager=manager)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"Status relay listening on {sub_path}")
  return streaming_pull