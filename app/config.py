from dotenv import load_dotenv
import os

load_dotenv()

# pub sub settings
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
PUBSUB_EMULATOR_HOST = os.getenv("PUBSUB_EMULATOR_HOST")

# topic names
TOPIC_ORDER_PLACED = "order-placed"
TOPIC_STATUS_UPDATES = "status-updates"
TOPIC_DLQ = "order-placed-dlq"

# subscription names
SUB_INVENTORY = "inventory-sub"
SUB_NOTIFICATION = "notification-sub"
SUB_ANALYTICS = "analytics-sub"
SUB_STATUS_RELAY = "status-relay-sub"
SUB_DLQ = "dlq-sub"

# Database URLs
DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
