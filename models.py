from pydantic import BaseModel

class SignalPayload(BaseModel):
    symbol: str
    signal_type: str
    score: int
    price: float
    timestamp: str
