from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists
from app.config import (
  PROJECT_ID,
  TOPIC_ORDER_PLACED, TOPIC_STATUS_UPDATES, TOPIC_DLQ,
  SUB_INVENTORY, SUB_ANALYTICS, SUB_NOTIFICATION,
  SUB_STATUS_RELAY, SUB_DLQ
)

# responsible for creating topics and subscriptions on startup
def ensure_topic(publisher, topic_id):
  path = publisher.topic_path(PROJECT_ID, topic_id)
  try:
    publisher.create_topic(name=path)
  except AlreadyExists:
    pass
  return path

def ensure_subscription(subscriber, topic_id, sub_id, dlq_topic_path=None):
  sub_path = subscriber.subscription_path(PROJECT_ID, sub_id)
  topic_path = subscriber.topic_path(PROJECT_ID, topic_id)
  subscription = pubsub_v1.types.Subscription(
    name=sub_path,
    topic=topic_path,
  )
  if dlq_topic_path:
    subscription.dead_letter_policy = pubsub_v1.types.DeadLetterPolicy(
      dead_letter_topic=dlq_topic_path,
      max_delivery_attempts=5,
    )
  try:
    subscriber.create_subscription(request=subscription)
  except AlreadyExists:
    pass
  return sub_path

# Called during startup to setup the topics and subscriptions
def setup_pubsub():
  publisher = pubsub_v1.PublisherClient()
  subscriber = pubsub_v1.SubscriberClient()

  # topics
  ensure_topic(publisher, TOPIC_ORDER_PLACED)
  ensure_topic(publisher, TOPIC_STATUS_UPDATES)
  dlq_path = ensure_topic(publisher, TOPIC_DLQ)

  # subscriptions
  ensure_subscription(subscriber, TOPIC_ORDER_PLACED, SUB_INVENTORY, dlq_topic_path=dlq_path)
  ensure_subscription(subscriber, TOPIC_ORDER_PLACED, SUB_NOTIFICATION, dlq_topic_path=dlq_path)
  ensure_subscription(subscriber, TOPIC_ORDER_PLACED, SUB_ANALYTICS, dlq_topic_path=dlq_path)

  # subscription for status-update
  ensure_subscription(subscriber, TOPIC_STATUS_UPDATES, SUB_STATUS_RELAY)

  # subscription on DLQ topic (to inspect failure)
  ensure_subscription(subscriber, TOPIC_DLQ, SUB_DLQ)