import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_INVENTORY
from app.db import SyncSessionLocal
from app.models import Order
from app.publisher import publish_status

# This is the function that gets executed when we receive the data from message queue

def callback(message):
  try:
    order = json.loads(message.data.decode("utf-8"))
    order_id = order["order_id"]

    with SyncSessionLocal() as session:
      with session.begin():
        order_row = session.get(Order, order_id)
        order_row.inventory_status = "done"

    publish_status(order_id, "inventory", "done")
    message.ack()

  except Exception as e:
    print(f"inventory subscriber failed {e}")
    # After 5 of these nack, this message will be moved to dlq
    message.nack()

# This is where we initialize a subscriber/consumer
def start_inventory_subscriber():
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_INVENTORY)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"Inventory subscriber listening on {sub_path}")
  return streaming_pull