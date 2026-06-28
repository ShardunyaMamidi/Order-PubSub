from pydantic import BaseModel

# Request model
class OrderRequest(BaseModel):
  item: str
  quantity: int = 1

# Response model
class OrderResponse(BaseModel):
  order_id: str
  item: str
  status: str

  