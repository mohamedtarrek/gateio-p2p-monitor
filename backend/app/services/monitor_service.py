"""
Core monitoring service for Gate.io P2P price tracking.
Manages polling loop, comparison logic, and notification deduplication.
"""
import asyncio
import time
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from app.models import (
    MonitorSettings, P2PAdvertisement, NotificationPayload, 
    SystemStatus, NotificationLog
)
from app.services.gateio_scraper import scraper
from app.services.telegram_service import telegram_service
from app.utils import setup_logger

logger = setup_logger(__name__)

@dataclass
class MonitorState:
    """Internal state tracking for the monitor."""
    status: SystemStatus = SystemStatus.STOPPED
    last_checked: Optional[datetime] = None
    notifications_sent: int = 0
    settings: Optional[MonitorSettings] = None
    last_my_ad: Optional[P2PAdvertisement] = None
    notified_ads: Dict[str, float] = field(default_factory=dict)  # ad_id -> price
    notification_history: List[NotificationLog] = field(default_factory=list)
    error_count: int = 0
    last_error: Optional[str] = None
    start_time: Optional[float] = None
    _task: Optional[asyncio.Task] = None

class MonitorService:
    """
    Main monitoring service that orchestrates price checking and notifications.
    Uses asyncio for non-blocking concurrent operations.
    """

    def __init__(self):
        self.state = MonitorState()
        self._lock = asyncio.Lock()

    async def update_settings(self, settings: MonitorSettings) -> bool:
        """
        Update monitor settings immediately without restarting.

        Args:
            settings: New configuration settings

        Returns:
            True if settings applied successfully
        """
        async with self._lock:
            # Validate Telegram token by getting bot info
            bot_info = await telegram_service.get_bot_info(settings.telegram_bot_token)
            if not bot_info:
                logger.error("Invalid Telegram bot token provided")
                return False

            self.state.settings = settings
            self.state.notified_ads.clear()  # Reset deduplication on major changes

            logger.info(f"Settings updated: trader={settings.trader_name}, "
                       f"min_qty={settings.min_quantity}, interval={settings.polling_interval}s")
            return True

    async def start(self) -> bool:
        """
        Start the monitoring loop.

        Returns:
            True if started successfully
        """
        async with self._lock:
            if self.state.status == SystemStatus.RUNNING:
                logger.warning("Monitor is already running")
                return True

            if not self.state.settings:
                logger.error("Cannot start: no settings configured")
                return False

            self.state.status = SystemStatus.RUNNING
            self.state.start_time = time.time()
            self.state.error_count = 0
            self.state.last_error = None

            # Create background task for monitoring
            self.state._task = asyncio.create_task(self._monitoring_loop())

            logger.info("Monitor started successfully")
            return True

    async def stop(self) -> bool:
        """
        Stop the monitoring loop gracefully.

        Returns:
            True if stopped successfully
        """
        async with self._lock:
            if self.state.status != SystemStatus.RUNNING:
                logger.warning("Monitor is not running")
                return True

            self.state.status = SystemStatus.STOPPED

            # Cancel background task if running
            if self.state._task and not self.state._task.done():
                self.state._task.cancel()
                try:
                    await self.state._task
                except asyncio.CancelledError:
                    pass

            self.state._task = None
            logger.info("Monitor stopped")
            return True

    async def _monitoring_loop(self):
        """Main monitoring loop that runs continuously."""
        while self.state.status == SystemStatus.RUNNING:
            try:
                await self._check_prices()

                # Wait for next poll interval
                interval = self.state.settings.polling_interval if self.state.settings else 10
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.state.error_count += 1
                self.state.last_error = str(e)

                # Don't stop on error - wait and retry
                await asyncio.sleep(5)

    async def _check_prices(self):
        """Execute a single price check cycle."""
        settings = self.state.settings
        if not settings:
            return

        try:
            # Step 1: Find our own ad
            my_ad = await scraper.find_my_ad(
                trader_name=settings.trader_name,
                crypto="USDT",
                fiat="EGP",
                trade_type="sell"
            )

            if not my_ad:
                logger.warning(f"Could not find your ad for trader: {settings.trader_name}")
                self.state.last_checked = datetime.utcnow()
                return

            self.state.last_my_ad = my_ad

            # Step 2: Get competitor ads
            competitors = await scraper.get_competitor_ads(
                my_trader_name=settings.trader_name,
                min_quantity=settings.min_quantity,
                payment_method=settings.payment_method,
                crypto="USDT",
                fiat="EGP",
                trade_type="sell"
            )

            # Step 3: Check for higher-priced competitors
            notifications_to_send = []
            for competitor in competitors:
                # Condition: competitor price > my price
                if competitor.price > my_ad.price:
                    # Deduplication: check if we already notified for this price
                    last_notified_price = self.state.notified_ads.get(competitor.ad_id)

                    # Only notify if price changed or never notified
                    if last_notified_price is None or abs(competitor.price - last_notified_price) > 0.01:
                        payload = NotificationPayload(
                            competitor_name=competitor.trader_name,
                            competitor_price=competitor.price,
                            my_price=my_ad.price,
                            price_difference=competitor.price - my_ad.price,
                            max_quantity=competitor.max_amount,
                            ad_link=competitor.ad_link,
                            timestamp=datetime.utcnow(),
                            payment_method=settings.payment_method
                        )
                        notifications_to_send.append((competitor.ad_id, competitor.price, payload))

            # Step 4: Send notifications
            for ad_id, price, payload in notifications_to_send:
                try:
                    message_id = await telegram_service.send_notification(
                        bot_token=settings.telegram_bot_token,
                        chat_id=settings.telegram_chat_id,
                        payload=payload
                    )

                    if message_id:
                        # Update deduplication tracking
                        self.state.notified_ads[ad_id] = price

                        # Add to history
                        log = NotificationLog(
                            id=f"{ad_id}_{int(time.time())}",
                            payload=payload,
                            sent_at=datetime.utcnow(),
                            telegram_message_id=message_id,
                            status="sent"
                        )
                        self.state.notification_history.append(log)
                        self.state.notifications_sent += 1

                        logger.info(f"Notification sent for {payload.competitor_name}: "
                                   f"{payload.competitor_price} vs {payload.my_price}")

                except Exception as e:
                    logger.error(f"Failed to send notification: {e}")

            # Cleanup old deduplication entries (older than 1 hour)
            # This allows re-notification if price returns to previous level after 1 hour
            # (Implementation would track timestamps, simplified here)

            self.state.last_checked = datetime.utcnow()
            self.state.last_error = None

        except Exception as e:
            logger.error(f"Price check failed: {e}")
            self.state.error_count += 1
            self.state.last_error = str(e)

    def get_status(self) -> dict:
        """
        Get current monitor status.

        Returns:
            Status dictionary for API response
        """
        uptime = None
        if self.state.start_time and self.state.status == SystemStatus.RUNNING:
            uptime = time.time() - self.state.start_time

        return {
            "status": self.state.status,
            "last_checked": self.state.last_checked,
            "notifications_sent": self.state.notifications_sent,
            "current_settings": self.state.settings,
            "error_message": self.state.last_error,
            "uptime_seconds": uptime,
            "error_count": self.state.error_count,
            "last_my_price": self.state.last_my_ad.price if self.state.last_my_ad else None
        }

    def get_notification_history(self, limit: int = 50) -> List[NotificationLog]:
        """
        Get recent notification history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of notification logs (most recent first)
        """
        history = sorted(
            self.state.notification_history,
            key=lambda x: x.sent_at,
            reverse=True
        )
        return history[:limit]

    def clear_history(self):
        """Clear notification history."""
        self.state.notification_history.clear()
        self.state.notified_ads.clear()
        self.state.notifications_sent = 0
        logger.info("Notification history cleared")

# Global monitor instance
monitor = MonitorService()
