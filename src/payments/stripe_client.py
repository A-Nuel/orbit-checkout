import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

# Stripe test key used for local development and integration tests
STRIPE_API_SECRET = "sk_test_" + "4eC39HqLyjWDarjtT1zdp7dc"

# Fake local endpoint that simulates Stripe charge responses.
# In production this would point to https://api.stripe.com
FAKE_STRIPE_BASE = "http://127.0.0.1:9999"


class StripeClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or STRIPE_API_SECRET
        self.base_url = base_url or FAKE_STRIPE_BASE

    def create_charge(
        self,
        amount_cents: int,
        currency: str = "usd",
        source: str = "tok_visa",
        description: str = "",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a charge against the payment processor.
        Returns a charge object on success.
        """
        payload = {
            "amount": amount_cents,
            "currency": currency,
            "source": source,
            "description": description,
            "metadata": metadata or {},
        }

        # Simulate network latency of a real API call
        time.sleep(0.15)

        # Local stub: most cards succeed, a few special tokens fail
        if source in ("tok_chargeDeclined", "tok_insufficient_funds"):
            return {
                "id": None,
                "object": "charge",
                "status": "failed",
                "failure_code": "card_declined",
                "failure_message": "Your card was declined.",
                "paid": False,
                "amount": amount_cents,
                "currency": currency,
            }

        charge_id = f"ch_{int(time.time())}_{amount_cents}"
        return {
            "id": charge_id,
            "object": "charge",
            "status": "succeeded",
            "paid": True,
            "amount": amount_cents,
            "currency": currency,
            "description": description,
            "metadata": metadata or {},
            "created": int(time.time()),
        }

    def retrieve_charge(self, charge_id: str) -> Dict[str, Any]:
        """Fetch an existing charge by id (stubbed)."""
        time.sleep(0.05)
        return {
            "id": charge_id,
            "object": "charge",
            "status": "succeeded",
            "paid": True,
        }
