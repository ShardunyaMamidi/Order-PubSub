import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_DLQ
from app.db import SyncSessionLocal
from app.models import Order
from app.redis_client import sync_redis_client
from app.publisher import publish_status

def callback(message):
  try:
    order = json.loads(message.data.decode("utf-8"))
    order_id = order["order_id"]

    with SyncSessionLocal() as session:
      with session.begin():
        order_row = session.get(Order, order_id)
        if order_row.inventory_status == "pending":
          order_row.inventory_status = "failed"
          publish_status(order_id, "inventory", "failed")
        if order_row.notification_status == "pending":
          order_row.notification_status = "failed"
          publish_status(order_id, "notification", "failed")
        if order_row.analytics_status == "pending":
          order_row.analytics_status = "failed"
          publish_status(order_id, "analytics", "failed")

      sync_redis_client.incr("stats:dlq_count")
      print(f"DLQ: order {order_id} marked as failed")
      message.ack()

  except Exception as e:
    print(f"DLQ handler error: {e}")
    message.ack()

def start_dlq_handler():
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_DLQ)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"DLQ handler listening on {sub_path}")
  return streaming_pull