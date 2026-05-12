"""
Telegram Bot service for sending notifications.
Uses official Telegram Bot API with async HTTP client.
"""
import httpx
from datetime import datetime
from typing import Optional
from app.models import NotificationPayload
from app.config import settings
from app.utils import setup_logger

logger = setup_logger(__name__)

class TelegramService:
    """
    Telegram notification service.
    Sends formatted messages about competitor price changes.
    """

    def __init__(self):
        self.base_url = "https://api.telegram.org/bot"
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def send_notification(
        self,
        bot_token: str,
        chat_id: str,
        payload: NotificationPayload
    ) -> Optional[int]:
        """
        Send a formatted notification message to Telegram.

        Args:
            bot_token: Telegram Bot API token
            chat_id: Target chat ID
            payload: Notification content

        Returns:
            Message ID if successful, None otherwise
        """
        try:
            message = self._format_message(payload)

            url = f"{self.base_url}{bot_token}/sendMessage"

            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)

                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get("result", {}).get("message_id")
                    logger.info(f"Telegram notification sent: message_id={message_id}")
                    return message_id
                else:
                    error_text = response.text
                    logger.error(f"Telegram API error {response.status_code}: {error_text}")
                    return None

        except httpx.RequestError as e:
            logger.error(f"Network error sending Telegram message: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return None

    def _format_message(self, payload: NotificationPayload) -> str:
        """
        Format notification payload into HTML message.

        Args:
            payload: Notification data

        Returns:
            Formatted HTML string for Telegram
        """
        # Determine emoji based on price difference
        diff_emoji = "🟢" if payload.price_difference > 0 else "🔴"

        # Format timestamp
        time_str = payload.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        message = f"""
<b>🔔 Gate.io P2P Price Alert</b>

<b>Competitor:</b> <code>{payload.competitor_name}</code>
<b>Competitor Price:</b> <code>{payload.competitor_price:,.2f} EGP</code>
<b>Your Price:</b> <code>{payload.my_price:,.2f} EGP</code>
<b>Difference:</b> {diff_emoji} <code>{payload.price_difference:+.2f} EGP</code>
<b>Max Quantity:</b> <code>{payload.max_quantity:,.2f} USDT</code>
<b>Payment:</b> <code>{payload.payment_method}</code>

<b>🔗 Ad Link:</b> <a href="{payload.ad_link}">View on Gate.io</a>

<i>⏰ {time_str}</i>
        """.strip()

        return message

    async def send_test_message(
        self,
        bot_token: str,
        chat_id: str
    ) -> bool:
        """
        Send a test message to verify Telegram configuration.

        Args:
            bot_token: Bot token to test
            chat_id: Chat ID to test

        Returns:
            True if message sent successfully
        """
        try:
            url = f"{self.base_url}{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": "✅ <b>Gate.io P2P Monitor</b>\n\nYour Telegram notifications are configured correctly!\n\n<i>You will receive alerts when competitors list higher prices than yours.</i>",
                "parse_mode": "HTML"
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Test message failed: {e}")
            return False

    async def get_bot_info(self, bot_token: str) -> Optional[dict]:
        """Get bot information to validate token."""
        try:
            url = f"{self.base_url}{bot_token}/getMe"
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json().get("result")
                return None
        except Exception:
            return None

# Global service instance
telegram_service = TelegramService()
