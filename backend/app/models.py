"""
Pydantic models for request/response validation and data structures.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SystemStatus(str, Enum):
    """System monitoring status."""
    RUNNING = "Running"
    STOPPED = "Stopped"
    ERROR = "Error"

class PaymentMethod(BaseModel):
    """Payment method details."""
    name: str
    id: Optional[str] = None

class P2PAdvertisement(BaseModel):
    """Gate.io P2P advertisement model."""
    ad_id: str = Field(..., description="Unique advertisement ID")
    trader_name: str = Field(..., description="Trader display name")
    price: float = Field(..., description="Price per USDT in EGP")
    currency: str = Field(default="EGP", description="Fiat currency")
    crypto_currency: str = Field(default="USDT", description="Crypto currency")
    min_amount: float = Field(..., description="Minimum trade amount")
    max_amount: float = Field(..., description="Maximum trade amount")
    available_quantity: float = Field(..., description="Available USDT quantity")
    payment_methods: List[str] = Field(default=[], description="Accepted payment methods")
    trade_type: str = Field(..., description="Buy or Sell ad")
    ad_link: str = Field(..., description="Direct link to advertisement")
    trader_id: Optional[str] = None

class MonitorSettings(BaseModel):
    """User-configurable monitor settings."""
    trader_name: str = Field(..., description="Your Gate.io trader name")
    min_quantity: float = Field(default=100.0, ge=1, description="Minimum quantity to monitor")
    telegram_bot_token: str = Field(..., description="Telegram Bot API Token")
    telegram_chat_id: str = Field(..., description="Telegram Chat ID")
    polling_interval: int = Field(default=10, ge=5, le=300, description="Polling interval in seconds")
    payment_method: str = Field(default="Instapay", description="Payment method to filter")

class NotificationPayload(BaseModel):
    """Telegram notification content."""
    competitor_name: str
    competitor_price: float
    my_price: float
    price_difference: float
    max_quantity: float
    ad_link: str
    timestamp: datetime
    payment_method: str

class NotificationLog(BaseModel):
    """Stored notification record."""
    id: str
    payload: NotificationPayload
    sent_at: datetime
    telegram_message_id: Optional[int] = None
    status: str = "sent"

class StatusResponse(BaseModel):
    """System status response."""
    status: SystemStatus
    last_checked: Optional[datetime] = None
    notifications_sent: int = 0
    current_settings: Optional[MonitorSettings] = None
    error_message: Optional[str] = None
    uptime_seconds: Optional[float] = None

class UpdateResponse(BaseModel):
    """Settings update response."""
    success: bool
    message: str
    updated_settings: Optional[MonitorSettings] = None
    error: Optional[str] = None
