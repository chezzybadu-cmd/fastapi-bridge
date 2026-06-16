from pydantic import BaseModel
from typing import Optional

# --- Signal model ---
class Signal(BaseModel):
    """
    Represents a trading signal stored in the 'signals' table.
    """
    id: Optional[int] = None
    timestamp: str
    symbol: str
    action: str          # "buy" or "sell"
    confidence: float    # confidence score %
    price: float         # market price at signal
    severity: str        # "weak", "strong", "critical"

    class Config:
        orm_mode = True


# --- Escalation log model ---
class EscalationLog(BaseModel):
    """
    Represents an escalation record stored in the 'escalation_log' table.
    """
    id: Optional[int] = None
    timestamp: str
    symbol: str
    action: str
    confidence: float
    price: float
    recipient: str       # phone number or user ID
    outcome: str         # "answered", "missed", "sms_sent"

    class Config:
        orm_mode = True


# --- Token model ---
class Token(BaseModel):
    """
    Represents an Expo push token stored in the 'tokens' table.
    """
    id: Optional[int] = None
    token: str
    registered_at: Optional[str] = None

    class Config:
        orm_mode = True
