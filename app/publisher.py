
# handles publishing events

import json
from google.cloud import pubsub_v1
from app.config import PROJECT_ID, TOPIC_ORDER_PLACED, TOPIC_STATUS_UPDATES

# publisher client
publisher = pubsub_v1.PublisherClient()

# publish order to topic order placed
def publish_order(order: dict):
  topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ORDER_PLACED)
  data = json.dumps(order).encode("utf-8")
  future = publisher.publish(topic_path, data)
  future.result()

# publish the status updated
def publish_status(order_id: str, stage: str, status: str):
  topic_path = publisher.topic_path(PROJECT_ID, TOPIC_STATUS_UPDATES)
  data = json.dumps({
    "order_id": order_id,
    "stage": stage,
    "status": status,
  }).encode("utf-8")
  future = publisher.publish(topic_path, data)
  furute.result()