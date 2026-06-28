from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

# This is used in db.py to create tables during startup
Base = declarative_base()


# Schema for Order
class Order(Base):
  __tablename__ = "orders"

  order_id = Column(String, primary_key=True)
  item = Column(String, nullable=False)
  inventory_status = Column(String, default="pending")
  notification_status = Column(String, default="pending")
  analytics_status = Column(String, default="pending")
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
