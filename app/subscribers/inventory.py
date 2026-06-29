import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_INVENTORY
from app.db import SyncSessionLocal
from app.models import Order
from app.publisher import publish_status
from app.redis_client import sync_redis_client

# This is the function that gets executed when we receive the data from message queue

def callback(message):
  try:
    order = json.loads(message.data.decode("utf-8"))
    order_id = order["order_id"]

    # deduplication guard — check only, don't set yet
    if sync_redis_client.exists(f"processed:inventory:{order_id}"):
      message.ack()
      return

    # forced failure for DLQ demo
    if order["item"] == "fail":
      raise Exception("forced failure for DLQ demo")

    with SyncSessionLocal() as session:
      with session.begin():
        order_row = session.get(Order, order_id)
        order_row.inventory_status = "done"

    # mark as processed only after successful work
    sync_redis_client.set(f"processed:inventory:{order_id}", 1, ex=86400)
    publish_status(order_id, "inventory", "done")
    message.ack()

  except Exception as e:
    print(f"inventory subscriber failed {e}")
    message.nack()

# This is where we initialize a subscriber/consumer
def start_inventory_subscriber():
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_INVENTORY)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"Inventory subscriber listening on {sub_path}")
  return streaming_pull