import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_NOTIFICATION
from app.db import SyncSessionLocal
from app.models import Order
from app.publisher import publish_status
from app.redis_client import sync_redis_client


def callback(message):
  try:
    order = json.loads(message.data.decode("utf-8"))
    order_id = order["order_id"]

    # deduplication guard
    if not sync_redis_client.set(f"processed:notification:{order_id}", 1, nx=True, ex=86400):
      message.ack()
      return

    with SyncSessionLocal() as session:
      with session.begin():
        order_row = session.get(Order, order_id)
        order_row.notification_status = "done"

    publish_status(order_id, "notification", "done")
    message.ack()

  except Exception as e:
    print(f"notification subscriber failed: {e}")
    message.nack()


def start_notification_subscriber():
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_NOTIFICATION)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"Notification subscriber listening on {sub_path}")
  return streaming_pull
