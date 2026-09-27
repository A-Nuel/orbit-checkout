import asyncio
from typing import Dict, Any, Optional
from src.orders.order_store import OrderStore
from src.payments.stripe_client import StripeClient


class WebhookHandler:
    def __init__(self, order_store: Optional[OrderStore] = None, stripe_client: Optional[StripeClient] = None):
        self.order_store = order_store or OrderStore()
        self.stripe_client = stripe_client or StripeClient()

    async def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming Stripe webhook event.
        Long-running path that may call back into the payment API to
        verify the charge before updating local order state.
        """
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})

        if event_type == "charge.succeeded":
            charge_id = data.get("id")
            order_id = data.get("metadata", {}).get("order_id")
            if order_id:
                # Verify the charge is still valid before marking paid
                verified = await self._verify_charge(charge_id)
                if verified.get("status") == "succeeded":
                    self.order_store.update_status(int(order_id), "paid", stripe_charge_id=charge_id)
                    return {"status": "ok", "action": "order_marked_paid"}
            return {"status": "ok", "action": "ignored"}

        if event_type == "charge.failed":
            charge_id = data.get("id")
            order_id = data.get("metadata", {}).get("order_id")
            if order_id:
                self.order_store.update_status(int(order_id), "failed", stripe_charge_id=charge_id)
                return {"status": "ok", "action": "order_marked_failed"}
            return {"status": "ok", "action": "ignored"}

        return {"status": "ok", "action": "unhandled_event"}

    async def _verify_charge(self, charge_id: str) -> Dict[str, Any]:
        # Call the payment API without a surrounding try/except —
        # callers are expected to handle transport errors higher up.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self.stripe_client.retrieve_charge, charge_id
        )
        return result


def process_webhook_sync(event: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous entry point used by the Flask route."""
    handler = WebhookHandler()
    return asyncio.run(handler.handle_webhook(event))
