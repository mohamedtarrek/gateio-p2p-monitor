"""
Gate.io P2P scraper service.
Fetches P2P advertisements using Gate.io's official API endpoint.
Handles both API requests and fallback web scraping if needed.
"""
import httpx
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import P2PAdvertisement
from app.config import settings
from app.utils import setup_logger

logger = setup_logger(__name__)

class GateioScraper:
    """
    Scraper for Gate.io P2P marketplace.
    Uses the official /p2p/merchant/books/ads_list endpoint.
    """

    def __init__(self):
        self.base_url = "https://www.gate.com"
        self.api_url = f"{self.base_url}/api/v4/p2p/merchant/books/ads_list"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://www.gate.com",
            "Referer": "https://www.gate.com/ar/p2p/sell/USDT-EGP"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def fetch_ads(
        self,
        crypto: str = "USDT",
        fiat: str = "EGP",
        trade_type: str = "sell",  # "sell" means we want to sell USDT (buyers' ads)
        payment_method: Optional[str] = "Instapay",
        page: int = 1,
        per_page: int = 20
    ) -> List[P2PAdvertisement]:
        """
        Fetch P2P advertisements from Gate.io.

        Args:
            crypto: Cryptocurrency code (USDT, BTC, etc.)
            fiat: Fiat currency code (EGP, USD, etc.)
            trade_type: "sell" or "buy" (from seller's perspective)
            payment_method: Filter by payment method name
            page: Page number for pagination
            per_page: Items per page

        Returns:
            List of P2PAdvertisement objects
        """
        try:
            # Build request payload based on Gate.io API structure
            payload = {
                "crypto": crypto,
                "fiat": fiat,
                "side": 1 if trade_type == "sell" else 0,  # 1 = sell ads (we sell USDT), 0 = buy ads
                "page": page,
                "per_page": per_page,
                "amount": "",
                "amount_type": "fiat",
                "payment_methods": [payment_method] if payment_method else [],
                "order_by": "price",
                "sort": "desc" if trade_type == "sell" else "asc"
            }

            logger.info(f"Fetching P2P ads: {crypto}/{fiat}, type={trade_type}, payment={payment_method}")

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.post(
                    self.api_url,
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    return []

                data = response.json()

                # Parse response based on Gate.io API structure
                ads_data = data.get("data", data) if isinstance(data, dict) else data

                if not ads_data or not isinstance(ads_data, list):
                    logger.warning("No ads data returned from API")
                    return []

                advertisements = []
                for ad in ads_data:
                    try:
                        parsed_ad = self._parse_advertisement(ad, crypto, fiat, trade_type)
                        if parsed_ad:
                            advertisements.append(parsed_ad)
                    except Exception as e:
                        logger.warning(f"Failed to parse ad: {e}")
                        continue

                logger.info(f"Successfully fetched {len(advertisements)} advertisements")
                return advertisements

        except httpx.RequestError as e:
            logger.error(f"Network error fetching ads: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching ads: {e}")
            return []

    def _parse_advertisement(
        self,
        ad_data: Dict[str, Any],
        crypto: str,
        fiat: str,
        trade_type: str
    ) -> Optional[P2PAdvertisement]:
        """
        Parse raw API response into P2PAdvertisement model.
        Handles various response formats from Gate.io API.
        """
        try:
            # Extract fields with fallback keys for different API versions
            ad_id = str(ad_data.get("id", ad_data.get("ad_id", "")))
            if not ad_id:
                return None

            # Trader info - could be nested or flat
            trader_info = ad_data.get("merchant", ad_data.get("user", ad_data.get("trader", {}))
            if isinstance(trader_info, dict):
                trader_name = trader_info.get("nickname", trader_info.get("name", "Unknown"))
                trader_id = str(trader_info.get("id", ""))
            else:
                trader_name = ad_data.get("nickname", ad_data.get("merchant_name", "Unknown"))
                trader_id = ""

            # Price handling
            price_raw = ad_data.get("price", ad_data.get("unit_price", 0))
            price = float(price_raw) if price_raw else 0.0

            # Quantity limits
            min_amount = float(ad_data.get("min_amount", ad_data.get("min_single_order_amount", 0)))
            max_amount = float(ad_data.get("max_amount", ad_data.get("max_single_order_amount", 0)))
            available = float(ad_data.get("amount", ad_data.get("available_amount", ad_data.get("currency_amount", 0))))

            # Payment methods
            payments = ad_data.get("payments", ad_data.get("payment_methods", []))
            payment_names = []
            if isinstance(payments, list):
                for p in payments:
                    if isinstance(p, dict):
                        payment_names.append(p.get("name", p.get("payment_method_name", "")))
                    elif isinstance(p, str):
                        payment_names.append(p)

            # Build ad link
            ad_link = f"https://www.gate.com/ar/p2p/{trade_type}/{crypto}-{fiat}?ad_id={ad_id}"

            return P2PAdvertisement(
                ad_id=ad_id,
                trader_name=trader_name,
                price=price,
                currency=fiat,
                crypto_currency=crypto,
                min_amount=min_amount,
                max_amount=max_amount,
                available_quantity=available,
                payment_methods=payment_names,
                trade_type=trade_type,
                ad_link=ad_link,
                trader_id=trader_id
            )

        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Error parsing ad data: {e}")
            return None

    async def find_my_ad(
        self,
        trader_name: str,
        crypto: str = "USDT",
        fiat: str = "EGP",
        trade_type: str = "sell"
    ) -> Optional[P2PAdvertisement]:
        """
        Find the user's own advertisement by trader name.

        Args:
            trader_name: Your Gate.io trader name
            crypto: Cryptocurrency
            fiat: Fiat currency
            trade_type: Trade type

        Returns:
            Your P2PAdvertisement or None if not found
        """
        # Fetch multiple pages to find our ad
        for page in range(1, 4):
            ads = await self.fetch_ads(crypto, fiat, trade_type, page=page, per_page=20)

            for ad in ads:
                if ad.trader_name.lower().strip() == trader_name.lower().strip():
                    logger.info(f"Found your ad: {ad.ad_id} at price {ad.price}")
                    return ad

            if len(ads) < 20:  # Last page
                break

        logger.warning(f"Could not find ad for trader: {trader_name}")
        return None

    async def get_competitor_ads(
        self,
        my_trader_name: str,
        min_quantity: float,
        payment_method: str = "Instapay",
        crypto: str = "USDT",
        fiat: str = "EGP",
        trade_type: str = "sell"
    ) -> List[P2PAdvertisement]:
        """
        Get competitor ads that meet criteria:
        - Same payment method
        - Minimum quantity >= threshold
        - Not our own ad

        Args:
            my_trader_name: Your trader name to exclude
            min_quantity: Minimum max_quantity filter
            payment_method: Payment method to filter
            crypto: Cryptocurrency
            fiat: Fiat currency
            trade_type: Trade type

        Returns:
            List of competitor advertisements
        """
        all_ads = await self.fetch_ads(crypto, fiat, trade_type, payment_method)

        competitors = []
        for ad in all_ads:
            # Skip our own ad
            if ad.trader_name.lower().strip() == my_trader_name.lower().strip():
                continue

            # Check payment method (case-insensitive)
            has_payment = any(
                payment_method.lower() in p.lower() 
                for p in ad.payment_methods
            ) if ad.payment_methods else False

            if not has_payment:
                continue

            # Check minimum quantity
            if ad.max_amount < min_quantity:
                continue

            competitors.append(ad)

        logger.info(f"Found {len(competitors)} competitor ads meeting criteria")
        return competitors

# Global scraper instance
scraper = GateioScraper()
