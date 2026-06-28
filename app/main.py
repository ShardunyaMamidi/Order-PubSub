# entrypoint of the application

from fastapi import FastAPI
from app.pubsub_setup import setup_pubsub
from app.db import create_tables
from app.redis_client import redis_client

# Create app instance
app = FastAPI()

# Startup handling
@app.on_event("startup")
async def startup():
  setup_pubsub()
  await create_tables()
  await redis_client.ping()
  print("Startup Completed")

@app.get("/")
async def root():
  return {"status": "ok"}
