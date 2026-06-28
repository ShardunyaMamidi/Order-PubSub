import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, SUB_ANALYTICS
from app.db import SyncSessionLocal
from app.models import Order
from app.publisher import publish_status


def callback(message):
  try:
    order = json.loads(message.data.decode("utf-8"))
    order_id = order["order_id"]

    with SyncSessionLocal() as session:
      with session.begin():
        order_row = session.get(Order, order_id)
        order_row.analytics_status = "done"

    publish_status(order_id, "analytics", "done")
    message.ack()

  except Exception as e:
    print(f"analytics subscriber failed: {e}")
    message.nack()


def start_analytics_subscriber():
  subscriber = pubsub_v1.SubscriberClient()
  sub_path = subscriber.subscription_path(PROJECT_ID, SUB_ANALYTICS)
  streaming_pull = subscriber.subscribe(sub_path, callback=callback)
  print(f"Analytics subscriber listening on {sub_path}")
  return streaming_pull
